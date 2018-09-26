import sys

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIAccess

from .models import sequences, panoramas, image_object_types, image_objects, userkeys
from .serializers import sequences_serializer, panoramas_serializer, image_object_types_serializer, image_objects_serializer, userkeys_serializer

class sequencesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = sequences.objects.all()
    serializer_class = sequences_serializer
    permission_classes = (IsAuthenticated,)

class panoramasViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = panoramas.objects.all()
    serializer_class = panoramas_serializer
    permission_classes = (IsAuthenticated, )


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print ("instance",instance, file=sys.stderr)
        print ("args",instance, file=sys.stderr)
        print ("kwargs",instance, file=sys.stderr)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def __destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            pass


class image_object_typesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = image_object_types.objects.all()
    serializer_class = image_object_types_serializer
    permission_classes = (IsAuthenticated, )

class image_objectsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = image_objects.objects.all()
    serializer_class = image_objects_serializer
    permission_classes = (IsAuthenticated, )

class userkeysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = userkeys.objects.all()
    serializer_class = userkeys_serializer
    permission_classes = (IsAuthenticated, )
