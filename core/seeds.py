from core.models import Amenties
from django.contrib.auth.models import User
from core.models import Profile, Property
import random


def amenities_seed():
    amenities = [
        Amenties(name='wifi', description='Wifi'),
        Amenties(name='gym', description='Gym'),
        Amenties(name='ac', description='AC'),
        Amenties(name='pool', description='Pool'),
        Amenties(name='parking', description='Parking'),
        Amenties(name='garden', description='Garden'),
        Amenties(name='security', description='Security'),
        Amenties(name='cctv', description='CCTV'),
        Amenties(name='tv', description='TV'),
        Amenties(name='kitchen', description='Kitchen'),
    ]
    
    for amenity in amenities:
        amenity.save()
        print(f"Amenity {amenity.name} created")
        
    print("Amenities seeded successfully")
    

def superuser_seed():
    user = User.objects.create_superuser(username='admin@rentease.com', email='admin@rentease.com', password='admin', first_name='admin', last_name='admin')
    profile = Profile.objects.create(user=user, address='', phone='1234567890', role='seller')
    user.save()
    profile.save()
    print("Superuser created successfully")

def property_seed():
    user = User.objects.get(username='admin@rentease.com')
    profile = Profile.objects.get(user=user)
    images  = [
        "https://files.edgestore.dev/li1g6vchhfjyhtr3/rentEaseImages/_public/584ed2eb-cfa4-4a08-b008-c33fab09ea0e.jpg",
        "https://i.pinimg.com/736x/37/d4/96/37d4965ae66ed3c5b3dfcf117b9f3f6c.jpg",
        "https://i.pinimg.com/736x/15/b7/4a/15b74ae851241e4bd87628239e69b668.jpg",
        "https://i.pinimg.com/1200x/df/83/30/df833071fbf921ef4e27d42a3776138f.jpg",
        "https://i.pinimg.com/1200x/3c/01/ec/3c01ec4b5039be727c99fd50e65e5043.jpg",
        "https://i.pinimg.com/1200x/50/9d/ce/509dce6b282b0dcc48a129e94ad4c74c.jpg"
    ]
    names = [
        "Fajara Villa Mansion Mini",
        "Banjul Estate Mini Mansion",
        "Penthouse Mini Mansion",
        "Luxury Villa Mansion Mini",
        "Villa Mansion Mini",
        "Mansion Mega"
    ]
    locations = [
        "Fajara",
        "Banjul",
        "Bakau",
        "Serekunda",
        "Brikama",
        "Ker Serrigne"
    ]
    
    for i in range(1,6):
        p = Property.objects.create(
            owner=profile,
            name=names[i-1],
            description=f'Description for property {names[i-1]}',
            location=locations[i-1],
            price=random.randint(1000, 10000),
            image=images[i-1],
            tags=f'Tags {i}',
            beds=6,
            baths=2,
            guests=5,
        
        )
        p.amenities.add(*Amenties.objects.all())
        p.save()
        print(f"Property {names[i-1]} created")
        
    print("Properties seeded successfully")