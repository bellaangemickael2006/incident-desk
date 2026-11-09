from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the two course user accounts and two admin accounts (idempotent)."

    def handle(self, *args, **options):
        User = get_user_model()

        # Simple users (no staff/superuser)
        simple_users = [
            {"username": "bellaangesimple", "password": "Bella2006", "is_staff": False, "is_superuser": False},
            {"username": "Nazairefabsimple", "password": "N@zaire2026", "is_staff": False, "is_superuser": False},
        ]

        # Admin users (staff + superuser)
        admin_users = [
            {"username": "bellaangeadmin", "password": "Bella2006admin", "is_staff": True, "is_superuser": True},
            {"username": "Nazairefabadmin", "password": "N@zaire2026", "is_staff": True, "is_superuser": True},
        ]

        for spec in simple_users + admin_users:
            user, created = User.objects.get_or_create(username=spec["username"])
            if created:
                user.is_staff = spec["is_staff"]
                user.is_superuser = spec["is_superuser"]
                # set_password bypasses length validators — intentional for course accounts
                user.set_password(spec["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {spec['username']}"))
            else:
                self.stdout.write(f"User already exists: {spec['username']}")
