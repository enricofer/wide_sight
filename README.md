# WIDESIGHT backend

This is the backend component of Widesight Service application.
It is a django app based on [Django REST Framework](https://www.django-rest-framework.org/) that exposes a REST interface for creating and mantaining a street level  images and derived objects database

## WIDESIGHT Web interface
https://github.com/enricofer/wide_sight_frontend

## Uploading utilities
https://github.com/enricofer/wide_sight_utils

## Install:

Manually install GDAL and related python library for your platform. GDAL version and related python bindings version must be the same.
```
sudo add-apt-repository ppa:ubuntugis/ppa
sudo apt-get update
sudo apt install gdal-bin=3.0.4
pip install GDAL==3.0.4
```

local clone the repository than install the remaining needed python library requirements:

```
pip install -r requirements.txt
```
In order to run the application a geodatabase must be installed, spatialite for testing and development postgis for production
configure `ws/settings.py` specifying database backend (demo on spatialite backend) then migrate database from scratch.

```
python manage.py migrate
```

Create an admin user

```
python manage.py createsuperuser
```

run development service (by default localhost on port 8000):

```
python manage.py runserver
```

## REST API interface

The service manage listing , creation and editing of three five sets of objects:

http://localhost:8000/

- main

  - sequences: panorama containers

  - panoramas: geolocated equirectangular images with support informations

  - image objects: geolocated user recognized image objects (tags, spots, stereo measurements, etc...)

- support

  - image objects types: custom image objects categories

  - userkey: userkeys user capabilities (geofencing, allowed appkeys)

  - appkeys: allowed application keys (needed for GET method without user authorization)

the complete API reference is available at [docs/API.html](https://app.swaggerhub.com/apis-docs/enricofer/Widesight/1.0.0)

## ADMIN interface

Authenticate as the previously defined user and point to http://localhost:8000/admin

With the Admin interface is possible to load equirectangular images with the following workflow:

- define an appkey: http://10.10.21.50:8000/admin/wide_sight/appkeys/add/
- define a userker: http://10.10.21.50:8000/admin/wide_sight/userkeys/add/
- define a sequence: http://10.10.21.50:8000/admin/wide_sight/sequences/add/
- then manually load the panorama images: http://10.10.21.50:8000/admin/wide_sight/panoramas/add/

The image parameters (gps location, heading, pitch and roll) can be manually inserted or taken from EXIF tags if defined
For massive insertion of images make use of https://github.com/enricofer/wide_sight_utils uploading util

## integrated equirectangular viewer (https://github.com/enricofer/wide_sight_frontend)

The web interface include a build of the equirectangular widesight web viewer:

http://localhost:8000/viewer/
http://localhost:8000/viewer/[panorama id]