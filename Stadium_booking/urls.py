# stadium_booking/urls.py
from django.urls import path
from .views import *
from .views import UserRegistrationView, CustomLoginView,DeleteUserView,AllStaffDetailsView
from .views import AddStadiumView,UpdateProfileView,GetProfileView,GetAllStadiumsView, FilterStadiumsView
from .views import LoginAPIView, StadiumDetailView,StadiumsByUserView, UpdateStadiumView,DeleteStadiumView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('add-stadium/', AddStadiumView.as_view(), name='add-stadium'),
    path('get-stadium/<int:stadiumId>/', StadiumDetailView.as_view(), name='get-stadium'),
    path('get-all-stadiums/<int:userId>/', StadiumsByUserView.as_view(), name='get-all-stadiums'),
    path('update-stadium/<int:stadiumId>/', UpdateStadiumView.as_view(), name='update-stadium'),
    path('delete-stadium/<int:stadiumId>/', DeleteStadiumView.as_view(), name='delete-stadium'),
    path('get-profile/', GetProfileView.as_view(), name='get-profile'),
    path('update-profile/',UpdateProfileView.as_view(), name='update-profile'),
    path('user-delete/',DeleteUserView.as_view(),name='user-delete'),
    path('get-stadiums/',GetAllStadiumsView.as_view(),name='get-stadiums'),
    path('get-all-staff/',AllStaffDetailsView.as_view(),name='get-all-staff'),
    path('filter-stadiums/',FilterStadiumsView.as_view(),name='filter-stadiums'),
    path('book-stadium/',BookStadiumView.as_view(),name='book-stadium'),
    path('manage-booking/<int:booking_id>/',ManageBookingView.as_view(),name='manage-booking'),
    path('cancel-booking/<int:booking_id>/',CancelBookingByUserView.as_view(),name='cancel-booking'),
]
