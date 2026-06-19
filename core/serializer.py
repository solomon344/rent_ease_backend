from rest_framework import serializers
from .models import Profile, Amenties, Property, Booking, PropertyMedia, Payout
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'address', 'phone', 'role']

class AmentiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenties
        fields = ['id', 'name', 'description']

class PropertyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyMedia
        fields = ['id', 'url', 'type', 'order']

class PropertySerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(read_only=True)
    amenities = AmentiesSerializer(many=True, read_only=True)
    media = PropertyMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'owner', 'name', 'description', 'location', 'price', 'image', 'beds', 'baths', 'guests', 'amenities', 'tags', 'media']

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'property', 'start_date', 'end_date', 'guests', 'status', 'total_price', 'payment_state', 'created_at']

class PayoutSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Payout
        fields = ['id', 'user', 'amount', 'mobile_money_number', 'payment_method', 'status', 'transaction_id', 'created_at', 'updated_at']