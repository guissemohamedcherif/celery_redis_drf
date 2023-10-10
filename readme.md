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
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">CRYPTA DJANGO API</h3>

  <p align="center">
    A project for accountants.
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
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

There are many great README templates available on GitHub; however, I didn't find one that really suited my needs so I created this enhanced one. I want to create a README template so amazing that it'll be the last one you ever need -- I think this is it.

Here's why:

- Your time should be focused on creating something amazing. A project that solves a problem and helps others
- You shouldn't be doing the same tasks over and over like creating a README from scratch
- You should implement DRY principles to the rest of your life :smile:

Of course, no one template will serve all projects since your needs may be different. So I'll be adding more in the near future. You may also suggest changes by forking this repo and creating a pull request or opening an issue. Thanks to all the people have contributed to expanding this template!

Use the `BLANK_README.md` to get started.

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

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.

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
   git clone https://gitlab.com/volkeno/crypta-django.git
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

## Troubleshooting

If there is any problem during the installation of the python package, just install each them one by one using pip install package_name.
The most important packages are django, djangorestframework, djangorestframework-jwt and mixer.

## Docker(for deployment)

<!-- USAGE EXAMPLES -->

```sh
docker-compose -f docker-compose.prod.yml up -d --build
```

```sh
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
```

```sh
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
```

## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme
- [ ] Multi-language Support
  - [ ] Chinese
  - [ ] Spanish

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://gitlab.com/volkeno/crypta-django](https://gitlab.com/volkeno/crypta-django)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

- [django-softdelete](https://choosealicense.com)
- [django-safedelete](https://www.webpagefx.com/tools/emoji-cheat-sheet)
- [reportlab](https://flexbox.malven.co/)
- [uritemplate](https://grid.malven.co/)
- [xhtml2pdf](https://shields.io)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://gitlab.com/volkeno/crypta-django
[contributors-url]: https://gitlab.com/volkeno/crypta-django
[forks-shield]: https://gitlab.com/volkeno/crypta-django
[forks-url]: https://gitlab.com/volkeno/crypta-django
[stars-shield]: https://gitlab.com/volkeno/crypta-django
[stars-url]: https://gitlab.com/volkeno/crypta-django
[issues-shield]: https://gitlab.com/volkeno/crypta-django
[issues-url]: https://gitlab.com/volkeno/crypta-django
[license-shield]: https://gitlab.com/volkeno/crypta-django
[license-url]: https://gitlab.com/volkeno/crypta-django
[linkedin-shield]: https://gitlab.com/volkeno/crypta-django
[linkedin-url]: https://www.linkedin.com/company/volkeno/mycompany
[product-screenshot]: images/screenshot.png
