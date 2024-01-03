"""_summary_
오디오 장치를 제어하기 위한 도구들을 포함합니다.

Returns:
    _type_: _description_
"""
import pyaudio

def list_audio_devices():
    """_summary_
    사용자가 가지고 있는 오디오 Input 장치의 목록과 ID를 출력합니다.
    """
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print(
                "Input Device id ",
                i,
                " - ",
                p.get_device_info_by_host_api_device_index(0, i).get('name')
            )

def select_audio_device():
    """_summary_
    사용자가 가지고 있는 오디오 Input 장치 중 사용할 장치의 ID를 입력받습니다.

    Returns:
        _type_: _description_
    """
    device_id = input("Enter the ID of the audio input device you want to use: ")
    return int(device_id)
