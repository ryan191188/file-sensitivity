# file-sensitivity-score

RESTful API service based on Django-Rest-Framework to upload files and calculate sensitivity score

## Description

1. Simple User Authentication based on default user model (username-password)
2. JWT Token Authentication on Login
3. Uploading of files to media folder and file path saved to database (can be extended to external storage API)
4. Listing of files with filter / pagination (default=10)
5. Celery (Periodic task: every 5 mins): for all files, calculate sensitivity score with updated timestamp

Below are the main endpoints:

- {BASE_URL}/api/signup/ [POST]
- {BASE_URL}/api/login/ [POST]
- {BASE_URL}/api/file-upload/ [POST] (Token Authentication)
- {BASE_URL}/api/file-listing/ [POST] (Token Authentication)

Only authenticated users can use the API services, for that reason if we try this:
```
http://{BASE_URL}/api/file-upload/ or http://{BASE_URL}/api/file-listing/
```
we get:
```
{
    "detail": "Authentication credentials were not provided."
}
```

After signup, user must login to generate a JWT token

To get a token first we need to request
```
http://{BASE_URL}/api/login/ name="username" password="password"
```
after that, we get the token under data dictionary
```
"data": {
    "token": "{SOME_TOKEN}",
    ...
}
```

To access file upload / file listing API, add token under header:
```
http://{BASE_URL}/api/file-listing/ "Authorization: Token {LOGIN_TOKEN}"
```

## Project Setup

This project is deployed on Amazon Linux 2 machine with Nginx as reverse proxy to Gunicorn application server.
This is linked to a PostgreSQL RDS instance.

## Requirements
- Python 3.7.9
- Django 3.2.3
- Django REST Framework 3.12.4
- Gunicorn 20.1.0

(other packages...)

## Installation
After cloning the repository, create a virtual environment since the default python version is 2.7 
You can do this by running the command
```
sudo pip3 install virtualenv
cd file-sensitivity
virtualenv fsesenv
```

After this, activate the virtual environment with
```
source fsesenv/bin/activate
```

Install all the required dependencies by running below command. 
Comment out psycopg2 first if PostgreSQL is not yet installed
```
pip install -r requirements.txt
```

Installation of PostgreSQL-related packages
```
sudo yum install postgresql postgresql-contrib postgresql-devel
sudo yum install python3-devel
sudo yum install gcc
```

Changes in fsesite/settings.py file
- create secret_key.txt file in root folder and paste SECRET_KEY there
- allowed_hosts: add domain name
- database: change settings (engine to django.db.backends.postgresql_psycopg2)

Running migrations for the first time:
Make sure there is a migrations folder with __init__.py file in fapi dir
Comment out path('api/', include('fapi.urls')) in fsesite/urls.py
```
python manage.py makemigrations
python manage.py migrate
```

Create static folder to store all static assets:
```
python manage.py collectstatic
```

Create gunicorn service under systemd. 
Gunicorn sock file should be in root folder after this step
```
sudo vim /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/file-sensitivity
ExecStart=/home/ec2-user/file-sensitivity/fsesenv/bin/gunicorn --access-logfile - --error-logfile /home/ec2-user/file-sensitivity/gunicorn-error.log --workers 3 --timeout 300 --bind unix:/home/ec2-user/file-sensitivity/gunicorn.sock fsesite.wsgi:application

[Install]
WantedBy=multi-user.target

sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
sudo systemctl daemon-reload
```

Nginx configuration
- create sub folder(sites-enabled) under /etc/nginx with below nginx.conf:
```
server {
        listen 80;
        server_name {DOMAIN_NAME};
        root /home/ec2-user/file-sensitivity;

        client_max_body_size 100M;
        location = /favicon.ico {access_log off; log_not_found off;}
        location /static {
                alias /home/ec2-user/file-sensitivity/static/;
        }
        location /media {
                alias /home/ec2-user/file-sensitivity/media/;
        }
        location / {
                proxy_set_header Host $host;
                proxy_pass http://unix:/home/ec2-user/file-sensitivity/gunicorn.sock;
                autoindex_localtime on;
        }
}

sudo nginx -t
sudo systemctl restart nginx
```

Setup RabbitMQ server with Celery
- Manual Installation of erlang and rabbitmq
- check port 5672 open
- Daemonize celeryd / celerybeat (periodic)
- Under fsesite/celery.py, add below
```
app = Celery('fsesite')
app.config_from_object('django.conf:settings')
app.conf.BROKER_URL = "amqp://user:password@domain:5672"
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
```