from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique = True, blank = True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_rooms")
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug =  slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"