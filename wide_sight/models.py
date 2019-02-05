import uuid
import os
import exifread
import sys
import datetime
import utm

from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry, LineString, MultiPoint
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.gis.geos import Point
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.helpers import generate_key
from dirtyfields import DirtyFieldsMixin
from django.utils.translation import ugettext_lazy as _ 

from .exif_gps import get_exif_values, set_heading_tag
from .utils import get_utm_srid_from_lonlat


sample_type_choice = (
    (1,'tag'),
    (2,'map spot'),
    (3,'stereo interpretation'),
    (4,'visual intersection'),
)

def validate_file_extension(value):
    if value.file.content_type == 'image/jpeg':
        raise ValidationError(u'File not allowed: invalid extension')

class sequences(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text=_("unique alphanumeric identifier"))
    title = models.CharField(max_length=50, help_text=_("sequence title string"))
    geom = models.MultiPointField(srid=4326, blank=True, null=True, help_text=_("geometry containing all related panorama positions"))
    shooting_data = models.DateField(default=datetime.date.today, blank=True, help_text=_("date of shooting (default today)"))
    height_from_ground = models.FloatField(blank=True, null=True, default=2, help_text=_("height from the ground of the camera. can be overidden in single panorama setting"))
    creator_key = models.ForeignKey('userkeys', on_delete=models.PROTECT, help_text=_("the userkey of the sequence creator"))
    note = models.CharField(max_length=50,blank=True, help_text=_("free notes about the sequence"))

    class Meta:
        verbose_name_plural = "Sequences"
        verbose_name = "Sequence"
        app_label = 'wide_sight'
        ordering = ['shooting_data']

    def __str__(self):
        return '%s_%s' % (str(self.id),self.title)

@receiver(pre_delete, sender=sequences)
def delete_sequence(sender, instance, **kwargs):
    os.rmdir(os.path.join(settings.MEDIA_ROOT,'panos',str(instance.id)))

