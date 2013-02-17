from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

import requests
from requests.auth import AuthBase

from library.models import RdioConnection

def home(request):
    c = RequestContext(request, {
        # something good
    })
    return render_to_response('index.html', c)


def give(request):

    # Check to see how many waiting connections you have
    num_waiting_connections = RdioConnection.objects.filter(status='waiting').filter(followee=request.user).count()
    if num_waiting_connections >= 5:
        c = RequestContext(request, {
            'waiting_count': num_waiting_connections
        })
        return render_to_response('overlimit.html', c)

    # Agree to follow someone
    connection = RdioConnection(followee=request.user)
    connection.save()

    # Find who you follow already
    users_already_following = set()
    users_already_following.add(request.user)
    query = RdioConnection.objects.filter(status='connected').filter(follower=request.user) # Connections where you are the follower
    if query.exists():
        users_already_following.update([connection.followee for connection in query])

    # Find someone to follow
    available_connections = RdioConnection.objects.filter(status='waiting').exclude(followee__in=users_already_following).order_by('?')
    if available_connections.count() == 0:
        # no friends to meet yet
        c = RequestContext(request, {
            # something good
        })
        return render_to_response('none.html', c)

    else:
        new_connection = available_connections[0]

        follower_rdio_auth = request.user.social_auth.filter(provider='rdio_oauth2').get()
        token = follower_rdio_auth.extra_data['access_token']

        payload = {
            'method': 'addFriend',
            'user': new_connection.followee.social_auth.filter(provider='rdio_oauth2').get().uid
        }
        r = requests.post('https://www.rdio.com/api/1/', auth=BearerAuth(token),
            data=payload)

        new_connection.follower = request.user
        new_connection.status = 'connected'
        new_connection.save()

        c = RequestContext(request, {
            'follower': new_connection.follower,
            'followee': new_connection.followee,
        })
        return render_to_response('meet.html', c)


def sign_out(request):
    response = logout(request, next_page=reverse('index'))
    return HttpResponse(response)


class BearerAuth(AuthBase):
    """Adds a HTTP Bearer token to the given Request object."""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer %s' % self.token
        return r
