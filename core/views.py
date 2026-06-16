from django.shortcuts import render
from django.db import models
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from core.serializer import (ProfileSerializer,UserSerializer,AmentiesSerializer, BookingSerializer, PropertySerializer)
from core.models import (Profile,User,Amenties,Property,Booking,PropertyMedia)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, BaseInFilter
import uuid
import requests
import logging
import json
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
import modempay
from modempay.types import *
import secrets
import hashlib
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired


logger = logging.getLogger(__name__)

# Create your views here.

def render_email_template(template_name, context):
    return render_to_string(template_name, context)


def send_html_email(subject, recipient_list, template_name, context, from_email=None):
    html_content = render_email_template(template_name, context)
    text_content = strip_tags(html_content)
    message = EmailMultiAlternatives(
        subject,
        text_content,
        from_email or settings.DEFAULT_FROM_EMAIL,
        recipient_list,
    )
    message.attach_alternative(html_content, "text/html")
    message.send(fail_silently=False)


def safe_send_html_email(subject, recipient_list, template_name, context, from_email=None):
    try:
        send_html_email(subject, recipient_list, template_name, context, from_email)
        logger.info(f"Email sent successfully to {recipient_list}")
    except Exception as exc:
        logger.error(f"Failed to send email {template_name} to {recipient_list}: {str(exc)}", exc_info=True)
        print(f"Email Error: {template_name} -> {recipient_list}: {exc}")


def get_modempay_client():
    ModemPay = modempay.ModemPay
    api_key = getattr(settings, 'MODEM_API_KEY', None)
    if not api_key:
        raise ValueError("MODEM_API_KEY must be set in settings for ModemPay integration.")

    return ModemPay(api_key=api_key)


def create_modempay_intent(booking, guest):
    Modempay = get_modempay_client()
    currency = getattr(settings, 'MODEM_PAYMENT_CURRENCY', 'GMD')
    payment_methods = getattr(settings, 'MODEM_PAYMENT_METHODS', 'card').split(',')
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    # backend_url = settings.BACKEND_URL.rstrip('/')
    payload = {
        'amount': int(round(float(booking.total_price))),
        'currency': currency,
        'description': f"RentEase booking payment for {booking.property.name}",
        'metadata': {
            'booking_id': str(booking.id),
            'customer_email': guest.email,
        },
        'return_url': f"{frontend_url}/payment/verify?booking_id={booking.id}",
        'cancel_url': f"{frontend_url}/bookings?payment=cancelled",
        # 'callback_url': f"{backend_url}/api/v1/booking/payment/callback/",
        'payment_methods': payment_methods,
        'title': f"RentEase Booking #{booking.id}",
        'skip_url_validation': True
    }

    response = Modempay.payment_intents.create(payload)
    if isinstance(response, dict):
        data = response.get('data', {})
    else:
        data = getattr(response, 'data', {}) or {}

    return data


def verify_modempay_event(request):
    transaction_id = request.GET.get('transaction_id')
    
    try:
        print("payload",transaction_id)
        # print("MODEM_WEBHOOK_SECRET",settings.MODEM_WEBHOOK_SECRET)
        Modempay = get_modempay_client()
        transaction = Modempay.transactions.retrieve(transaction_id)
        if transaction:
            return transaction
    except Exception as exc:
        raise ValueError(f"ModemPay transaction verification failed: {exc}")


def calculate_nights(start_date, end_date):
    try:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
        return max((end_date - start_date).days, 0)
    except Exception:
        return 0


class ProfileView(APIView):

    def get(self, request,id, *args, **kwargs):
        profiles = Profile.objects.get(id=id)
        serializer = ProfileSerializer(profiles)
        return Response(serializer.data)
    
    def post(self, request,id, *args, **kwargs):
        data = request.data
        print(data)
        return Response({"message":"success"})
        

class PropertyFilterSet(FilterSet):
    """Custom filter set for Property model with support for range and IN lookups"""
    # Price range filters
    price__gte = NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = NumberFilter(field_name='price', lookup_expr='lte')
    
    # Amenities filter - supports filtering by multiple amenities IDs
    amenities__id__in = BaseInFilter(field_name='amenities__id', lookup_expr='in')
    
    class Meta:
        model = Property
        fields = {
            'id': ['exact'],
            'tags': ['exact', 'icontains'],
            'price': ['exact'],
            'location': ['exact', 'icontains'],
            'amenities': ['exact'],
            'owner': ['exact'],
            'owner__user__email': ['exact'],
        }


