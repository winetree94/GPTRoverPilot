#!/usr/bin/env python3
"""_summary_
    py
"""
import os
import random
import wave
import struct
import threading
import time
from threading import Thread
from typing import Final
import openai
from pvrecorder import PvRecorder
from dotenv import load_dotenv
from audio import PilotAudio
import voice
import gpt as ChatGPT
import printer
from tts import PilotTTS

devices = PvRecorder.get_available_devices()
print(devices)

load_dotenv()

GPT_MODEL: Final = str(os.getenv('OPENAI_GPT_MODEL', 'gpt-4'))
OPENAI_API_KEY: Final = str(os.getenv('OPENAI_API_KEY'))
PICOVOICE_API_KEY: Final = str(os.getenv('PICOVOICE_API_KEY'))

selected_device = int(os.getenv('AUDIO_INPUT_DEVICE_ID'))

pilot_tts = PilotTTS(
    picovoice_api_key=PICOVOICE_API_KEY
)

pilot_audio = PilotAudio(
    picovoice_api_key=PICOVOICE_API_KEY
)

pilot_gpt = ChatGPT.ChatGPT(
    key=OPENAI_API_KEY,
    default_model=GPT_MODEL,
)

if selected_device == -1:
    pilot_audio.list_audio_devices()
    selected_device = int(input("Enter the ID of the audio input device you want to use: "))
    print("You selected device with ID: ", selected_device)

prompt = [
    "무엇을 도와드릴까요?",
    # "How may I help?",
    # "What can I do for you?",
    # "Ask me anything.",
    # "Yes?",
    # "I'm here.",
    # "I'm listening.",
    # "What would you like me to do?"
]

def append_clear_countdown():
    time.sleep(300)
    pilot_gpt.clear()
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

        recorder = PvRecorder(device_index=-1, frame_length=512)
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
    event = threading.Event()
    count = 0
    print('안녕하세요 서연입니다.')
    voice.voice("안녕하세요 서연입니다.")

    while True:
        try:
            if count == 0:
                t_count = threading.Thread(target = append_clear_countdown)
                t_count.start()
            else:
                pass

            count += 1
            # pilot_audio.listen_for_wake_word2(
            #     pilot_tts.speech_recognition
            # )
            pilot_audio.wait_until_wake_word(selected_device)
            # pilot_audio.listen_for_wake_word2(pilot_tts.speech_recognition, speech_recognition.Microphone())
            voice.voice(random.choice(prompt))
            recorder = Recorder()
            recorder.start()
            pilot_audio.listen_until_silence()
            pilot_audio.wait_until_silence()
            recorded = recorder.stop()
            out = wave.open('recorded.wav', 'w')
            out.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            out.writeframes(struct.pack("h" * len(recorded), *recorded))
            transcript = pilot_tts.speech_to_text('recorded.wav')
            # transcript, words = pilot_tts.speech_to_text_legacy(recorded)
            print(transcript)
            res = pilot_gpt.chat(transcript)
            print("\nChatGPT's response is:\n")
            t1 = threading.Thread(target = voice.voice, args=(res,))
            t2 = threading.Thread(target = printer.print_slowly, args=(res,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            event.set()
            recorder.stop()
            recorder = None

        except openai.RateLimitError as e:
            print("\nYou have hit your assigned rate limit.")
            voice.voice("\nYou have hit your assigned rate limit.")
            event.set()
            recorder.stop()
            recorder = None
            break

        except openai.APIConnectionError as e:
            print("\nI am having trouble connecting to the API.  Please check your network connection and then try again.")
            voice.voice("\nI am having trouble connecting to the A P I.  Please check your network connection and try again.")
            event.set()
            recorder.stop()
            recorder = None
            time.sleep(1)

        except openai.AuthenticationError as e:
            print("\nYour OpenAI API key or token is invalid, expired, or revoked.  Please fix this issue and then restart my program.")
            voice.voice("\nYour Open A I A P I key or token is invalid, expired, or revoked.  Please fix this issue and then restart my program.")
            event.set()
            recorder.stop()
            recorder = None
            break

        except openai.APIError as e:
            print("\nThere was an API error.  Please try again in a few minutes.")
            voice.voice("\nThere was an A P I error.  Please try again in a few minutes.")
            print(e)
            event.set()
            recorder.stop()
            recorder = None
            time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting ChatGPT Virtual Assistant")
    pilot_tts.delete()
