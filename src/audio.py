"""_summary_

Returns:
    _type_: _description_
"""
import os
import sys
import time
import struct
import pyaudio
from colorama import Fore
import pvporcupine
import pvcobra

class PilotAudio:
    """_summary_
        pyaudio 와 picovoice 를 사용하여 오디오 입력을 처리합니다.
    """
    pyaudio = pyaudio.PyAudio()

    def __init__(self, picovoice_api_key: str):
        self.picovoice_api_key = picovoice_api_key
        self.selected_device = None

    def list_audio_devices(self):
        """_summary_
        사용자가 가지고 있는 오디오 Input 장치의 목록과 ID를 출력합니다.

        Args:
            pyaudio (_type_): _description_
        """
        numdevices = self.pyaudio.get_device_count()
        for i in range(0, numdevices):
            device = self.pyaudio.get_device_info_by_index(i)
            if (device.get('maxInputChannels')) > 0:
                print(
                    "Input Device id ",
                    i,
                    " - ",
                    device.get('name')
                )

    def select_audio_device(self):
        """_summary_
        사용자가 가지고 있는 오디오 Input 장치 중 사용할 장치의 ID를 입력받습니다.

        Returns:
            _type_: _description_
        """
        device_id = input("Enter the ID of the audio input device you want to use: ")
        return int(device_id)

    def wait_until_wake_word(self, device_index: int):
        """_summary_
            wake word 가 감지될 때까지 대기합니다.
        """
        keywords = ["computer", "jarvis", "americano"]
        porcupine = pvporcupine.create(
            keywords = keywords,
            access_key = self.picovoice_api_key,
            sensitivities = [1, 1, 1],
        )
        devnull = os.open(os.devnull, os.O_WRONLY)
        old_stderr = os.dup(2)
        sys.stderr.flush()
        os.dup2(devnull, 2)
        os.close(devnull)

        porcupine_audio_stream = self.pyaudio.open(
            rate = porcupine.sample_rate,
            input_device_index = device_index,
            channels = 1,
            format = pyaudio.paInt16,
            input = True,
            frames_per_buffer = porcupine.frame_length
        )

        detected = True

        while detected:
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
                detected = False

    def wait_until_silence(self):
        """_summary_
            조용함이 감지될 때까지 대기합니다.
        """
        cobra = pvcobra.create(access_key=self.picovoice_api_key)

        cobra_audio_stream = self.pyaudio.open(
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

    def listen_until_silence(self):
        """_summary_
            사용자의 음성을 입력받습니다.
            조용함이 감지되면 종료됩니다.
        """
        cobra = pvcobra.create(access_key = self.picovoice_api_key)

        listen_audio_stream = self.pyaudio.open(
            rate = cobra.sample_rate,
            channels = 1,
            format = pyaudio.paInt16,
            input = True,
            frames_per_buffer = cobra.frame_length
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
