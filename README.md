# Follow Swap for Rdio

Follow a random person on Rdio and receive a random follower later. Built at [Music Hack Day SF 2013](http://sf.musichackday.org/2013/)

## Develop

Create a `.env` file with the following defined:

    AWS_ACCESS_KEY_ID=
    AWS_SECRET_ACCESS_KEY=
    DJANGO_DEBUG=true
    DJANGO_SECRET_KEY=
    RDIO_OAUTH2_KEY=
    RDIO_OAUTH2_SECRET=

Setup and run locally:

    $ pip install -r requirements.txt
    $ foreman run python manage.py syncdb
    $ foreman run python manage.py runserver

## Deploy

Before first deploy:

    $ heroku apps:create <app_name>
    $ heroku addons:add heroku-postgresql:dev
    $ heroku config:set <contents of .env>

First deploy:

    $ git push heroku master
    $ heroku run python manage.py syncdb
    $ heroku ps:scale web=1

For each deployment thereafter:

    $ foreman run python manage.py collectstatic
    $ git push heroku master
