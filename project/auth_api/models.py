from datetime import timezone
import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from threading import Timer


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
    
    
    # Добавляем только эти два поля для решения конфликта
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_groups',
        related_query_name='custom_user_group',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_permissions',
        related_query_name='custom_user_permission',
    )

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
            raise ValueError("Вы уже активировали invite-code.")
        
        if not User.objects.filter(invite_code=code).exists():
            raise ValueError("Не правильный invite-code.")
        
        self.activated_invite_code = code
        self.save()


class AuthCode(models.Model):
    phone = models.CharField(max_length=17)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def create_or_replace(phone, code):
        """Создает новый код, удаляя предыдущий для того же номера телефона."""
        AuthCode.objects.filter(phone=phone).delete()  # Удаляем предыдущий код для номера
        return AuthCode.objects.create(phone=phone, code=code)
