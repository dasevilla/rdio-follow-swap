from django.contrib.auth.models import User
from django.db import models
from django.utils import simplejson


REQUEST_STATES = (
    (u'connected', u'Connected'),
    (u'waiting', u'Waiting'),
)

class RdioConnection(models.Model):
    """
    A follower offers themselves to follow a user.

    Alice follows Bob. Alice is the follower, Bob is the followee.
    """

    follower = models.ForeignKey(User, related_name='follower_connections', blank=True, null=True)

    followee = models.ForeignKey(User, related_name='followee_connections', blank=False, null=True)

    status = models.CharField(max_length=10, choices=REQUEST_STATES,
        blank=False, default='waiting')
