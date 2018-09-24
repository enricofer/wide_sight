from rest_framework import serializers
from .models import sequences, panoramas, image_object_types, image_objects, userkeys


class sequences_serializer(serializers.ModelSerializer):#HyperlinkedModelSerializer ModelSerializer

    creator = serializers.SlugRelatedField(queryset=userkeys.objects.all(), slug_field='key') #serializers.PrimaryKeyRelatedField(queryset=userkeys.objects.all())

    class Meta:
        model = sequences
        fields = ('uiid', 'geom', 'shooting_data', 'creator','note','pk')


class panoramas_serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = panoramas
        fields = ('uiid', 'eqimage', 'geom', 'sequence', 'lon', 'lat', 'elevation', 'accurancy', 'heading', 'pitch', 'roll', 'address', 'note','pk')

class image_object_types_serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = image_object_types
        fields = ('type','pk')

class image_objects_serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = image_objects
        fields = ('uiid', 'type', 'panorama', 'match', 'img_lat', 'img_lon', 'width', 'height', 'lon', 'lat', 'elevation', 'accurancy', 'sample_type', 'note', 'user_data', 'sampling_data', 'creator','pk')

class userkeys_serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = userkeys
        fields = ('user', 'key', 'pk', 'context')
