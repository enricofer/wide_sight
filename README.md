# WIDESIGHT backend

This is the backend component of Widesight Service application.
It is a django app based on [Django REST Framework](https://www.django-rest-framework.org/) that exposes a REST interface for creating and mantaining a street level  images and derived objects database

## Install:

Manually install GDAL and related python library for your platform.
local clone the repository than install the remaining needed python library requirements:

```
pip install -r requirements.txt
```

configure `ws/settings.py` specifying database backend (demo on spatialite backend) then migrate database from scratch.

```
python manage.py makemigrations wide_sight

python manage.py migrate
```

run development service:

```
python manage.py runserver
```

## REST API interface

The service manage listing , creation and editing of three five sets of objects:

- main

  - sequences: panorama containers

  - panoramas: geolocated equirectangular images with support informations

  - image objects: geolocated user recognized image objects (tags, spots, stereo measurements, etc...)

- support

  - image objects types: custom image objects categories

  - userkey: userkeys user capabilities (geofencing, allowed appkeys)

  - appkeys: allowed application keys (needed for GET method without user authorization)

the complete API reference is available at [docs/API.html](https://app.swaggerhub.com/apis-docs/enricofer/Widesight/1.0.0)
