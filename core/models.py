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
    LOCATION_CHOICES = [
        ('Banjul', 'Banjul'),
        ('Kololi', 'Kololi'),
        ('Kotu', 'Kotu'),
        ('Fajara', 'Fajara'),
        ('Brufut', 'Brufut'),
        ('Serekunda', 'Serekunda'),
        ('Bakau', 'Bakau'),
        ('Banjul West', 'Banjul West'),
        ('Banjul East', 'Banjul East'),
        ('Banjul North', 'Banjul North'),
        ('Banjul South', 'Banjul South'),
        ('Brikama', 'Brikama'),
        ('Janjanbureh', 'Janjanbureh'),
        ('Kanifing', 'Kanifing'),
        ('Kerewan', 'Kerewan'),
        ('Kuntaur', 'Kuntaur'),
        ('Mansakonko', 'Mansakonko'),
        ('Sukuta', 'Sukuta'),
        ('Yundum', 'Yundum'),
    ]

    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=600, blank=True, null=True)
    beds = models.PositiveIntegerField()
    baths = models.PositiveIntegerField()
    guests = models.PositiveIntegerField()
    amenities = models.ManyToManyField(Amenties)
    tags = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

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
    payment_intent_id = models.CharField(max_length=200, blank=True, null=True)
    payment_link = models.URLField(max_length=600, blank=True, null=True)
    payment_state_choices = (
        ('pending', 'PENDING'),
        ('requires_payment', 'REQUIRES_PAYMENT'),
        ('paid', 'PAID'),
        ('failed', 'FAILED'),
    )
    payment_state = models.CharField(max_length=20, choices=payment_state_choices, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.property.name}"

class Payout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mobile_money_number = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=[
        ('wave', 'Wave'),
        ('afrimoney', 'Afrimoney'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    transaction_id = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"

class PropertyMedia(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='media')
    url = models.CharField(max_length=600)
    type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='image')
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.type} - {self.property.name}"