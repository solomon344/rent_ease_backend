from rest_framework.serializers import ModelSerializer
from core.models import Property, Amenties, Profile, Booking, PropertyMedia
from django.contrib.auth.models import User


class UserSerializer(ModelSerializer):
    profile = "ProfileSerializer"
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


class PropertyMediaSerializer(ModelSerializer):
    class Meta:
        model = PropertyMedia
        fields = ['id', 'url', 'type', 'order']


class PropertySerializer(ModelSerializer):
    amenities = AmentiesSerializer(many=True)
    owner = ProfileSerializer()
    media = PropertyMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = '__all__'


class BookingSerializer(ModelSerializer):
    user = UserSerializer()
    property = PropertySerializer()
    class Meta:
        model = Booking
        fields = '__all__'



        
        



