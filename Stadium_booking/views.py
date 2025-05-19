# Stadium_booking/views.py
from .serializers import StadiumBookingSerializer
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
from .models import CustomUser, StadiumBooking
from django.db import models
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
    
# ..............get-stadium-by-Id.....................

class StadiumDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, stadiumId):
        try:
            stadium = Add_Stadium.objects.get(sId=stadiumId)
        except Add_Stadium.DoesNotExist:
            return Response({"error": "Stadium not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = StadiumSerializer(stadium)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ..............get-all-stadiums-by-userId.....................
class StadiumsByUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, userId):
        stadiums = Add_Stadium.objects.filter(owner__id=userId)
        serializer = StadiumSerializer(stadiums, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# ..............update-stadium-by-Id.....................

class UpdateStadiumView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, stadiumId):
        try:
            stadium = Add_Stadium.objects.get(sId=stadiumId)
        except Add_Stadium.DoesNotExist:
            return Response({"error": "Stadium not found."}, status=status.HTTP_404_NOT_FOUND)
        # Optional: Only allow the owner to update
        if stadium.owner != request.user:
            raise PermissionDenied("You do not have permission to update this stadium.")
        serializer = StadiumSerializer(stadium, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Stadium updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# ..............delete-stadium-by-Id.....................
class DeleteStadiumView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, stadiumId):
        try:
            stadium = Add_Stadium.objects.get(sId=stadiumId)
        except Add_Stadium.DoesNotExist:
            return Response({"error": "Stadium not found."}, status=status.HTTP_404_NOT_FOUND)
        # Only allow the owner to delete
        if stadium.owner != request.user:
            raise PermissionDenied("You do not have permission to delete this stadium.")
        stadium.delete()
        return Response({"message": "Stadium deleted successfully."}, status=status.HTTP_200_OK)
    

#............common-operations.................
# ..............get-profile.....................

class GetProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CustomUserRegistrationSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# ..............update-profile.....................

class UpdateProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        print(request.data.get('staff_details'),request.data.get('role'))
        if request.data.get('role') == user.role:
            raise PermissionDenied("You cannot change your role.")
        if request.user.role == 'user' and request.data.get('staff_details'):
            raise PermissionDenied("You cannot add staff_details")
        serializer = CustomUserRegistrationSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Owner details updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ..............delete-user.....................

class DeleteUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
    
# ............get-all-stadiums.......................
class GetAllStadiumsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stadiums = Add_Stadium.objects.all()
        serializer = StadiumSerializer(stadiums, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# ..............get-all-the-staff-available.....................
class AllStaffDetailsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        staff_users = CustomUser.objects.filter(role='staff')
        staff_details_list = [
            {"id": user.id, "name": user.name, "email": user.email, "staff_details": user.staff_details}
            for user in staff_users
        ]
        return Response(staff_details_list, status=status.HTTP_200_OK)

# ..............filter-stadiums.....................

class FilterStadiumsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        event_name = request.data.get('event_name')
        max_price = request.data.get('max_price')
        location = request.data.get('location')

        stadiums = Add_Stadium.objects.all()

        # Filter by location (city, state, or area)
        if location:
            stadiums = stadiums.filter(
                models.Q(city__icontains=location) |
                models.Q(state__icontains=location) |
                models.Q(area__icontains=location)
            )

        # Filter by event name and price in event_types JSONField
        if event_name:
            stadiums = [stadium for stadium in stadiums if event_name in (stadium.event_types or {})]
            if max_price is not None:
                stadiums = [
                    stadium for stadium in stadiums
                    if event_name in (stadium.event_types or {}) and stadium.event_types[event_name] <= float(max_price)
                ]
        elif max_price is not None:
            # If only price is provided, filter stadiums where any event price is <= max_price
            stadiums = [
                stadium for stadium in stadiums
                if any(price <= float(max_price) for price in (stadium.event_types or {}).values())
            ]

        serializer = StadiumSerializer(stadiums, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# ..............book-stadium.....................
class BookStadiumView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = StadiumBookingSerializer(data=request.data)
        if request.user.role == 'owner':
            raise PermissionDenied("Stadium owners cannot book their own stadiums.")
        if serializer.is_valid():
            serializer.save(user=request.user, status='pending')
            return Response({"message": "Booking request sent to owner.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# ..............manage-booking-details.....................
class ManageBookingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = StadiumBooking.objects.get(id=booking_id)
        except StadiumBooking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        if booking.stadium.owner != request.user:
            raise PermissionDenied("Only the stadium owner can manage this booking.")

        action = request.data.get('action')
        if action == 'approve':
            booking.status = 'approved'
        elif action == 'cancel':
            booking.status = 'cancelled'
        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
        booking.save()
        return Response({"message": f"Booking {action}d.", "status": booking.status}, status=status.HTTP_200_OK)
    
# ...............cancel-booking-by-user.....................

class CancelBookingByUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = StadiumBooking.objects.get(id=booking_id, user=request.user)
        except StadiumBooking.DoesNotExist:
            return Response({"error": "Booking not found or not yours."}, status=status.HTTP_404_NOT_FOUND)
        if booking.status == 'cancelled':
            return Response({"message": "Booking is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = 'cancelled'
        booking.save()
        return Response({"message": "Booking cancelled successfully."}, status=status.HTTP_200_OK)