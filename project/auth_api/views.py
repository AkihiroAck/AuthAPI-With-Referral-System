from django.shortcuts import render, redirect
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework import status
from .models import User, AuthCode
from .serializers import ProfileSerializer
from django.core.exceptions import ObjectDoesNotExist
import random
from django.contrib import messages


class PhoneAuthView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        code = f"{random.randint(1000, 9999)}"
        
        AuthCode.create_or_replace(phone=phone, code=code)
        
        return Response({"message": "Authorization code sent.", "code": code})


class VerifyCodeView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        
        if not phone or not code:
            return Response({"error": "Phone and code are required."}, status=status.HTTP_400_BAD_REQUEST)
        
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
            user.activate_invite_code(invite_code)
        except ObjectDoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "Invite-code activated successfully."})


def register_page(request):
    """Страница для ввода номера телефона и получения кода."""
    if request.method == "POST":
        phone = request.POST.get("phone")
        if not phone:
            messages.error(request, "Введите номер телефона.")
            return redirect("register_page")
        
        # Преобразуем данные формы в JSON
        drf_request = Request(request, parsers=[JSONParser()])
        drf_request._full_data = {"phone": phone}  # Устанавливаем данные в формате JSON

        # Используем API PhoneAuthView
        response = PhoneAuthView().post(drf_request)
        if response.status_code == 200:
            messages.success(request, f"Код отправлен на номер {phone}. DEBUG: (CODE: {response.data.get('code')})")
            return redirect("verify_page")
        else:
            messages.error(request, response.data.get("error", "Ошибка при отправке кода."))
            return redirect("register_page")
    
    return render(request, "auth_api/register.html")


def verify_page(request):
    """Страница для ввода кода подтверждения."""
    if request.method == "POST":
        phone = request.POST.get("phone")
        code = request.POST.get("code")
        
        if not phone or not code:
            messages.error(request, "Введите номер телефона и код.")
            return redirect("verify_page")
        
        # Преобразуем данные формы в JSON
        drf_request = Request(request, parsers=[JSONParser()])
        drf_request._full_data = {"phone": phone, "code": code}  # Устанавливаем данные в формате JSON

        # Используем API VerifyCodeView
        response = VerifyCodeView().post(drf_request)
        if response.status_code == 200:
            user_id = response.data.get("user_id")
            request.session["user_id"] = user_id
            return redirect("profile_page")
        else:
            messages.error(request, response.data.get("error", "Ошибка при проверке кода."))
            return redirect("verify_page")
    
    return render(request, "auth_api/verify.html")


def profile_page(request):
    """Страница профиля пользователя."""
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("register_page")
    
    response = ProfileView().get(request, user_id=user_id)
    if response.status_code != 200:
        messages.error(request, response.data.get("error", "Ошибка при загрузке профиля."))
        return redirect("register_page")
    
    user_data = response.data
    invited_users = user_data.get("invited_users", [])
    
    if request.method == "POST":
        invite_code = request.POST.get("invite_code")
        if invite_code:
            # Преобразуем данные формы в JSON
            drf_request = Request(request, parsers=[JSONParser()])
            drf_request._full_data = {"invite_code": invite_code}  # Устанавливаем данные в формате JSON

            # Используем API ProfileView для активации инвайт-кода
            response = ProfileView().post(drf_request, user_id=user_id)
            if response.status_code == 200:
                messages.success(request, "Инвайт-код успешно активирован.")
            else:
                messages.error(request, response.data.get("error", "Ошибка при активации инвайт-кода."))
    
    return render(request, "auth_api/profile.html", {
        "user": user_data,
        "invited_users": invited_users,
    })
