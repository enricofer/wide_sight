from django.shortcuts import render
from rest_framework import viewsets

from .models import sequences, panoramas, image_object_types, image_objects, userkeys
from .serializers import sequences_serializer, panoramas_serializer, image_object_types_serializer, image_objects_serializer, userkeys_serializer

class sequencesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = sequences.objects.all()
    serializer_class = sequences_serializer

class panoramasViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = panoramas.objects.all()
    serializer_class = panoramas_serializer

class image_object_typesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = image_object_types.objects.all()
    serializer_class = image_object_types_serializer

class image_objectsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = image_objects.objects.all()
    serializer_class = image_objects_serializer

class userkeysViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = userkeys.objects.all()
    serializer_class = userkeys_serializer