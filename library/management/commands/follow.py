from django.core.management.base import BaseCommand

from social_auth.models import UserSocialAuth


import requests
from requests.auth import AuthBase


class BearerAuth(AuthBase):
    """Adds a HTTP Bearer token to the given Request object."""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer %s' % self.token
        return r


class Command(BaseCommand):
    help = 'Start following someone'

    def handle(self, *args, **options):
        if len(args) != 2:
            print 'Missing parameters'
            return

        follower = UserSocialAuth.objects.filter(uid=args[0]).get()
        followee = UserSocialAuth.objects.filter(uid=args[1]).get()

        token = follower.extra_data['access_token']

        payload = {
            'method': 'removeFriend',
            'user': followee.uid
        }
        r = requests.post('https://www.rdio.com/api/1/', auth=BearerAuth(token),
            data=payload)

        print r.text


        print follower.user.first_name, 'is now following', followee.user.first_name
