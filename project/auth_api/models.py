import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    invite_code = models.CharField(max_length=6, unique=True, blank=True)
    activated_invite_code = models.CharField(max_length=6, blank=True, null=True)
    
    USERNAME_FIELD = 'phone'
    username = None
    

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_unique_invite_code()
        super().save(*args, **kwargs)


    def generate_unique_invite_code(self):
        """Генерирует уникальный инвайт-код"""
        while True:
            new_code = self.generate_invite_code()
            if not User.objects.filter(invite_code=new_code).exists():
                return new_code
    

    @staticmethod
    def generate_invite_code():
        characters = string.ascii_uppercase + string.digits + '!@#$%^&*'
        return ''.join(random.choice(characters) for _ in range(6))


    def get_invited_users(self):
        """Возвращает список пользователей, которые активировали инвайт-код текущего пользователя"""
        return User.objects.filter(activated_invite_code=self.invite_code)


    def activate_invite_code(self, code):
        """Активирует инвайт-код, если он еще не был активирован"""
        if self.activated_invite_code:
            raise ValueError("Invite code has already been activated.")
        
        if not User.objects.filter(invite_code=code).exists():
            raise ValueError("Invalid invite code.")
        
        self.activated_invite_code = code
        self.save()
        