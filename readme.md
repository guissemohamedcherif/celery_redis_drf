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

  <h3 align="center">redis_celery_django_api</h3>

  <p align="center">
    A small project to test Celery + Redis on django.
    <br />
  </p>
</div>


<!-- ABOUT THE PROJECT -->

## About The Project

Celery + Redis on django
<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

- [Django](https://www.djangoproject.com/)
- [djangorestframework](https://pypi.org/project/djangorestframework/)
- [djangorestframework-jwt](https://jpadilla.github.io/django-rest-framework-jwt/)
- [django-cors-headers](https://pypi.org/project/django-cors-headers/)
- [python-dotenv](https://pypi.org/project/dotenv-python/)
- [python-dateutil](https://pypi.org/project/python-dateutil/)
- [requests](https://pypi.org/project/requests/)
- [redis](https://pypi.org/project/redis/)
- [django-redis](https://pypi.org/project/django-redis/)
- [celery](https://pypi.org/project/celery/)
- [django-celery-results](https://pypi.org/project/django-celery-results/)
- [django-celery-beat](https://pypi.org/project/django-celery-beat/)




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


## CELERY
### This app comes with Celery.

To run a celery worker:
  ```sh
  celery -A backend worker -l info
  ```


To run a celery beat:
  ```sh
  celery -A backend beat -l INFO
  ```
