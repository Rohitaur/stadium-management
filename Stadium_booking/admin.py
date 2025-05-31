from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import Add_Stadium, CustomUser , StadiumBooking

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'name', 'phone', 'role', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'role', 'password1', 'password2', 'is_staff', 'is_superuser', 'staff_details'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)



# Register your models here.

class AddStadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'owner', 'is_available')
    search_fields = ('name', 'city', 'state')
    list_filter = ('city', 'state', 'is_available')

class StadiumBookingAdmin(admin.ModelAdmin):
    list_display = ('stadium', 'user', 'event_name', 'event_date', 'status')
    search_fields = ('stadium__name', 'user__email', 'event_name')
    list_filter = ('status', 'event_date')
    actions = ['approve_bookings']

    def approve_bookings(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} bookings approved.")
    approve_bookings.short_description = "Approve selected bookings"

 
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Add_Stadium, AddStadiumAdmin)
admin.site.register(StadiumBooking, StadiumBookingAdmin)

