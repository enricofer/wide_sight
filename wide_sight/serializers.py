from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import sequences, panoramas, image_object_types, image_objects, userkeys

class sequences_serializer(serializers.ModelSerializer):#HyperlinkedModelSerializer ModelSerializer

    creator = serializers.PrimaryKeyRelatedField(queryset=userkeys.objects.all()) #HyperlinkedRelatedField(queryset=userkeys.objects.all(),view_name='sequencesViewSet') #serializers.PrimaryKeyRelatedField(queryset=userkeys.objects.all())
    class Meta:
        model = sequences
        geo_field = "geom"
        fields = ('id', 'geom', 'shooting_data', 'creator','note')


class panoramas_serializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()

    def get_creator(self,obj):
        return obj.sequence.creator.pk

    class Meta:
        model = panoramas
        fields = ('id', 'eqimage', 'geom', 'sequence', 'creator', 'lon', 'lat', 'elevation', 'accurancy', 'heading', 'pitch', 'roll', 'fov', 'camera_prod', 'camera_model', 'address', 'note')

class panoramas_geo_serializer(GeoFeatureModelSerializer):
    class Meta:
        model = panoramas
        geo_field = "geom"
        fields = ('id', 'eqimage', 'sequence', 'elevation', 'accurancy', 'heading', 'pitch', 'roll', 'fov', 'camera_prod', 'camera_model', 'address', 'note')

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
