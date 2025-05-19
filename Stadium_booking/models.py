
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=50, choices=(('owner', 'Owner'), ('user', 'User'), ('staff', 'Staff')))
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    staff_details = models.JSONField(default=dict, blank=True, null=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone', 'role']

    def __str__(self):
        return self.email
    


# ADD STADIUM

class Add_Stadium(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    sId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    area = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='Stadium_images/', null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)
    event_types = models.JSONField(default=dict, blank=True, null=False)

    
    class Meta:
        permissions = [
            ("can_add_stadium", "can add stadium"),
            ("can_update_stadium", "Can update stadium"),
            ("can_delete_stadium", "Can delete stadium"),
            ("can_view_stadium", "Can view stadium"),
        ]
     
    def __str__(self):
        return self.name

# Stadium Booking
class StadiumBooking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    stadium = models.ForeignKey(Add_Stadium, on_delete=models.CASCADE, related_name='bookings')
    event_name = models.CharField(max_length=100)
    event_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)