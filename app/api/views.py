from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser

from ..models import UserProfile, Comment
from .serializers import CommentSerializer
from app.utils.sanitize import sanitize_html, USERNAME_RE
from app.utils.captcha import gen_code, captcha_image
from app.utils.uploads import handle_upload

@api_view(['GET'])
def get_comments(request):
    sort = request.GET.get("sort", "-created_at")
    allowed = {"username": "user__username", "email": "user__email", "created_at": "created_at"}
    order = allowed.get(sort.replace("-", ""), "-created_at")
    if sort.startswith("-"):
        order = f"-{order}"

    qs = Comment.objects.filter(parent=None).select_related("user").order_by(order)
    paginator = PageNumberPagination()
    paginator.page_size = 25
    page = paginator.paginate_queryset(qs, request)
    return paginator.get_paginated_response(CommentSerializer(page, many=True).data)

def create_comment(request):
    username = (request.data.get('username') or "").strip()
    email = (request.data.get('email') or "").strip()
    homepage = (request.data.get('homepage') or "").strip()
    text = (request.data.get('text') or "").strip()
    captcha = (request.data.get('captcha') or "").strip()

    if not username or not email or not text:
        return Response({"error": "Имя, Email и текст обязательны"}, status=400)

    if not USERNAME_RE.match(username):
        return Response({"error": "Некорректный username (A-Za-z0-9)"}, status=400)

    real = request.session.get("captcha_code", "")
    if not real or captcha != real:
        return Response({"error": "Неверная CAPTCHA"}, status=400)

    safe_text = sanitize_html(text)

    user, _ = UserProfile.objects.get_or_create(
        username=username, email=email, defaults={"homepage": homepage}
    )
    comment = Comment.objects.create(user=user, text=safe_text)
    return Response(CommentSerializer(comment).data, status=201)

@api_view(['GET'])
def get_replies(request, comment_id):
    replies = Comment.objects.filter(parent_id=comment_id).select_related("user").order_by("-created_at")
    return Response(CommentSerializer(replies, many=True).data)

@api_view(['POST'])
def reply_comment(request, comment_id):
    username = (request.data.get('username') or "").strip()
    email = (request.data.get('email') or "").strip()
    text = (request.data.get('text') or "").strip()

    if not username or not email or not text:
        return Response({"error": "Имя, Email и текст обязательны"}, status=400)
    if not USERNAME_RE.match(username):
        return Response({"error": "Некорректный username (A-Za-z0-9)"}, status=400)

    parent = Comment.objects.get(id=comment_id)
    safe_text = sanitize_html(text)
    user, _ = UserProfile.objects.get_or_create(username=username, email=email)
    reply = Comment.objects.create(user=user, parent=parent, text=safe_text)
    return Response(CommentSerializer(reply).data, status=201)

@api_view(['GET'])
def get_captcha(request):
    code = gen_code()
    request.session["captcha_code"] = code
    return captcha_image(code)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_attachment(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Комментарий не найден"}, status=404)

    f = request.FILES.get("file")
    if not f:
        return Response({"error": "Файл обязателен"}, status=400)

    try:
        att = handle_upload(comment, f)
        return Response({
            "id": att.id,
            "type": att.type,
            "url": att.file.url,
            "size": att.size_bytes,
            "width": getattr(att, "width", None),
            "height": getattr(att, "height", None),
        }, status=201)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
