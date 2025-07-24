from django.shortcuts import render
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, AuthCode
from .serializers import ProfileSerializer
from django.core.exceptions import ObjectDoesNotExist
import random


class PhoneAuthView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate a 4-digit code
        code = f"{random.randint(1000, 9999)}"
        
        # Create or replace the AuthCode
        AuthCode.create_or_replace(phone=phone, code=code)
        
        # Simulate sending the code with a delay
        time.sleep(2)
        return Response({"message": "Authorization code sent.", "code": code})


class VerifyCodeView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        
        if not phone or not code:
            return Response({"error": "Phone and code are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем существование кода без try-except
        auth_code_exists = AuthCode.objects.filter(
            phone=phone,
            code=code
        ).exists()

        if not auth_code_exists:
            return Response({"error": "Invalid phone or code."}, status=status.HTTP_400_BAD_REQUEST)
    
        # Check if user exists, if not create a new user
        user, created = User.objects.get_or_create(phone=phone)

        if created:
            user.save()
        
        return Response({"message": "Authorization successful.", "user_id": user.id})


class ProfileView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(user)
        return Response(serializer.data)

    def post(self, request, user_id):
        invite_code = request.data.get('invite_code')
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if user.activated_invite_code:
            return Response({"error": "Invite code already activated."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not User.objects.filter(invite_code=invite_code).exists():
            return Response({"error": "Invalid invite code."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.activate_invite_code(invite_code)
        return Response({"message": "Invite code activated successfully."})
