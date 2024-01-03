#!/usr/bin/env python3
"""_summary_
    py
"""
import os
import random
import struct
import sys
import textwrap
import threading
import time
from threading import Thread
import openai
import pvcobra
import pvporcupine
import pyaudio
import pvleopard
from colorama import Fore
from openai import OpenAI
from pvrecorder import PvRecorder
from dotenv import load_dotenv
from pvleopard import *
import audio
import voice

load_dotenv()

RECORDER = None

GPT_MODEL = "gpt-4"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PICOVOICE_API_KEY= os.getenv('PICOVOICE_API_KEY')

client = OpenAI(
  api_key=OPENAI_API_KEY
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

chat_log=[
    {
        "role": 
            "system", 
            "content": 
                "Your name is DaVinci. You are a helpful assistant. If asked about yourself, you include your name in your response."
    },
]

py_audio = pyaudio.PyAudio()
selected_device = int(os.getenv('AUDIO_INPUT_DEVICE_ID'))
if (selected_device == -1):
    audio.list_audio_devices(py_audio)
    selected_device = int(input("Enter the ID of the audio input device you want to use: "))
    print("You selected device with ID: ", selected_device)

def ChatGPT(query):
    user_query = [
        {"role": "user", "content": query},
    ]
    send_query = (chat_log + user_query)
    response = client.chat.completions.create(
    model=GPT_MODEL,
    messages=send_query
    )
    answer = response.choices[0].message.content
    chat_log.append({"role": "assistant", "content": answer})
    return answer
    

def responseprinter(chat):
    wrapper = textwrap.TextWrapper(width=70)  # Adjust the width to your preference
    paragraphs = res.split('\n')
    wrapped_chat = "\n".join([wrapper.fill(p) for p in paragraphs])
    for word in wrapped_chat:
        time.sleep(0.06)
        print(word, end="", flush=True)
    print()

#DaVinci will 'remember' earlier queries so that it has greater continuity in its response
#the following will delete that 'memory' five minutes after the start of the conversation
def append_clear_countdown():
    time.sleep(300)
    global chat_log
    chat_log.clear()
    chat_log=[
        {
            "role": 
                "system", 
                "content": 
                    "Your name is DaVinci. You are a helpful assistant. If asked about yourself, you include your name in your response."
        }
    ]
    global count
    count = 0
    t_count.join

def wake_word():
    keywords = ["computer", "jarvis", "americano"]
    porcupine = pvporcupine.create(
        keywords=keywords,
        access_key=PICOVOICE_API_KEY,
        sensitivities=[1, 1, 1],
    )
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)

    porcupine_audio_stream = py_audio.open(
        rate=porcupine.sample_rate,
        input_device_index=selected_device,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    
    Detect = True

    while Detect:
        porcupine_pcm = porcupine_audio_stream.read(porcupine.frame_length)
        porcupine_pcm = struct.unpack_from("h" * porcupine.frame_length, porcupine_pcm)

        porcupine_keyword_index = porcupine.process(porcupine_pcm)

        if porcupine_keyword_index >= 0:

            keyword = keywords[porcupine_keyword_index]
            print(Fore.GREEN + "\n" + keyword + " detected\n")
            porcupine_audio_stream.stop_stream()
            porcupine_audio_stream.close()
            porcupine.delete()         
            os.dup2(old_stderr, 2)
            os.close(old_stderr)
            Detect = False

def listen():
    cobra = pvcobra.create(access_key=PICOVOICE_API_KEY)

    listen_audio_stream = py_audio.open(
        rate=cobra.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=cobra.frame_length
    )

    print("Listening...")

    while True:
        listen_pcm = listen_audio_stream.read(cobra.frame_length)
        listen_pcm = struct.unpack_from("h" * cobra.frame_length, listen_pcm)
           
        if cobra.process(listen_pcm) > 0.3:
            print("Voice detected")
            listen_audio_stream.stop_stream()
            listen_audio_stream.close()
            cobra.delete()
            break

def detect_silence():
    cobra = pvcobra.create(access_key=PICOVOICE_API_KEY)

    cobra_audio_stream = py_audio.open(
        rate=cobra.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=cobra.frame_length
    )

    last_voice_time = time.time()

    while True:
        cobra_pcm = cobra_audio_stream.read(cobra.frame_length)
        cobra_pcm = struct.unpack_from("h" * cobra.frame_length, cobra_pcm)
           
        if cobra.process(cobra_pcm) > 0.2:
            last_voice_time = time.time()
        else:
            silence_duration = time.time() - last_voice_time
            if silence_duration > 1.3:
                print("End of query detected\n")
                cobra_audio_stream.stop_stream()
                cobra_audio_stream.close()
                cobra.delete()
                last_voice_time=None
                break

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
    pv_leopard = pvleopard.create(
        access_key=PICOVOICE_API_KEY,
        enable_automatic_punctuation = True,
    )

    event = threading.Event()
    count = 0

    while True:
        try:
            if count == 0:
                t_count = threading.Thread(target=append_clear_countdown)
                t_count.start()
            else:
                pass
            count += 1
            wake_word()
            voice.voice(random.choice(prompt))
            RECORDER = Recorder()
            RECORDER.start()
            listen()
            detect_silence()
            transcript, words = pv_leopard.process(RECORDER.stop())
            RECORDER.stop()
            print(transcript)
            res = ChatGPT(transcript)
            print("\nChatGPT's response is:\n")
            t1 = threading.Thread(target=voice.voice, args=(res,))
            t2 = threading.Thread(target=responseprinter, args=(res,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            event.set()
            RECORDER.stop()
            pv_leopard.delete()
            RECORDER = None

        except openai.RateLimitError as e:
            print("\nYou have hit your assigned rate limit.")
            voice.voice("\nYou have hit your assigned rate limit.")
            event.set()
            RECORDER.stop()
            pv_leopard.delete()
            RECORDER = None
            break

        except openai.APIConnectionError as e:
            print("\nI am having trouble connecting to the API.  Please check your network connection and then try again.")
            voice.voice("\nI am having trouble connecting to the A P I.  Please check your network connection and try again.")
            event.set()
            RECORDER.stop()
            pv_leopard.delete()
            RECORDER = None
            time.sleep(1)

        except openai.AuthenticationError as e:
            print("\nYour OpenAI API key or token is invalid, expired, or revoked.  Please fix this issue and then restart my program.")
            voice.voice("\nYour Open A I A P I key or token is invalid, expired, or revoked.  Please fix this issue and then restart my program.")
            event.set()
            RECORDER.stop()
            pv_leopard.delete()
            RECORDER = None
            break

        except openai.APIError as e:
            print("\nThere was an API error.  Please try again in a few minutes.")
            voice.voice("\nThere was an A P I error.  Please try again in a few minutes.")
            print(e)
            event.set()
            RECORDER.stop()
            pv_leopard.delete()
            RECORDER = None
            time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting ChatGPT Virtual Assistant")
    pv_leopard.delete()
