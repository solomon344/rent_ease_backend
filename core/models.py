from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    roles = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=roles)

    def __str__(self):
        return self.user.username
    
class Amenties(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Property(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=600, blank=True, null=True)
    beds = models.PositiveIntegerField()
    baths = models.PositiveIntegerField()
    guests = models.PositiveIntegerField()
    amenities = models.ManyToManyField(Amenties)
    tags = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title
    
bookin_status = (
    ('pending', 'PENDING'),
    ('confirmed', 'CONFIRMED'),
    ('cancelled', 'CANCELLED'),
    ('rejected', 'REJECTED'),
)

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    status = models.CharField(max_length=10, choices=bookin_status, default='pending')
    guests = models.PositiveIntegerField(null=True, blank=True, default=1)
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.property.title}"


    
