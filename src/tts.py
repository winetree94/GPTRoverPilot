"""_summary_
    TTS 관련 유틸 모음
"""
# pylint: disable=C0413
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import io
import gtts
import pygame

def parse(text: str, language: str) -> io.BytesIO:
    """
    텍스트를 Google TTS 를 사용하여 음성으로 전환하고 재생합니다.
    Args:
        text (str): 음성으로 변환할 텍스트
    """
    tts = gtts.gTTS(text, lang=language)

    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

def play(b: io.BytesIO):
    """ Byte IO 로부터 음성을 재생합니다.

    Args:
        b (io.BytesIO): 음성 파일
    """
    pygame.mixer.init()
    pygame.mixer.music.load(b)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def parse_and_play(text: str, language: str) -> None:
    """
    텍스트를 Google TTS 를 사용하여 음성으로 전환하고 재생합니다.
    Args:
        text (str): 음성으로 변환할 텍스트
    """
    tts = gtts.gTTS(text, lang=language)

    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
