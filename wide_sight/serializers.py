
import sys
import utm
from rest_framework import serializers
from django.contrib.gis.geos import GEOSGeometry, Point
from rest_framework.reverse import reverse
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import sequences, panoramas, image_object_types, image_objects, userkeys, appkeys

class sequences_serializer(serializers.ModelSerializer):#HyperlinkedModelSerializer ModelSerializer

    class Meta:
        model = sequences
        read_only_fields = ('id', 'geom', 'shooting_data', 'creator')
        geo_field = "geom"
        fields = ('id', 'title', 'geom', 'shooting_data', 'creator_key', 'note')
        extra_kwargs = {
            'creator_key': {'write_only': True},
        }


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

    #creator = serializers.SerializerMethodField()
    #def get_creator(self,obj):
    #    return obj.sequence.creator.pk

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
            #'creator',
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

    class Meta:
        model = panoramas
        geo_field = "geom"
        fields = (
            'id',
            'eqimage',
            #'eqimage_thumbnail',
            'geom',
            'sequence',
            #'creator',
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
        fields = ('type','pk', 'for_type', 'color')

class image_objects_serializer(serializers.ModelSerializer):
    class Meta:
        model = image_objects
        fields = (
            'id',
            'type' ,
            'creator_key',
            'sample_type',
            'geom_on_panorama',
            'panorama',
            'match',
            'img_lat',
            'img_lon',
            'width',
            'height',
            'lon',
            'lat',
            'utm_x',
            'utm_y',
            'utm_code',
            'utm_srid',
            'elevation',
            'accurancy',
            'note',
            'user_data',
            'sampling_data',
        )
        extra_kwargs = {
            'creator_key': {'write_only': True},
        }

class image_objects_geo_serializer(GeoFeatureModelSerializer):
    class Meta:
        model = image_objects
        geo_field = "geom"
        fields = (
            'id',
            'type' ,
            'creator_key',
            'sample_type',
            'geom_on_panorama',
            'panorama',
            'match',
            'img_lat',
            'img_lon',
            'width',
            'height',
            'lon',
            'lat',
            'utm_x',
            'utm_y',
            'utm_code',
            'utm_srid',
            'elevation',
            'accurancy',
            'note',
            'user_data',
            'sampling_data',
            'geom',
        )
        extra_kwargs = {
            'creator_key': {'write_only': True},
        }

class userkeys_serializer(serializers.ModelSerializer):
    class Meta:
        model = userkeys
        fields = ('user', 'key', 'app_keys', 'pk', 'context')

class appkeys_serializer(serializers.ModelSerializer):
    class Meta:
        model = appkeys
        fields = ('app_name', 'key', 'api_key')
