from rest_framework import serializers
from ..models import UserProfile, Comment, Attachment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "username", "email", "homepage"]

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["id", "type", "file", "width", "height", "size_bytes"]

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "text", "parent", "created_at", "replies", "attachments"]

    def get_replies(self, obj):
        children = Comment.objects.filter(parent=obj).order_by("-created_at")
        return CommentSerializer(children, many=True, context=self.context).data