class panoramas(DirtyFieldsMixin, models.Model):

    def upload_img(instance, filename):
        name, file_extension = os.path.splitext(filename)
        f_name = str(instance.id)+file_extension
        rel_path = os.path.join("panos",str(instance.sequence.id))
        os_path = os.path.join(settings.MEDIA_ROOT,rel_path)
        if not os.path.exists(os_path):
            os.makedirs(os_path)
        return os.path.join(rel_path, f_name)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text=_("unique alphanumeric identifier"))
    eqimage = models.ImageField(upload_to=upload_img, help_text=_("equirectangular image path"))
    eqimage_thumbnail = ImageSpecField(source='eqimage',
                                      processors=[ResizeToFill(480, 240)],
                                      format='JPEG',
                                      options={'quality': 60})
    geom = models.PointField(srid=4326, blank=True, null=True, geography=True, help_text=_("geometry location of the panorama"))
    sequence = models.ForeignKey('sequences', on_delete=models.CASCADE, help_text=_("sequence id to which panorama belongs"))
    lon = models.FloatField(blank=True, null=True, help_text=_("decimal longitude of the panorama"))
    lat = models.FloatField(blank=True, null=True, help_text=_("decimal latitude of the panorama"))
    utm_x = models.FloatField(blank=True, null=True, help_text=_("UTM projected coordinate x in meters"))
    utm_y = models.FloatField(blank=True, null=True, help_text=_("UTM projected coordinate y in meters"))
    utm_code = models.CharField(max_length=3,blank=True, help_text=_("UTM zone code"))
    utm_srid = models.IntegerField(blank=True, null=True, help_text=_("UTM srid code"))
    elevation = models.FloatField(blank=True, null=True, help_text=_("elevation over the sealevel of the panorama location"))
    accurancy = models.FloatField(blank=True, null=True, help_text=_("accurancy of theh panorama location"))
    heading = models.FloatField(blank=True, null=True, help_text=_("heading of the camera expressed in clockwise decimal degrees from north"))
    pitch = models.FloatField(blank=True, null=True, help_text=_("pitch angle of the camera"))
    roll = models.FloatField(blank=True, null=True, help_text=_("roll angle of the camera"))
    fov = models.FloatField(blank=True, null=True, help_text=_("Field of view of the camera"))
    camera_prod = models.CharField(max_length=50,blank=True, null=True, help_text=_("Camera producer (from EXIF)"))
    camera_model = models.CharField(max_length=50,blank=True, null=True, help_text=_("Camera model (from EXIF)"))
    address = models.CharField(max_length=150,blank=True, help_text=_("Geolocated address (not yet implemented)"))
    note = models.CharField(max_length=50,blank=True, help_text=_("Free text annotation on panorama"))
    shooting_time = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True, help_text=_("Datetime instant of panorama shot"))
    height_correction = models.FloatField(blank=True, null=True, help_text=_("Correction of sequence height from ground"))

    class Meta:
        verbose_name_plural = "Panoramas"
        verbose_name = "Panorama"
        app_label = 'wide_sight'
        ordering = ['shooting_time']

    def save(self, *args, **kwargs):
        for key, value in kwargs.items():
            print ("%s == %s" %(key, value))
        print ("dirty_fields",self.get_dirty_fields(), file=sys.stderr)
        if self.heading and'heading' in self.get_dirty_fields():
            pass #following method throws exception
            #set_heading_tag(os.path.join(settings.MEDIA_ROOT,self.eqimage.path),self.heading)
        if 'eqimage' in self.get_dirty_fields():
            exiftags = exifread.process_file(self.eqimage)
            print ("EXIFTAGS",exiftags, file=sys.stderr)
            self.lat, self.lon, self.elevation, self.heading, self.pitch, self.roll, self.fov, self.camera_prod, self.camera_model, self.shooting_time  = get_exif_values(exiftags)
        if (self.lon and 'lon' in self.get_dirty_fields()) or (self.lat and 'lat' in self.get_dirty_fields()):
            self.geom = Point(self.lon,self.lat)
            self.utm_srid = get_utm_srid_from_lonlat(self.lon,self.lat)
            self.utm_x, self.utm_y, utm_zone_number, utm_letter = utm.from_latlon(self.lat,self.lon)
            self.utm_code = str(utm_zone_number)+utm_letter

        super(panoramas,self).save(*args, **kwargs)
        update_sequence(self.sequence)
        #if (self.lon and 'lon' in self.get_dirty_fields()) or (self.lat and 'lat' in self.get_dirty_fields()):


def update_sequence(seq, exclude=None):
    imgs_in_sequence = panoramas.objects.filter(sequence=seq).order_by('shooting_time')
    seq_points = []
    for img in imgs_in_sequence:
        if exclude and img.pk == exclude.pk:
            pass
        else:
            seq_points.append(img.geom)

    cloud = MultiPoint(seq_points)
    seq.geom = GEOSGeometry(cloud, srid=4326)
    seq.save()

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
            self.geom = Point(self.lon,self.lat, srid=4326)
            instance.save()

@receiver(pre_delete, sender=panoramas)
def delete_panorama(sender, instance, **kwargs):
    print ("REMOVING",instance.eqimage.name, file=sys.stderr)
    try:
        os.remove(os.path.join(settings.MEDIA_ROOT,instance.eqimage.name))
        update_sequence(instance.sequence, exclude=instance)
    except Exception as e:
        print ("error: ", e, file=sys.stderr)

class image_object_types(models.Model):
    type = models.CharField(max_length=20,blank=True)
    for_type = models.IntegerField(choices=sample_type_choice)
    color = models.CharField(max_length=20,blank=True)

    class Meta:
        verbose_name_plural = "Image_object_types"
        verbose_name = "Image_object_type"

