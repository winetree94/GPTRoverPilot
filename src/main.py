#!/usr/bin/env python3
"""
    ChatGPT Voice Assistant
"""
import json
from typing import Final, List
from threading import Thread
import pyaudio
import speech_recognition
import numpy
import audio
import gpt
import tts
import utils

with open('configuration.json', 'r', encoding='utf-8') as file:
    env = json.load(file)

OPENAI_API_KEY: Final[str] = str(env.get('openai_api_key'))
OPENAI_GPT_MODEL: Final[str] = str(env.get('openai_gpt_model', 'gpt-4'))
OPENAI_GPT_PREFIX: Final[str] = str(env.get('openai_gpt_prefix', ''))
LANGUAGE_CODE: Final[str] = str(env.get('language_code', 'en'))
COUNTRY_CODE: Final[str] = str(env.get('country_code', 'US'))
WAKE_WORDS: Final[List[str]] = env.get('wake_words', ['Jarvis'])
GREETING_MESSAGES: Final[List[str]] = env.get('greeting_messages', ['Hello'])

pilot_gpt = gpt.ChatGPT(
    key = OPENAI_API_KEY,
    default_model = OPENAI_GPT_MODEL,
    prefix = OPENAI_GPT_PREFIX,
)
pyaudio = pyaudio.PyAudio()
recognizer = speech_recognition.Recognizer()

audio_input_device_id = int(env.get('audio_input_device_id'))
if audio_input_device_id == -1:
    audio.list_audio_input_devices(pyaudio)
    audio_input_device_id = int(input("Enter the ID of the audio input device you want to use: "))

# audio_output_device_id = int(env.get('audio_output_device_id'))
# if audio_output_device_id == -1:
#     audio.list_audio_output_devices(pyaudio)
#     audio_output_device_id = int(input("Enter the ID of the audio output device you want to use: "))

def listen_wake_word():
    """
        음성을 녹음하고 Wake Word 가 감지될 때까지 대기합니다.
    """
    audio.listen_for_wake_word(
        recognizer=recognizer,
        audio_source=source,
        wake_words=WAKE_WORDS,
        language=LANGUAGE_CODE + '-' + COUNTRY_CODE
    )
    tts.play(numpy.random.choice(GREETING_MESSAGES), LANGUAGE_CODE)
    listen_and_response()

def listen_and_response():
    """
        음성을 녹음하고 텍스트로 변환하여 ChatGPT 로 전송합니다.
        수신받은 응답은 다시 음성으로 변환하여 출력합니다.
    """
    question = audio.listen_voice_and_return_text(
        recognizer=recognizer,
        audio_source=source,
        language=LANGUAGE_CODE + '-' + COUNTRY_CODE
    )
    print("You said: ", question)
    response = pilot_gpt.chat(question)
    print_thread = Thread(target = utils.print_slowly, args=(response,))
    print_thread.start()
    tts.play(response, LANGUAGE_CODE)
    print_thread.join()
    listen_wake_word()

with speech_recognition.Microphone(
    device_index = None if audio_input_device_id == -2 else audio_input_device_id,
) as source:
    tts.play(numpy.random.choice(GREETING_MESSAGES), LANGUAGE_CODE)
    print("ChatGPT Assistant is ready")
    listen_wake_word()