class PropertyView(ListAPIView):
    permission_classes = [AllowAny,]
    authentication_classes = []
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name','description']
    filterset_class = PropertyFilterSet
    

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
            property.media.all().delete()
            for i, item in enumerate(data.get('media', [])):
                PropertyMedia.objects.create(property=property, url=item['url'], type=item['type'], order=i)
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
            for i, item in enumerate(data.get('media', [])):
                PropertyMedia.objects.create(property=property, url=item['url'], type=item['type'], order=i)
            return Response({"message":"Property Created Successfully"})
    
  
    
    
    

    
    
    
    
    
    # def post(self, request, *args, **kwargs):
    #     data = request.data
    #     print(data)
    #     return Response({"message":"success"})
    

class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            property_obj = Property.objects.get(id=data['id'])
            
            # Prevent sellers from booking their own listings
            
            if property_obj.owner.user.email == request.user.email:
                return Response({"message": "You cannot book your own property"}, status=400)
            
            # Check if user has booked the house already
            if Booking.objects.filter(user=request.user, property=property_obj, status__in=['pending', 'confirmed']).exists():
                return Response({"message": "You already have an active booking for this house"}, status=400)

            # Check if the house is available (overlapping bookings)
            start_date = data['start_date']
            end_date = data['end_date']
            
            overlapping_bookings = Booking.objects.filter(
                property=property_obj,
                status__in=['pending', 'confirmed'],
                start_date__lt=end_date,
                end_date__gt=start_date
            )
            
            if overlapping_bookings.exists():
                return Response({"message": "Property is not available for these dates"}, status=400)
                
            booking = Booking.objects.create(
                user = request.user,
                property = property_obj,
                start_date = start_date,
                end_date = end_date,
                guests = data['guests'],
                total_price = data['total_price']
            )
            booking.save()

            owner = property_obj.owner.user
            frontend_url = settings.FRONTEND_URL.rstrip('/')
            safe_send_html_email(
                subject="New reservation request for your RentEase property",
                recipient_list=[owner.email],
                template_name="reservation-notification-owner.html",
                context={
                    'property_image': property_obj.image or '',
                    'property_name': property_obj.name,
                    'guest_name': f"{request.user.first_name} {request.user.last_name}",
                    'guest_email': request.user.email,
                    'guest_avatar': '',
                    'check_in_date': start_date,
                    'check_out_date': end_date,
                    'number_of_guests': data['guests'],
                    'number_of_nights': calculate_nights(start_date, end_date),
                    'total_amount': data['total_price'],
                    'guest_message': data.get('message', 'No message provided.'),
                    'accept_url': f"{frontend_url}/dashboard/reservations",
                    'decline_url': f"{frontend_url}/dashboard/reservations",
                },
            )

            return Response({"message":"Booking Created Successfully"})
        except Property.DoesNotExist:
            return Response({"message":"Property not found"}, status=404)
        except Exception as e:
            logger.error('BookingCreateView failed: %s', str(e), exc_info=True)
            return Response({"message":"Something went wrong"}, status=400)

class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        booking_id = data.get('id')
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
            if booking.status == 'cancelled':
                return Response({"message": "Booking is already cancelled"}, status=400)
            
            booking.status = 'cancelled'
            booking.save()
            return Response({"message": "Booking cancelled successfully"})
        except Booking.DoesNotExist:
            return Response({"message": "Booking not found or you don't have permission to cancel it"}, status=404)
        except Exception as e:
            return Response({"message": str(e)}, status=400)

class UserBookingView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        # Return bookings where the user is the buyer OR the owner of the property
        return Booking.objects.filter(
            models.Q(user=user) | models.Q(property__owner__user=user)
        ).distinct().order_by('-created_at')

