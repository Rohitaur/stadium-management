from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Add_Stadium, StadiumBooking


class CustomUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'phone', 'role', 'password','staff_details']
    def validate(self, attrs):
        role = attrs.get('role')
        staff_details = attrs.get('staff_details')
        # Only staff can add staff_details
        if role in ['staff'] and not staff_details:
            raise serializers.ValidationError({"staff_details": "This field is required for staff."})
        if role == 'user' and staff_details:
            raise serializers.ValidationError({"staff_details": "User cannot add staff_details."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data
    



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        data['user'] = {
            'email': self.user.email,
            'name': self.user.name,
            'phone': self.user.phone,
            'role': self.user.role,
        }

        return data
    


class StadiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Add_Stadium
        fields = '__all__'

# stadium_booking_serializer
class StadiumBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StadiumBooking
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']