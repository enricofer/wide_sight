import uuid
import os
import exifread
import sys
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.gis.geos import Point
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.helpers import generate_key

def validate_file_extension(value):
    if not (value.file.content_type == 'image/png' or value.file.content_type == 'image/jpeg'):
        raise ValidationError(u'File not allowed: invalid extension')

class sequences(models.Model):
    uiid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    geom = models.LineStringField(srid=4326, blank=True, null=True)
    shooting_data = models.DateField(default=datetime.date.today, blank=True)
    creator = models.ForeignKey('userkeys', on_delete=models.PROTECT)
    note = models.CharField(max_length=50,blank=True)

    class Meta:
        verbose_name_plural = "Sequences"
        verbose_name = "Sequence"
        app_label = 'wide_sight'

@receiver(pre_delete, sender=sequences)
def delete_panorama(sender, instance, **kwargs):
    os.rmdir(os.path.join(settings.MEDIA_ROOT,instance.uuid))

class panoramas(models.Model):

    def upload_img(instance, filename):
        path = "panos/%s" % str(instance.sequence.uiid)
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT,path)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT,path))
        return os.path.join(path, filename)

    uiid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    eqimage = models.ImageField(upload_to=upload_img)
    eqimage_thumbnail = ImageSpecField(source='eqimage',
                                      processors=[ResizeToFill(480, 240)],
                                      format='JPEG',
                                      options={'quality': 60})
    geom = models.PointField(srid=4326, blank=True, null=True, geography=True)
    sequence = models.ForeignKey('sequences', on_delete=models.PROTECT)
    lon = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    elevation = models.FloatField(blank=True, null=True)
    accurancy = models.FloatField(blank=True, null=True)
    heading = models.FloatField(blank=True, null=True)
    pitch = models.FloatField(blank=True, null=True)
    roll = models.FloatField(blank=True, null=True)
    fov = models.FloatField(blank=True, null=True)
    camera_prod = models.CharField(max_length=50,blank=True)
    camera_model = models.CharField(max_length=50,blank=True)
    address = models.CharField(max_length=150,blank=True)
    note = models.CharField(max_length=50,blank=True)
    shooting_time = models.DateTimeField(default=datetime.datetime.now, blank=True)

    class Meta:
        verbose_name_plural = "Panoramas"
        verbose_name = "Panorama"
        app_label = 'wide_sight'

@receiver(post_save, sender=panoramas)
def sync_geom(sender, instance,  **kwargs):
    update_fields = kwargs["update_fields"]
    created = kwargs["created"]
    print ("instance",instance, file=sys.stderr)
    print ("kwargs",kwargs, file=sys.stderr)
    print ("update_fields",update_fields, file=sys.stderr)

    if created or update_fields:
        if created or 'eqimage' in update_fields:
            f = open(os.path.join(settings.MEDIA_ROOT,instance.eqimage), 'rb')
            print ("eqimage",os.path.join(settings.MEDIA_ROOT,instance.eqimage), file=sys.stderr)
            exiftags = exifread.process_file(f)
            print ("EXIFTAGS",exiftags, file=sys.stderr)
        if 'lon' in update_fields or 'lat' in update_fields:
            instance.geom = Point(instance.lon,instance.lat)
            instance.save()

@receiver(pre_delete, sender=panoramas)
def delete_panorama(sender, instance, **kwargs):
    os.remove(os.path.join(settings.MEDIA_ROOT,instance.eqimage))


class image_object_types(models.Model):
    type = models.CharField(max_length=20,blank=True)

    class Meta:
        verbose_name_plural = "Image_object_types"
        verbose_name = "Image_object_type"

class image_objects(models.Model):

    sample_type_choice = (
        (1,'panorama sampling'),
        (2,'road intersection'),
        (3,'map positioning'),
        (4,'stereo interpretation'),
    )

    uiid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.ForeignKey('image_object_types', on_delete=models.PROTECT)
    panorama = models.ForeignKey('panoramas', on_delete=models.CASCADE)
    match = models.ManyToManyField("self")
    img_lat = models.IntegerField()
    img_lon = models.IntegerField()
    width = models.IntegerField(blank=True)
    height = models.IntegerField(blank=True)
    lon = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    elevation = models.FloatField(blank=True, null=True)
    accurancy = models.FloatField(blank=True, null=True)
    sample_type = models.IntegerField(choices=sample_type_choice)
    note = models.CharField(max_length=50,blank=True)
    user_data = models.TextField(blank=True) #user data json store
    sampling_data = models.DateField()
    creator = models.ForeignKey('userkeys', on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Image_objects"
        verbose_name = "Image_object"
        app_label = 'wide_sight'

class appkeys(models.Model):
    app_name = models.CharField(max_length=50)
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_key = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Appkeys"
        verbose_name = "Appkey"
        app_label = 'wide_sight'

class userkeys(models.Model):
    '''
    https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    app_keys = models.ManyToManyField(appkeys)
    context = models.MultiPolygonField(srid=4326, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Userkeys"
        verbose_name = "Userkey"
        app_label = 'wide_sight'

@receiver(post_save, sender=appkeys)
def get_APIkey(sender, instance,  **kwargs):
    created = kwargs["created"]
    if created:
        instance.api_key = APIKey.objects.create(name=instance.app_name, key=generate_key()).key
        instance.save()
