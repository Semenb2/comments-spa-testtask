from django.urls import path
from .api.views import (
    get_comments, create_comment, get_replies, reply_comment,
    get_captcha, upload_attachment
)

urlpatterns = [
    path('comments/', get_comments),
    path('comments/create/', create_comment),
    path('comments/<int:comment_id>/replies/', get_replies),
    path('comments/<int:comment_id>/reply/', reply_comment),
    path('comments/<int:comment_id>/attachments/', upload_attachment),
    path('captcha/', get_captcha),
]
