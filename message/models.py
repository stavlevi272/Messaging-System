from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_sender")
    receiver = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_receiver")
    subject = models.CharField(max_length=120)
    content = models.TextField(default="")
    creation_date = models.DateField(auto_now_add=True)
    was_read = models.BooleanField(default=False)
    was_deleted_by_sender = models.BooleanField(default=False)
    was_deleted_by_receiver = models.BooleanField(default=False)

    def get_content(self):
        return self.content

    def was_message_read(self):
        return self.was_read

    def mark_as_read(self):
        self.was_read = True

    def mark_as_unread(self):
        self.was_read = False

    def mark_as_deleted(self, user_id):
        if user_id == self.sender.id:
            self.was_deleted_by_sender = True
        else:
            self.was_deleted_by_receiver = True




