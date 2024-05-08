from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Creates a new user and returns an authentication token'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username for the new user')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = 'password'  # You can set a default password or prompt for one

        # Create a new user
        user = User.objects.create_user(username, password=password)
        # Create an authentication token for the user
        token, created = Token.objects.get_or_create(user=user)
        # Print the token
        self.stdout.write(self.style.SUCCESS(f'Token for {user.username}: {token.key}'))
