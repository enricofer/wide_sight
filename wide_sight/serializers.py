from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import sequences, panoramas, image_object_types, image_objects, userkeys

class sequences_serializer(serializers.ModelSerializer):#HyperlinkedModelSerializer ModelSerializer

    creator = serializers.PrimaryKeyRelatedField(queryset=userkeys.objects.all()) #HyperlinkedRelatedField(queryset=userkeys.objects.all(),view_name='sequencesViewSet') #serializers.PrimaryKeyRelatedField(queryset=userkeys.objects.all())

    class Meta:
        model = sequences
        fields = ('uiid', 'geom', 'shooting_data', 'creator','note')


class panoramas_serializer(serializers.ModelSerializer):
    class Meta:
        model = panoramas
        fields = ('uiid', 'eqimage', 'geom', 'sequence', 'lon', 'lat', 'elevation', 'accurancy', 'heading', 'pitch', 'roll', 'address', 'note')

class image_object_types_serializer(serializers.ModelSerializer):
    class Meta:
        model = image_object_types
        fields = ('type','pk')

class image_objects_serializer(serializers.ModelSerializer):
    class Meta:
        model = image_objects
        fields = ('uiid', 'type', 'panorama', 'match', 'img_lat', 'img_lon', 'width', 'height', 'lon', 'lat', 'elevation', 'accurancy', 'sample_type', 'note', 'user_data', 'sampling_data', 'creator')

class userkeys_serializer(serializers.ModelSerializer):
    class Meta:
        model = userkeys
        fields = ('user', 'key', 'app_keys', 'pk', 'context')
