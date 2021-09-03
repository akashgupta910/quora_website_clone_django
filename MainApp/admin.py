from django.contrib import admin
from .models import Users, Question, Answer, Comment

admin.site.register(Users)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Comment)