from googletrans import Translator

translator = Translator()


def translate_ko_to_es(text: str) -> str:
    """
    한글KO > 스페인어ES 번역
    """
    try:
        result = translator.translate(text, src="ko", dest="es")
        return str(result.text)
    except Exception as e:
        print(e)  # 실패케이스 임시처리
        return text


def translate_es_to_ko(text: str) -> str:
    """
    스페인어ES > 한글KO 번역
    """
    try:
        result = translator.translate(text, src="es", dest="ko")
        return str(result.text)
    except Exception as e:
        print(e)  # 실패케이스 임시처리
        return text
