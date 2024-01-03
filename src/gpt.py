"""_summary_
오디오 장치를 제어하기 위한 도구들을 포함합니다.

Returns:
    _type_: _description_
"""
import openai

class ChatGPT:
    """_summary_
        ChatGPT 를 쉽게 사용하기 위한 OpenAPI 의 추상화 클래스입니다.
    """

    def __init__(
        self,
        key: str,
        default_model: str
    ):
        self.key = key
        self.default_model = default_model
        self.client = openai.OpenAI(api_key=key)
        self.clear()

    def chat(
        self,
        query: str,
    ):
        """_summary_
            ChatGPT 로 대화 내용을 전송합니다.

        Args:
            model (_type_): _description_
            query (_type_): _description_

        Returns:
            _type_: _description_
        """
        user_query: list[dict[str, str]] = [
            {"role": "user", "content": query},
        ]
        send_query = self.chat_log + user_query
        response = self.client.chat.completions.create(
            model = self.default_model,
            messages = send_query
        )
        answer = response.choices[0].message.content

        self.chat_log.append({"role": "assistant", "content": answer})
        return answer

    def clear(self):
        """_summary_
            ChatGPT 의 대화 내용을 초기화합니다.
        """
        self.chat_log = [
            {
                "role": 
                    "system", 
                    "content": 
                        "Your name is DaVinci. You are a helpful assistant."
                        "If asked about yourself, you include your name in your response."
            }
        ]
