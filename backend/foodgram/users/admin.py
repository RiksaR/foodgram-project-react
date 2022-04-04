from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name',]
    list_filter = ('email', 'username',)
