"""_summary_
    음성을 텍스트로 변환하거나, 텍스트를 음성으로 변환하기 위한 모듈
"""
import pvleopard
import speech_recognition

class PilotTTS:
    """_summary_
        Picovoice Leopard 를 쉽게 사용하기 위한 추상화 클래스입니다.
    """

    def __init__(self, picovoice_api_key: str):
        self.pv_leopard = pvleopard.create(
            access_key=picovoice_api_key,
            enable_automatic_punctuation = True,
        )
        self.speech_recognition = speech_recognition.Recognizer()

    def speech_to_text_legacy(self, pcm: list):
        """_summary_
            음성을 텍스트로 변환합니다.

        Args:
            pcm (list): _description_

        Returns:
            _type_: _description_
        """
        return self.pv_leopard.process(pcm)

    def speech_to_text(self, file_name: str):
        """_summary_
            음성을 텍스트로 변환합니다.

        Args:
            pcm (list): _description_

        Returns:
            _type_: _description_
        """

        with speech_recognition.AudioFile(file_name) as source:
            return self.speech_recognition.recognize_google(
                self.speech_recognition.record(source),
                language='ko-KR',
            )

    def delete(self):
        """_summary_
            Picovoice Leopard 를 종료합니다.
        """
        self.pv_leopard.delete()