class image_objects(DirtyFieldsMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text=_("unique alphanumeric identifier"))
    sample_type = models.ForeignKey('image_object_types', on_delete=models.PROTECT,blank=True, null=True, help_text=_("User-defined Image object type"))
    type = models.IntegerField(choices=sample_type_choice, help_text=_("Application image object type (1:tag, 2:map_spot, 3:stereo interpretation, 4:visual intersection, ... more will come)"))
    panorama = models.ForeignKey('panoramas', on_delete=models.CASCADE, help_text=_("Panorama id to which image object belongs "))
    match = models.ManyToManyField("self",blank=True, help_text=_("matching id of other related image objects (not yet used)"))
    img_lat = models.FloatField(blank=True, null=True, help_text=_("image object latitude on equirectangular panorama image"))
    img_lon = models.FloatField(blank=True, null=True, help_text=_("image object longitude on equirectangular panorama image"))
    geom_on_panorama = models.TextField(blank=True, help_text=_("geometry trace of image object as array of longitude/latitude points on equirectangular panorama image")) #jsonfield representing a geometry traced on panorama
    width = models.IntegerField(blank=True, null=True, help_text=_("graphic width of image object"))
    height = models.IntegerField(blank=True, null=True, help_text=_("height from ground of geo-located image object"))
    lon = models.FloatField(blank=True, null=True, help_text=_("longitude of geo-located image object"))
    lat = models.FloatField(blank=True, null=True, help_text=_("latitude of geo-located image object"))
    utm_x = models.FloatField(blank=True, null=True, help_text=_("UTM projected x of geo-located image object"))
    utm_y = models.FloatField(blank=True, null=True, help_text=_("UTM projected y of geo-located image object"))
    utm_code = models.CharField(max_length=3,blank=True, help_text=_("UTM zone code related to geo-located image object position"))
    utm_srid = models.IntegerField(blank=True, null=True, help_text=_("UTM srid related to geo-located image object position"))
    elevation = models.FloatField(blank=True, null=True, help_text=_("elevation from sea level of geo-located image object"))
    accurancy = models.FloatField(blank=True, null=True, help_text=_("accurancy of geo-located image object position"))
    note = models.CharField(max_length=50,blank=True, help_text=_("User textual notes on image object"))
    user_data = models.TextField(blank=True, help_text=_("json field structured user data related to image object (not yet implemented)")) #user data json store
    sampling_data = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True, help_text=_("Datetime instant of image object recognition"))
    creator_key = models.ForeignKey('userkeys', on_delete=models.CASCADE, help_text=_("Userkey id of the of image object creator"))
    geom = models.PointField(srid=4326, blank=True, null=True, geography=True, help_text=_("Point Geometry of geo-located image object"))

    class Meta:
        verbose_name_plural = "Image_objects"
        verbose_name = "Image_object"
        app_label = 'wide_sight'

    def save(self, *args, **kwargs):
        if self.type == 2:
            self.geom = Point(self.lon,self.lat)
        else:
            self.geom = GEOSGeometry('POINT EMPTY', srid=4326)
        super(image_objects,self).save(*args, **kwargs)


class appkeys(models.Model):
    app_name = models.CharField(max_length=50, help_text=_("Name of the sallowed application"))
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text=_("unique alphanumeric identifier"))
    api_key = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Appkeys"
        verbose_name = "Appkey"
        app_label = 'wide_sight'

    def __str__(self):
        return '%s_%s' % (self.app_name,self.key)

@receiver(post_save, sender=appkeys)
def get_APIkey(sender, instance,  **kwargs):
    created = kwargs["created"]
    if created:
        instance.api_key = APIKey.objects.create(name=instance.app_name, key=generate_key()).key
        instance.save()

class userkeys(models.Model):
    '''
    https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text=_("User id to which the userkey is related"))
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text=_("unique alphanumeric identifier"))
    app_keys = models.ManyToManyField(appkeys, help_text=_("Application key authorized related to the userkey"))
    context = models.MultiPolygonField(srid=4326, null=True, blank=True, help_text=_("geometry of polygonal context in which userkey can operate on service"))

    class Meta:
        verbose_name_plural = "Userkeys"
        verbose_name = "Userkey"
        app_label = 'wide_sight'

    def __str__(self):
        return '%s_%s' % (str(self.key),self.user)
