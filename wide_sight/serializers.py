
import sys
import utm
from rest_framework import serializers
from django.contrib.gis.geos import GEOSGeometry, Point
from rest_framework.reverse import reverse
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import sequences, panoramas, image_object_types, image_objects, userkeys

class sequences_serializer(serializers.ModelSerializer):#HyperlinkedModelSerializer ModelSerializer

    creator = serializers.PrimaryKeyRelatedField(queryset=userkeys.objects.all()) #HyperlinkedRelatedField(queryset=userkeys.objects.all(),view_name='sequencesViewSet') #serializers.PrimaryKeyRelatedField(queryset=userkeys.objects.all())
    class Meta:
        model = sequences
        read_only_fields = ('id', 'geom', 'shooting_data',)
        geo_field = "geom"
        fields = ('id', 'title', 'geom', 'shooting_data', 'creator', 'note')


class panoramas_serializer(serializers.ModelSerializer):
    #utm_geom = serializers.SerializerMethodField()
    def get_utm_geom(self,obj):
        if obj.lon and obj.lat:
            utm_srid = get_utm_srid_from_lonlat(obj.lon,obj.lat)
            utm_easting, utm_northing, utm_zone_number, utm_letter = utm.from_latlon(obj.lon,obj.lat)
            wgs84_geom =  GEOSGeometry(Point(utm_easting, utm_northing, srid=utm_srid), srid=utm_srid)
            return wgs84_geom.ewkt #wgs84_geom.transform(get_utm_srid_from_lonlat(obj.lon,obj.lat)).geojson
        else:
            return None

    creator = serializers.SerializerMethodField()
    def get_creator(self,obj):
        return obj.sequence.creator.pk

    height_from_ground = serializers.SerializerMethodField()
    def get_height_from_ground(self,obj):
        return obj.sequence.height_from_ground

    class Meta:
        model = panoramas
        read_only_fields = ('id', 'utm_x', 'utm_y', 'utm_srid', 'utm_code', 'camera_prod', 'camera_model',)
        fields = (
            'id',
            'eqimage',
            #'eqimage_thumbnail',
            'geom',
            #'utm_geom',
            'sequence',
            'creator',
            'shooting_time',
            'lon',
            'lat',
            'utm_x',
            'utm_y',
            'utm_srid',
            'utm_code',
            'elevation',
            'accurancy',
            'heading',
            'height_from_ground',
            'pitch',
            'roll',
            'fov',
            'camera_prod',
            'camera_model',
            'address',
            'note'
        )

class panoramas_geo_serializer(GeoFeatureModelSerializer):

    creator = serializers.SerializerMethodField()
    def get_creator(self,obj):
        return obj.sequence.creator.pk

    class Meta:
        model = panoramas
        geo_field = "geom"
        fields = (
            'id',
            'eqimage',
            #'eqimage_thumbnail',
            'geom',
            'sequence',
            'creator',
            'lon',
            'lat',
            'utm_x',
            'utm_y',
            'utm_srid',
            'utm_code',
            'elevation',
            'accurancy',
            'heading',
            'pitch',
            'roll',
            'fov',
            'camera_prod',
            'camera_model',
            'address',
            'note'
        )

class image_object_types_serializer(serializers.ModelSerializer):
    class Meta:
        model = image_object_types
        fields = ('type','pk')

class image_objects_serializer(serializers.ModelSerializer):
    class Meta:
        model = image_objects
        fields = ('id', 'type', 'panorama', 'match', 'img_lat', 'img_lon', 'width', 'height', 'lon', 'lat', 'elevation', 'accurancy', 'sample_type', 'note', 'user_data', 'sampling_data', 'creator')

class userkeys_serializer(serializers.ModelSerializer):
    class Meta:
        model = userkeys
        fields = ('user', 'key', 'app_keys', 'pk', 'context')
