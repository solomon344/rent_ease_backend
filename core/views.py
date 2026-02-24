from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from core.serializer import (ProfileSerializer,UserSerializer,AmentiesSerializer, BookingSerializer, PropertySerializer)
from core.models import (Profile,User,Amenties,Property,Booking)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
import uuid

# Create your views here.


class ProfileView(APIView):

    def get(self, request,id, *args, **kwargs):
        profiles = Profile.objects.get(id=id)
        serializer = ProfileSerializer(profiles)
        return Response(serializer.data)
    
    def post(self, request,id, *args, **kwargs):
        data = request.data
        print(data)
        return Response({"message":"success"})
        

class PropertyView(ListAPIView):
    permission_classes = [AllowAny,]
    authentication_classes = []
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name','description']
    filterset_fields = ['tags','price','amenities','id','owner']
    

class PropertyCreateView(APIView):
    
    def post(self, request, *args, **kwargs):
        id =  kwargs.get('id') 
        data = request.data
        print(data)
        profile = Profile.objects.get(user=request.user)
        if profile.role != 'seller':
            return Response({"message":"You are not a seller","status":400})
        elif id:
            property = Property.objects.get(id=id)
            property.name = data['name']
            property.description = data['description']
            property.location = data['location']
            property.price = data['price']
            property.image = data['image']
            property.tags = data['tags']
            property.beds = data['beds']
            property.baths = data['baths']
            property.guests = data['guests']
            property.save()
            property.amenities.clear()
            property.amenities.add(*data['amenities'])
            property.save()
            return Response({"message":"Property Updated Successfully"})
        else:
            property = Property.objects.create(
            owner = profile,
            name = data['name'],
            description = data['description'],
            location = data['location'],
            price = data['price'],
            image = data['image'],
            beds = data['beds'],
            baths = data['baths'],
            guests = data['guests'],
            tags = data['tags'],
            )
            
            property.amenities.add(*data['amenities'])
            property.save()
            
            return Response({"message":"Property Created Successfully"})
    
  
    
    
    

    
    
    
    
    
    # def post(self, request, *args, **kwargs):
    #     data = request.data
    #     print(data)
    #     return Response({"message":"success"})
    

class BookingView(APIView):

    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        if id:
            bookings = Booking.objects.get(id=id)
        else:
            bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings,many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        return Response({"message":"success"})

class AmentiesView(APIView):
    permission_classes = [AllowAny,]
    authentication_classes = []
    
    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        if id:
            amenties = Amenties.objects.get(id=id)
        else:
            amenties = Amenties.objects.all()
        serializer = AmentiesSerializer(amenties,many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        return Response({"message":"success"})
    

class UserView(APIView):
    
    permission_classes = [AllowAny,]
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)

        try:
            if User.objects.filter(email=data['email']).exists():
                return Response({"message":"User Already Exists, Please Login"},status=400)
            user = User.objects.create_user(username=data['email'],email=data['email'],password=data['password'],first_name=data['firstName'],last_name=data['lastName'])
            profile = Profile.objects.create(user=user,address="",phone=data['phone'],role=data['role'])
            user.save()
            profile.save()
            return Response({"message":"Account Created Successfully"})
        except Exception as e:
            return Response({"message":str(e)},status=400)
        

class UserMeView(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, *args, **kwargs):
        users = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user=users)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    

class LogInView(APIView):
    permission_classes = [AllowAny, ]
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        print('data',request.data)
        try:
            user = User.objects.get(username=request.data['email'])
            if not user:
                return Response({"message":"Invalid Email or Password"},status=400)
            elif not user.check_password(request.data['password']):
                return Response({"message":"Invalid Email or Password"},status=400)
            profile = Profile.objects.get(user=user)
            token = RefreshToken.for_user(user)
            return Response({"access":str(token.access_token),"refresh":str(token),"profile":ProfileSerializer(profile).data})
        except Exception as e:
            return Response({"message":str(e)},status=400)
 