class BookingAcceptView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        user = Profile.objects.get(user=request.user)
        if user.role != 'seller':
            return Response({"message":"You are not a seller","status":400})
        
        bookinId = data['id']
        status = data['status']
        
        booking = Booking.objects.get(id=bookinId)
        guest = booking.user
        property_obj = booking.property
        owner = property_obj.owner.user
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        base_context = {
            'property_image': property_obj.image or '',
            'property_name': property_obj.name,
            'property_location': property_obj.location,
            'check_in_date': booking.start_date,
            'check_out_date': booking.end_date,
            'number_of_guests': booking.guests,
            'number_of_nights': calculate_nights(booking.start_date, booking.end_date),
            'total_amount': booking.total_price,
            'booking_id': booking.id,
            'reservation_date': timezone.localtime(timezone.now()).strftime('%B %d, %Y'),
        }

        if status == 'rejected':
            booking.status = 'rejected'
            booking.payment_state = 'failed'
            booking.save()
            safe_send_html_email(
                subject="Your RentEase booking request has been declined",
                recipient_list=[guest.email],
                template_name="reservation-denied-user.html",
                context={
                    **base_context,
                    'property_address': property_obj.location,
                    'refund_amount': booking.total_price,
                    'alternative_property_1_image': property_obj.image or '',
                    'alternative_property_1_name': f"Cozy stay near {property_obj.location}",
                    'alternative_property_1_location': property_obj.location,
                    'alternative_property_1_price': property_obj.price,
                    'alternative_property_1_url': f"{frontend_url}/listings",
                    'alternative_property_2_image': property_obj.image or '',
                    'alternative_property_2_name': f"Modern home in {property_obj.location}",
                    'alternative_property_2_location': property_obj.location,
                    'alternative_property_2_price': property_obj.price,
                    'alternative_property_2_url': f"{frontend_url}/listings",
                    'browse_properties_url': f"{frontend_url}/listings",
                    'contact_support_url': f"mailto:{settings.DEFAULT_FROM_EMAIL}",
                },
            )
            return Response({"message":f"Booking from {booking.user.first_name} {booking.user.last_name} has been rejected","data":BookingSerializer(booking).data})

        if status == 'confirmed':
            try:
                booking.status = 'confirmed'
                booking.payment_state = 'requires_payment'
                intent = create_modempay_intent(booking, guest)
                booking.payment_intent_id = intent.get('id') or intent.get('payment_intent_id')
                booking.payment_link = intent.get('payment_link')
                booking.save()
            except Exception as exc:
                logger.error('Failed to create ModemPay payment intent: %s', exc, exc_info=True)
                return Response({"message": "Failed to create payment intent", "error": str(exc)}, status=500)

            safe_send_html_email(
                subject="Your RentEase booking is confirmed — complete your payment",
                recipient_list=[guest.email],
                template_name="reservation-approved-user.html",
                context={
                    **base_context,
                    'check_in_time': '3:00 PM',
                    'check_out_time': '11:00 AM',
                    'property_address': property_obj.location,
                    'host_name': f"{owner.first_name} {owner.last_name}".strip() or owner.username,
                    'host_phone': property_obj.owner.phone,
                    'host_bio': f"Your host for {property_obj.name}.",
                    'host_email': owner.email,
                    'booking_details_url': f"{frontend_url}/bookings",
                    'message_host_url': f"mailto:{owner.email}",
                    'payment_link': booking.payment_link,
                },
            )

            return Response({"message":f"Booking from {booking.user.first_name} {booking.user.last_name} has been accepted and payment link sent","data":BookingSerializer(booking).data})

        booking.status = status
        booking.save()
        return Response({"message":f"Booking from {booking.user.first_name} {booking.user.last_name} has been updated","data":BookingSerializer(booking).data})

class BookingView(ListAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user','property','id','status']


class BookingPaymentVerifyView(APIView):
    permission_classes = [AllowAny,]
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        booking_id = request.query_params.get('booking_id')
        if not booking_id:
            return Response({"message": "booking_id is required"}, status=400)

        booking = Booking.objects.filter(id=booking_id).first()
        if not booking:
            return Response({"message": "Booking not found"}, status=404)

        return Response({
            "booking_id": booking.id,
            "status": booking.status,
            "payment_state": booking.payment_state,
            "payment_link": booking.payment_link,
            "paid": booking.payment_state == 'paid',
        })


class PaymentCallbackView(APIView):
    permission_classes = [AllowAny,]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        booking_id = request.data.get('booking_id')
        transaction_id = request.data.get('transaction_id')

        if not booking_id or not transaction_id:
            return Response({"message": "booking_id and transaction_id are required"}, status=400)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            logger.warning('Payment callback received for unknown booking ID: %s', booking_id)
            return Response({"message": "Booking not found"}, status=404)

        try:
            modempay_client = get_modempay_client()
            transaction = modempay_client.transactions.retrieve(transaction_id)
        except Exception as exc:
            logger.error('ModemPay transaction retrieval failed for transaction_id %s: %s', transaction_id, exc, exc_info=True)
            return Response({"message": "Failed to retrieve transaction details from payment provider"}, status=500)

        if transaction and transaction.status == 'successful':
            booking.payment_state = 'paid'
            booking.status = 'confirmed'
            booking.payment_intent_id = transaction_id
            booking.save()

            # Send email to property owner
            owner = booking.property.owner.user
            frontend_url = settings.FRONTEND_URL.rstrip('/')
            safe_send_html_email(
                subject="Payment Received for Your RentEase Property",
                recipient_list=[owner.email],
                template_name="payment-received-owner.html", # Assuming a new template for payment received
                context={
                    'property_image': booking.property.image or '',
                    'property_name': booking.property.name,
                    'guest_name': f"{booking.user.first_name} {booking.user.last_name}".strip(),
                    'guest_email': booking.user.email,
                    'check_in_date': booking.start_date,
                    'check_out_date': booking.end_date,
                    'total_amount': booking.total_price,
                    'booking_id': booking.id,
                    'transaction_id': transaction_id,
                    'view_booking_url': f"{frontend_url}/dashboard/reservations",
                },
            )
            return Response({"message": "Payment verified and booking confirmed", "paid": True})
        else:
            booking.payment_state = 'failed'
            booking.save()
            return Response({"message": "Payment verification failed", "paid": False})
        

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


class GoogleAuthView(APIView):
    """Verify Google id_token via Google's tokeninfo endpoint using `requests` and return a Django JWT."""
    permission_classes = [AllowAny,]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        data = request.data or {}
        id_token_str = data.get('id_token') or request.headers.get('Authorization', '').split('Bearer ')[-1]
        if not id_token_str:
            return Response({"message":"id_token required"}, status=400)

        try:
            res = requests.get('https://oauth2.googleapis.com/tokeninfo', params={'id_token': id_token_str}, timeout=5)
            if res.status_code != 200:
                return Response({"message":"Invalid token"}, status=401)
            idinfo = res.json()
        except Exception as e:
            return Response({"message":"Token verification failed","error":str(e)}, status=400)

        google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None)
        if google_client_id and idinfo.get('aud') != google_client_id:
            return Response({"message":"Token audience mismatch"}, status=401)

        email = idinfo.get('email')
        if not email:
            return Response({"message":"Google token did not return email"}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message":"User not found"}, status=404)

        try:
            refresh = RefreshToken.for_user(user)
        except Exception as e:
            return Response({"message":"Could not create JWT","error":str(e)}, status=500)
        

        user_info = {
            'sub': idinfo.get('sub'),
            'email': email,
            'email_verified': idinfo.get('email_verified'),
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
        }

        profile = Profile.objects.get(user=user)
        user_info['role'] = profile.role
        user_info['phone'] = profile.phone
        # user_info['profile'] = ProfileSerializer(profile).data

        request.session['google_user'] = user_info
        request.session['google_authenticated'] = True

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_info,
        })


