from django.db import models
from django.contrib.auth.models import User

class Learn_Session(models.Model):
    session_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Learn Sessions"
    
    def __str__(self):
        return f"{self.user_id}: Session {self.session_id}"
    
class Learn_Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    session_id = models.ForeignKey(Learn_Session, on_delete=models.DO_NOTHING)
    message = models.TextField()
    edited_message = models.TextField(blank=True)
    response = models.TextField()
    user_feedback = models.BooleanField(blank=True, default=False)
    written_feedback = models.TextField(blank=True)
    approved = models.BooleanField(blank=True, default=False)
    date = models.DateTimeField(auto_now_add=True)    
    
    class Meta:
        verbose_name_plural = "Learn Messages"
    
    # See return value in Admin panel
    def __str__(self):
        return f"{self.session_id} - Message{self.message_id}"