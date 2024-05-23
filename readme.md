<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url] -->

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/VolkenoMakers/MYAPP-django"></a>

  <h3 align="center">MYAPP DJANGO API</h3>

  <p align="center">
    A project for hospitals and medical offices.
    <br />
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#deployments">Deployment</a></li>

  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

[![MYAPP][product-screenshot]](https://MYAPP-app.withvolkeno.com/)
A project for hospitals and medical offices.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

- [Django](https://www.djangoproject.com/)
- [djangorestframework-jwt](https://jpadilla.github.io/django-rest-framework-jwt/)
- [django-jazzmin](https://github.com/farridav/django-jazzmin)
- [django-import-export](https://django-import-export.readthedocs.io/en/latest/)
- [drf-generators](https://pypi.org/project/drf-generators/)
- [exponent-server-sdk](https://github.com/expo-community/expo-server-sdk-python)
- [Pillow](https://pillow.readthedocs.io/en/stable/)
- [psycopg2-binary](https://pypi.org/project/psycopg2-binary/)
- [Django-NGINX-GUNICORN](https://realpython.com/django-nginx-gunicorn/)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

Instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites
List things you need to use the software and how to install them.

#### 1. Install python in function of your system.

For more information about it click link below https://www.python.org/downloads/

#### 2. Create a python environment

The environement setup process depends on your system. Do some research to find out how to do it on OS.

For Ubuntu you can use the following commands

```sh
virtualenv -p python3 env
source env/bin/activate
```

For OS WINDOWS you can use the following commands

```sh
virtualenv -p python3 env
source env/bin/activate
```
### Before installation 
_If you want generate serializers, views and urls respectively in that order_ 
    
    python manage.py generate api --serializers --format apiview --force
    python manage.py generate api --views --format apiview --force
    python manage.py generate api --urls --format apiview --force

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Clone the repo
   ```sh
   git clone https://gitlab.com/volkeno/MYAPP-django.git
   ```
2. Install required python packages

   ```sh
   pip install -r requirements.txt

   ```

3. Apply database migrations
   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Run the app
  ```sh
   python manage.py runserver
   ```

The api should now be running at http://127.0.0.1:8000/

<p align="right">(<a href="#top">back to top</a>)</p>


## DEPLOYMENT

### 1. Configure nginx. Go sur  `/etc/nginx/sites-enabled/` and create a file named `MYAPP-django-dev.conf` and the configuration bellow:
Ici c'est la configuration du nginx à mettre sur le serveur . Le fichier docker-compose.yml est déjà configuré et se trouve à la racine du projet.`5083` est le port dans le fichier dans l'environnement `dev`. En production au lieu  du port `5083`, utiliser le port `5084`

```  server {
       server_name  MYAPP-api.withvokeno.com www.MYAPP-api.withvokeno.com;
       location / {
       proxy_pass http://127.0.0.1:5083;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       client_max_body_size 1000M;
       proxy_connect_timeout 300;
       proxy_send_timeout 300;
       proxy_read_timeout 300;
       uwsgi_read_timeout 300;

   }
}
```

###  2. Install `docker-compose` on your server. Ici c'est au cas oû `docker-compose` ne serait pas isntallé.

    a) sudo curl -L https://github.com/docker/compose/releases/download/1.25.3/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose

    b). sudo chmod +x /usr/local/bin/docker-compose

    c).  `docker-compose --version`

###  3. Clone project and move on dev branch:
Le fichier docker-compose.yml étant déjà configuré donc il faudra cloner le code source en éxécutant ces commandes et suivre les instructions après cette étape
   1. `git clone https://github.com/VolkenoMakers/MYAPP-django`
   2. `cd MYAPP-django`
   3. `git checkout dev`

### 4. Create file `.env` and copy content `.env.example` in your new file `.env`
### 5. Run this command to build the project : `docker-compose -f docker-compose.prod.yml  up -d --build`
### 6. Run test `docker-compose -f docker-compose.prod.yml exec -T web python manage.py test`
### 7. Migrate db `docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate`
### 8. Deploy css `docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic`
### 9. Create admin superuser  `docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser`


## VERSIONNING
### DEV
1. git tag -a dev-1.0 -m "Dev release 1.0"
2. git push origin --tags
### STAGING
1. git tag -a staging-1.0 -m "Staging release 1.0"
2. git push origin --tags
### PRODUCTION
1. git tag -a production-1.0 -m "Production release 1.0"
2. git push origin --tags
