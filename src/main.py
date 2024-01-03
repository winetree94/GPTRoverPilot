#!/usr/bin/env python3
"""_summary_
    py
"""
import os
import random
import threading
import time
from threading import Thread
import openai
import pvleopard
from pvrecorder import PvRecorder
from dotenv import load_dotenv
from pvleopard import *
from typing import Final
from audio import PilotAudio
import voice
import gpt as ChatGPT
import printer

devices = PvRecorder.get_available_devices()
print(devices)

load_dotenv()

GPT_MODEL: Final = str(os.getenv('OPENAI_GPT_MODEL', 'gpt-4'))
OPENAI_API_KEY: Final = str(os.getenv('OPENAI_API_KEY'))
PICOVOICE_API_KEY: Final = str(os.getenv('PICOVOICE_API_KEY'))
selected_device = int(os.getenv('AUDIO_INPUT_DEVICE_ID'))

pilot_audio = PilotAudio(
    picovoice_api_key=PICOVOICE_API_KEY
)

if selected_device == -1:
    pilot_audio.list_audio_devices()
    selected_device = int(input("Enter the ID of the audio input device you want to use: "))
    print("You selected device with ID: ", selected_device)

gpt = ChatGPT.ChatGPT(
    key=OPENAI_API_KEY,
    default_model=GPT_MODEL,
)

prompt = [
    "How may I assist you?",
    "How may I help?",
    "What can I do for you?",
    "Ask me anything.",
    "Yes?",
    "I'm here.",
    "I'm listening.",
    "What would you like me to do?"
]

#DaVinci will 'remember' earlier queries so that it has greater continuity in its response
#the following will delete that 'memory' five minutes after the start of the conversation
def append_clear_countdown():
    time.sleep(300)
    gpt.clear()
    global count
    count = 0

class Recorder(Thread):
    def __init__(self):
        super().__init__()
        self._pcm = list()
        self._is_recording = False
        self._stop = False

    def is_recording(self):
        return self._is_recording

    def run(self):
        self._is_recording = True

        recorder = PvRecorder(device_index=3, frame_length=512)
        recorder.start()

        while not self._stop:
            self._pcm.extend(recorder.read())
        recorder.stop()

        self._is_recording = False

    def stop(self):
        self._stop = True
        while self._is_recording:
            pass

        return self._pcm

try:
    pv_leopard = pvleopard.create(
        access_key=PICOVOICE_API_KEY,
        enable_automatic_punctuation = True,
    )

    event = threading.Event()
    count = 0
    voice.voice("Jarvis is online")
    print('pilot is ready')

    while True:
        try:
            if count == 0:
                t_count = threading.Thread(target = append_clear_countdown)
                t_count.start()
            else:
                pass

            count += 1
            pilot_audio.wait_until_wake_word(selected_device)
            voice.voice(random.choice(prompt))
            recorder = Recorder()
            recorder.start()
            pilot_audio.listen_until_silence()
            pilot_audio.wait_until_silence()
            recorded = recorder.stop()
            print(recorded)
            transcript, words = pv_leopard.process(recorded)
            recorder.stop()
            print(transcript)
            res = gpt.chat(transcript)
            print("\nChatGPT's response is:\n")
            t1 = threading.Thread(target = voice.voice, args=(res,))
            t2 = threading.Thread(target = printer.print_slowly, args=(res,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            event.set()
            recorder.stop()
            pv_leopard.delete()
            recorder = None

        except openai.RateLimitError as e:
            print("\nYou have hit your assigned rate limit.")
            voice.voice("\nYou have hit your assigned rate limit.")
            event.set()
            recorder.stop()
            pv_leopard.delete()
            recorder = None
            break

        except openai.APIConnectionError as e:
            print("\nI am having trouble connecting to the API.  Please check your network connection and then try again.")
            voice.voice("\nI am having trouble connecting to the A P I.  Please check your network connection and try again.")
            event.set()
            recorder.stop()
            pv_leopard.delete()
            recorder = None
            time.sleep(1)

        except openai.AuthenticationError as e:
            print("\nYour OpenAI API key or token is invalid, expired, or revoked.  Please fix this issue and then restart my program.")
            voice.voice("\nYour Open A I A P I key or token is invalid, expired, or revoked.  Please fix this issue and then restart my program.")
            event.set()
            recorder.stop()
            pv_leopard.delete()
            recorder = None
            break

        except openai.APIError as e:
            print("\nThere was an API error.  Please try again in a few minutes.")
            voice.voice("\nThere was an A P I error.  Please try again in a few minutes.")
            print(e)
            event.set()
            recorder.stop()
            pv_leopard.delete()
            recorder = None
            time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting ChatGPT Virtual Assistant")
    pv_leopard.delete()
