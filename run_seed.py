import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentease_backend.settings")
django.setup()

from core.seeds import amenities_seed, superuser_seed, property_seed

def main():
    amenities_seed()
    # superuser_seed()
    # property_seed()

if __name__ == "__main__":
    main()