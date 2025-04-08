import re


def clean_text(text: str) -> str:
    text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")
    return re.sub(r"[^\x20-\x7E\n\r\t]", "", text)