class PasswordResetRequestView(APIView):
    """
    Initiates a password reset by sending an email with a reset link.
    The reset token is time-limited (1 hour by default).
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        if not email:
            return Response({"message": "Email is required"}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Return success even if user not found to prevent email enumeration
            return Response({"message": "If the email exists, a password reset link has been sent."})
        
        # Generate reset token using Django's signing framework
        signer = TimestampSigner()
        token = signer.sign(user.email)
        
        # Build reset URL
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        reset_url = f"{frontend_url}/reset-password/confirm?token={token}"
        
        # Send email
        try:
            safe_send_html_email(
                subject="Reset your RentEase password",
                recipient_list=[user.email],
                template_name="password-reset-email.html",
                context={
                    'user_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                    'reset_url': reset_url,
                    'support_email': settings.DEFAULT_FROM_EMAIL,
                    'company_name': 'RentEase',
                },
            )
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}", exc_info=True)
            return Response({"message": "Failed to send reset email. Please try again."}, status=500)
        
        return Response({"message": "If the email exists, a password reset link has been sent."})


class PasswordResetConfirmView(APIView):
    """
    Validates the reset token and updates the user's password.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        new_password = request.data.get('password')
        
        if not token or not new_password:
            return Response({"message": "Token and new password are required"}, status=400)
        
        # Validate password length
        if len(new_password) < 8:
            return Response({"message": "Password must be at least 8 characters long"}, status=400)
        
        try:
            # Verify and unsign the token
            signer = TimestampSigner()
            # Token format is "email:timestamp:signature"
            email = signer.unsign(token, max_age=3600)  # 1 hour expiry
            
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            return Response({"message": "Password has been reset successfully."})
            
        except (BadSignature, SignatureExpired) as e:
            return Response({"message": "Invalid or expired reset token. Please request a new one."}, status=400)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)
        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}", exc_info=True)
            return Response({"message": "Failed to reset password. Please try again."}, status=500)


class PasswordResetValidateTokenView(APIView):
    """
    Validates a reset token without changing the password.
    Used to check if a token is valid before showing the reset form.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        
        if not token:
            return Response({"message": "Token is required"}, status=400)
        
        try:
            signer = TimestampSigner()
            email = signer.unsign(token, max_age=3600)
            
            # Check if user exists
            if not User.objects.filter(email=email).exists():
                return Response({"valid": False, "message": "User not found"}, status=404)
            
            return Response({"valid": True, "message": "Token is valid"})
            
        except SignatureExpired:
            return Response({"valid": False, "expired": True, "message": "Token has expired. Please request a new one."})
        except BadSignature:
            return Response({"valid": False, "message": "Invalid token"})
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}", exc_info=True)
            return Response({"valid": False, "message": "Token validation failed"}, status=400)
 