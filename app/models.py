from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField()
    homepage = models.URLField(blank=True, null=True)

class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Attachment(models.Model):
    IMAGE = "image"
    TEXT = "text"
    TYPES = [(IMAGE, "image"), (TEXT, "text")]

    comment = models.ForeignKey("Comment", on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="uploads/")
    type = models.CharField(max_length=10, choices=TYPES)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    size_bytes = models.IntegerField()

    def __str__(self):
        return f"{self.type}:{self.file.name}"