#!/usr/bin/env python3
# pylint: disable=C0413
"""_summary_
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import time
import pygame
import boto3

polly = boto3.client('polly', region_name='us-west-2')

def voice(
    chat: str,
):
    """_summary_
        대화 내용을 음성으로 출력합니다.

    Args:
        chat (_type_): _description_
    """
    voice_res = polly.synthesize_speech(
        Text=chat,
        OutputFormat="mp3",
        VoiceId="Matthew"
    )

    if "AudioStream" in voice_res:
        with voice_res["AudioStream"] as stream:
            output_file = "speech.mp3"
            try:
                with open(output_file, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                print(error)

    else:
        print("did not work")

    pygame.mixer.init()
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass
    pygame.mixer.music.unload()
    time.sleep(0.2)