"""_summary_
    음성을 텍스트로 변환하거나, 텍스트를 음성으로 변환하기 위한 모듈
"""
import pvleopard

class PilotTTS:
    """_summary_
        Picovoice Leopard 를 쉽게 사용하기 위한 추상화 클래스입니다.
    """

    def __init__(self, picovoice_api_key: str):
        self.pv_leopard = pvleopard.create(
            access_key=picovoice_api_key,
            enable_automatic_punctuation = True,
        )

    def speech_to_text(self, pcm: list):
        """_summary_
            음성을 텍스트로 변환합니다.

        Args:
            pcm (list): _description_

        Returns:
            _type_: _description_
        """
        return self.pv_leopard.process(pcm)

    def delete(self):
        """_summary_
            Picovoice Leopard 를 종료합니다.
        """
        self.pv_leopard.delete()
