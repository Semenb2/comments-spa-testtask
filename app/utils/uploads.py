# app/utils/uploads.py
import io, imghdr
from PIL import Image
from django.core.files.base import ContentFile
from app.models import Attachment, Comment

MAX_W, MAX_H = 320, 240
MAX_TXT = 100 * 1024  

def handle_upload(comment: Comment, upfile):
    name = (upfile.name or "").lower()
    data = upfile.read()

    kind = imghdr.what(None, h=data)
    is_img_ext = name.endswith((".jpg", ".jpeg", ".png", ".gif"))
    is_img_sig = kind in ("jpeg", "png", "gif")

    if is_img_ext or is_img_sig:
        img = Image.open(io.BytesIO(data))
        img.thumbnail((MAX_W, MAX_H))
        out = io.BytesIO()
        fmt = "PNG" if kind == "png" else ("GIF" if kind == "gif" else "JPEG")
        img.save(out, format=fmt)
        content = ContentFile(out.getvalue())

        att = Attachment.objects.create(
            comment=comment,
            type=Attachment.IMAGE,
            size_bytes=content.size,
            width=img.width,
            height=img.height,
        )
        att.file.save(name or f"image.{fmt.lower()}", content, save=True)
        return att


    if name.endswith(".txt"):
        if len(data) > MAX_TXT:
            raise ValueError("TXT > 100KB")
        content = ContentFile(data)
        att = Attachment.objects.create(
            comment=comment, type=Attachment.TEXT, size_bytes=len(data)
        )
        att.file.save(name or "file.txt", content, save=True)
        return att

    raise ValueError("Unsupported file type")
