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
from dirtyfields import DirtyFieldsMixin

from .exif_gps import get_exif_values, set_heading_tag



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

    def __str__(self):
        return '%d_%s' % (self.uiid,self.title)

@receiver(pre_delete, sender=sequences)
def delete_sequence(sender, instance, **kwargs):
    os.rmdir(os.path.join(settings.MEDIA_ROOT,instance.uuid))

class panoramas(DirtyFieldsMixin, models.Model):

    def upload_img(instance, filename):
        name, file_extension = os.path.splitext(filename)
        f_name = str(instance.uiid)+file_extension
        rel_path = os.path.join("panos",str(instance.sequence.uiid))
        os_path = os.path.join(settings.MEDIA_ROOT,rel_path)
        if not os.path.exists(os_path):
            os.makedirs(os_path)
        return os.path.join(rel_path, f_name)

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
    camera_prod = models.CharField(max_length=50,blank=True, null=True)
    camera_model = models.CharField(max_length=50,blank=True, null=True)
    address = models.CharField(max_length=150,blank=True)
    note = models.CharField(max_length=50,blank=True)
    shooting_time = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Panoramas"
        verbose_name = "Panorama"
        app_label = 'wide_sight'

    def save(self, *args, **kwargs):
        for key, value in kwargs.items():
            print ("%s == %s" %(key, value))
        print ("dirty_fields",self.get_dirty_fields(), file=sys.stderr)
        if self.heading and'heading' in self.get_dirty_fields():
            set_heading_tag(os.path.join(settings.MEDIA_ROOT,self.eqimage.path),self.heading)
        if 'eqimage' in self.get_dirty_fields():
            exiftags = exifread.process_file(self.eqimage)
            print ("EXIFTAGS",exiftags, file=sys.stderr)
            self.lat, self.lon, self.elevation, self.heading, self.pitch, self.roll, self.fov, self.camera_prod, self.camera_model, self.shooting_time  = get_exif_values(exiftags)
        if (self.lon and 'lon' in self.get_dirty_fields()) or (self.lat and 'lat' in self.get_dirty_fields()):
            self.geom = Point(self.lon,self.lat)
        super(panoramas,self).save(*args, **kwargs)

#@receiver(post_save, sender=panoramas)
def sync_geom(sender, instance,  **kwargs):
    update_fields = instance.get_dirty_fields()
    created = kwargs["created"]
    print ("instance",instance, file=sys.stderr)
    print ("instance.eqimage",instance.eqimage, file=sys.stderr)
    print ("dirty_fields",instance.get_dirty_fields(), file=sys.stderr)

    if created or update_fields:
        if created or 'eqimage' in update_fields:
            exiftags = exifread.process_file(instance.eqimage)
            print ("EXIFTAGS",exiftags, file=sys.stderr)
            instance.lat, instance.lon, instance.elevation, instance.heading, instance.pitch, instance.roll, instance.fov, instance.camera_prod, instance.camera_model  = get_exif_values(exiftags)
            instance.save()
        if update_fields and ('lon' in update_fields or 'lat' in update_fields):
            self.geom = Point(self.lon,self.lat)
            instance.save()

@receiver(pre_delete, sender=panoramas)
def delete_panorama(sender, instance, **kwargs):
    print ("REMOVING",instance.eqimage.name, file=sys.stderr)
    os.remove(os.path.join(settings.MEDIA_ROOT,instance.eqimage.name))


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

    def __str__(self):
        return '%s_%s' % (self.app_name,self.api_key)

@receiver(post_save, sender=appkeys)
def get_APIkey(sender, instance,  **kwargs):
    created = kwargs["created"]
    if created:
        instance.api_key = APIKey.objects.create(name=instance.app_name, key=generate_key()).key
        instance.save()

'''
@receiver(post_save, sender=appkeys)
def get_APIkey(sender, instance,  **kwargs):
    created = kwargs["created"]
    if created:
        instance.api_key = APIKey.objects.create(name=instance.app_name, key=generate_key()).key
        instance.save()
'''

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

    def __str__(self):
        return '%d_%s' % (self.key,self.user)
