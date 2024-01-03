#!/usr/bin/env python3
"""_summary_
    콘솔에 출력하기 위한 도구
"""
import textwrap
import time

def print_slowly(res: str):
    """_summary_
    
    콘솔에 텍스트를 천천히 출력합니다.

    Args:
        res (str): _description_
    """
    wrapper = textwrap.TextWrapper(width=70)  # Adjust the width to your preference
    paragraphs = res.split('\n')
    wrapped_chat = "\n".join([wrapper.fill(p) for p in paragraphs])
    for word in wrapped_chat:
        time.sleep(0.06)
        print(word, end="", flush=True)
    print()