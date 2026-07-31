from django.contrib.auth.models import AbstractUser
from django.db import models


    
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('donor', 'Donor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    def save(self, *args, **kwargs):
        # Superusers (e.g. created with createsuperuser) always get the
        # admin dashboard and full access, regardless of what role was set.
        if self.is_superuser:
            self.role = 'admin'
        # Anyone with admin/manager role automatically gets staff access,
        # so custom-dashboard permission checks stay in sync with role changes
        # made from the "Manage Users" screen.
        if self.role in ('admin', 'manager'):
            self.is_staff = True
        super().save(*args, **kwargs)