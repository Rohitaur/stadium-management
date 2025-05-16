# stadium_booking/urls.py
from django.urls import path
from .views import UserRegistrationView, CustomLoginView
from .views import AddStadiumView
from .views import LoginAPIView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('add-stadium/', AddStadiumView.as_view(), name='add-stadium'),
]
