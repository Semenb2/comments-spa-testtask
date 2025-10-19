# app/utils/sanitize.py
import re
import bleach

ALLOWED_TAGS = ["a", "code", "i", "strong"]
ALLOWED_ATTRS = {"a": ["href", "title"]}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

# Имя пользователя: латиница и цифры по ТЗ
USERNAME_RE = re.compile(r"^[A-Za-z0-9]{2,32}$")

def sanitize_html(raw: str) -> str:
    return bleach.clean(
        raw or "",
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
