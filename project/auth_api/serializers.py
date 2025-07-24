from rest_framework import serializers
from .models import User

class ProfileSerializer(serializers.ModelSerializer):
    invited_users = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['phone', 'invite_code', 'activated_invite_code', 'invited_users']
    
    def get_invited_users(self, obj):
        # Получаем список номеров телефонов пользователей, которые активировали инвайт-код текущего пользователя
        return list(obj.get_invited_users().values_list('phone', flat=True))