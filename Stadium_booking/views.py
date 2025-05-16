# Stadium_booking/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import CustomUserRegistrationSerializer, LoginSerializer, StadiumSerializer, CustomTokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.exceptions import PermissionDenied
from .models import Add_Stadium
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny


# ------------------- USER REGISTRATION -------------------
class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]  # ✅ Anyone can register

    def post(self, request):
        serializer = CustomUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------- USER LOGIN -------------------
class LoginAPIView(APIView):
    authentication_classes= []
    permission_classes = [AllowAny]  # ✅ Login also doesn't require auth

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            user_data = {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": user.name 
            }
            return Response({
                "message": "Login sucessful",
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ------------------- ADD STADIUM -------------------
class AddStadiumView(APIView):

    authentication_classes= [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # ✅ Only logged-in users allowed

    def post(self, request):
        data = request.data.copy()
        # Check permission before allowing to add stadium
        if getattr(request.user, 'role', None) != 'owner':
            raise PermissionDenied("Only owners can add a stadium.")
        data['owner'] = request.user.id  # stadium owner = current user
        serializer = StadiumSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Stadium added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
