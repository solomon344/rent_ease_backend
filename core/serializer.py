from rest_framework.serializers import ModelSerializer
from core.models import Property, Amenties, Profile, Booking
from django.contrib.auth.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ProfileSerializer(ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Profile
        fields = '__all__'

class AmentiesSerializer(ModelSerializer):
    class Meta:
        model = Amenties
        fields = '__all__'

class BookingSerializer(ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Booking
        fields = '__all__'


class PropertySerializer(ModelSerializer):
    amenities = AmentiesSerializer(many=True)
    owner = ProfileSerializer()
    bookings = BookingSerializer(many=True)
    class Meta:
        model = Property
        fields = '__all__'
        
        



