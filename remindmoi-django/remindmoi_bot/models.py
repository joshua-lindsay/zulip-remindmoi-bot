from django.db import models


class Reminder(models.Model):
    reminder_id = models.AutoField(primary_key=True)

    zulip_user_email = models.CharField(max_length=128)
    title = models.CharField(max_length=300)
    created = models.DateTimeField()
    deadline = models.DateTimeField()
    active = models.BooleanField(default=True)
    stream = models.CharField(max_length=60, default="")
    topic = models.CharField(max_length=60, default="")
