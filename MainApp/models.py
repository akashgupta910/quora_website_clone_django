from django.db import models
from django.utils import timezone

class Users (models.Model):
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    verify = models.CharField(max_length=100)
    user_img = models.ImageField(default='user_profile/user_default.png', upload_to="user_profile")
    location = models.CharField(default=' ',max_length=100)
    date_posted = models.DateTimeField(default=timezone.now)
    description = models.TextField(max_length=400)
    show_email = models.BooleanField(default=True)
    change_pass_str = models.CharField(default= '', max_length=100)

    def __str__(self):
        return self.username


class Question (models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(max_length=1000)
    category = models.CharField(max_length=200)
    tags = models.CharField(max_length=200)
    views = models.IntegerField(default=0)
    date_posted = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    url = models.CharField(max_length=500, default="")
    answer_length = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Answer (models.Model):
    answer = models.TextField()
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    question_url = models.CharField(max_length=400)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.answer

class Comment (models.Model):
    comment = models.CharField(max_length=200)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    answer_id = models.IntegerField()
    date_posted = models.DateTimeField(default=timezone.now)
    question_url = models.CharField(max_length=400, default="")


    def __str__(self):
        return self.comment