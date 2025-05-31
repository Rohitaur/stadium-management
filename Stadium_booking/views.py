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
from datetime import datetime, timedelta,date
# ------------------- USER REGISTRATION -------------------
class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny] 

    def post(self, request):
        serializer = CustomUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Registration successful",
                "key": "success",
                "status": status.HTTP_201_CREATED,
                "data": {
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                    "phone": user.phone,
                }
            }, status=status.HTTP_201_CREATED)
        else:
            # Get first error message from serializer.errors
            error_messages = []
            for field, errors in serializer.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            error_message = " | ".join(error_messages) if error_messages else "Registration failed"
            return Response({
                "message": error_message,
                "key": "error",
                "status": status.HTTP_400_BAD_REQUEST,
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        


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
                "message": "Login successful",
                "key": "success",
                "status": status.HTTP_200_OK,
                "data": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": user_data
                }
            }, status=status.HTTP_200_OK)
        else:
            # Collect error messages from serializer.errors
            error_messages = []
            for field, errors in serializer.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            error_message = " | ".join(error_messages) if error_messages else "Login failed"
            return Response({
                "message": error_message,
                "key": "error",
                "status": status.HTTP_400_BAD_REQUEST,
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ------------------- ADD STADIUM -------------------
class AddStadiumView(APIView):

    authentication_classes= [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users allowed

    def post(self, request):
        data = request.data.copy()
        # Check permission before allowing to add stadium
        if getattr(request.user, 'role', None) != 'owner':
            raise PermissionDenied("Only owners can add a stadium.")
        data['owner'] = request.user.id  # stadium owner = current user

         # Check for duplicate stadium (same name and address for this owner)
        exists = Add_Stadium.objects.filter(
            owner=request.user,
            name=data.get('name'),
            area=data.get('area'),
            city=data.get('city'),
            state=data.get('state'),
            pincode=data.get('pincode')
        ).exists()
        if exists:
            return Response({
                "message": "A stadium with the same name and address already exists.",
                "key": "error",
                "status": status.HTTP_400_BAD_REQUEST,
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)


        serializer = StadiumSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Stadium added successfully",
                "key": "success",
                "status": status.HTTP_201_CREATED,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        # Collect error messages from serializer.errors
        error_messages = []
        for field, errors in serializer.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")
        error_message = " | ".join(error_messages) if error_messages else "Stadium creation failed"
        return Response({
            "message": error_message,
            "key": "error",
            "status": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)
    
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

        # Filter by price (new attribute)
        if max_price is not None:
            try:
                max_price = float(max_price)
                stadiums = stadiums.filter(price__lte=max_price)
            except ValueError:
                return Response({"message": "Invalid max_price value.", "key": "error", "status": status.HTTP_400_BAD_REQUEST, "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        # Filter by event name in event_types JSONField
        if event_name:
            stadiums = [stadium for stadium in stadiums if event_name in (stadium.event_types or {})]

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

        stadium_id = request.data.get('stadium')
        event_date = request.data.get('event_date')
        end_date = request.data.get('end_date')  # New: user must provide end_date
             

        
        if event_date is None or end_date is None:
            return Response({
                "message": "Both event_date and end_date are required.",
                "key": "error",
                "status": False,
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)        


        # Yeh block yahan likhein:
        if isinstance(event_date, date):
            start = event_date
        else:
            start = datetime.strptime(str(event_date), "%Y-%m-%d").date()

        if isinstance(end_date, date):
            end = end_date
        else:
            end = datetime.strptime(str(end_date), "%Y-%m-%d").date()

        # Get stadium and prices
        try:
            stadium = Add_Stadium.objects.get(pk=stadium_id)
        except Add_Stadium.DoesNotExist:
            return Response({"message": "Stadium not found.", "key": "error", "status": False, "data": {}}, status=status.HTTP_404_NOT_FOUND)

        owner_price = float(stadium.price)
        gst_percent = float(stadium.gst_percent)
        service_percent = float(stadium.service_percent)

        # Calculate number of days
        num_days = (end - start).days + 1
        if num_days < 1:
            return Response({"message": "End date must be after start date.", "key": "error", "status": False, "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate base price for all days
        base_price = owner_price * num_days
        gst_amount = base_price * gst_percent / 100
        service_amount = base_price * service_percent / 100
        total_price = base_price + gst_amount + service_amount

        # Check for overdue (if booking end_date < today, apply fine)
        today = datetime.now().date()
        extra_charges = 0
        fine_per_day = owner_price * 0.5  # Example: 50% of daily price as fine
        if end < today:
            overdue_days = (today - end).days
            extra_charges = fine_per_day * overdue_days
            total_price += extra_charges

        # Check for existing booking overlap
        overlap = StadiumBooking.objects.filter(
            stadium_id=stadium_id,
            status__in=['pending', 'approved'],
            event_date__lte=end,
            end_date__gte=start
        ).exists()
        if overlap:
            return Response({
                "message": "The stadium is already booked for these dates.",
                "key": "error",
                "status": False,
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save(
                user=request.user,
                status='approved',
                extra_charges=extra_charges
            )
            return Response({
                "message": "Stadium booked Successfully.",
                "key": "success",
                "status": status.HTTP_201_CREATED,
                "data": {
                    **serializer.data,
                    "price_breakdown": {
                        "base_price": base_price,
                        "days": num_days,
                        "owner_price_per_day": owner_price,
                        "gst_percent": f"{int(gst_percent)}%",
                        "gst_amount": gst_amount,
                        "service_percent": f"{int(service_percent)}%",
                        "service_amount": service_amount,
                        "extra_charges": extra_charges,
                        "total_price": total_price
                    }
                }
            }, status=status.HTTP_201_CREATED)
        # Collect error messages from serializer.errors
        error_messages = []
        for field, errors in serializer.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")
        error_message = " | ".join(error_messages) if error_messages else "Booking failed"
        return Response({
            "message": error_message,
            "key": "error",
            "status": False,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
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