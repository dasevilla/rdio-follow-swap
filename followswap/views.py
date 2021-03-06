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
        'connection_count': RdioConnection.objects.filter(status='connected').count()
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

        followee_uid = new_connection.followee.social_auth.filter(provider='rdio_oauth2').get().uid

        payload = {
            'method': 'addFriend',
            'user': followee_uid
        }
        r = requests.post('https://www.rdio.com/api/1/', auth=BearerAuth(token),
            data=payload)

        new_connection.follower = request.user
        new_connection.status = 'connected'
        new_connection.save()

        payload = {
            'method': 'get',
            'keys': followee_uid,
            'extras': 'twitterUrl,facebookUrl,lastfmUrl',
        }
        r = requests.post('https://www.rdio.com/api/1/', auth=BearerAuth(token),
            data=payload)

        r.json()

        c = RequestContext(request, {
            'follower': new_connection.follower,
            'followee': new_connection.followee,
            'followee_rdio': r.json()['result'][followee_uid]
        })
        return render_to_response('meet.html', c)

def history(request):

    rdio_auth = request.user.social_auth.filter(provider='rdio_oauth2').get()
    token = rdio_auth.extra_data['access_token']


    def get_user_info(token, user_keys):
        payload = {
            'method': 'get',
            'keys': ','.join(user_keys),
            'extras': 'twitterUrl,facebookUrl,lastfmUrl',
        }
        r = requests.post('https://www.rdio.com/api/1/', auth=BearerAuth(token),
            data=payload)

        return r.json()['result']


    your_follow_connections = RdioConnection.objects.filter(status='connected').filter(follower=request.user)
    people_you_follow = [conn.followee for conn in your_follow_connections]
    people_you_follow_rdio_keys = [user.social_auth.filter(provider='rdio_oauth2').get().uid for user in people_you_follow]

    your_followee_connections = RdioConnection.objects.filter(status='connected').filter(followee=request.user)
    people_who_follow_you = set([conn.follower for conn in your_followee_connections])
    people_who_follow_you_rdio_keys = [user.social_auth.filter(provider='rdio_oauth2').get().uid for user in people_who_follow_you]

    user_data = get_user_info(token, set(people_you_follow_rdio_keys + people_who_follow_you_rdio_keys))

    c = RequestContext(request, {
        'followers': [user_data[user_key] for user_key in people_who_follow_you_rdio_keys],
        'followees': [user_data[user_key] for user_key in people_you_follow_rdio_keys],
    })
    return render_to_response('history.html', c)

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
