import re

def clean_text(text: str) -> str:
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'Page\s+\d+', '', text)
    return text.strip()
