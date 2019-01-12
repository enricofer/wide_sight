import sys
from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_api_key.permissions import HasAPIAccess
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_gis.filters import DistanceToPointFilter, InBBoxFilter
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework.exceptions import APIException
from rest_condition import Or

from .models import sequences, panoramas, image_object_types, image_objects, userkeys, appkeys
from .serializers import (  panoramas_geo_serializer,
                            sequences_serializer,
                            panoramas_serializer,
                            image_object_types_serializer,
                            image_objects_serializer,
                            image_objects_geo_serializer,
                            userkeys_serializer,
                            appkeys_serializer)

from .permissions import baseAPIPermission

#@login_required(login_url='/login/?next=/viewer/')
def viewer(request, pano_id = ''):
    if not pano_id:
        pano_id = "0329a9dd-6c57-4af0-a347-ba1133a6094c"
    return render(request, 'index.html', {'pano_id': pano_id})

class basePagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000

class sequencesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to be view or edit sequences of panorama images.

    get:
    Return a list of all the existing sequences.

    post:
    Create a new sequence instance.

    patch:
    edit and update an existing sequence.

    delete:
    permanently delete an existing empty sequence.
    """
    queryset = sequences.objects.all()
    serializer_class = sequences_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)
    pagination_class = basePagination
    filter_backends = (DjangoFilterBackend,)

class panoramasViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = panoramas.objects.all()
    serializer_class = panoramas_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)
    pagination_class = basePagination
    distance_filter_field = 'geom'
    bbox_filter_field = 'geom'
    filter_backends = (DjangoFilterBackend, DistanceToPointFilter, InBBoxFilter)
    filterset_fields = ('sequence', 'id', )


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print ("instance",instance, file=sys.stderr)
        print ("args",instance, file=sys.stderr)
        print ("kwargs",instance, file=sys.stderr)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


    def get_queryset(self):
        #print ("get_filterset",self, dir(self), file=sys.stderr)
        #limit = self.request.query_params.get('limit', None)
        userkey = self.request.query_params.get('userkey', None)
        as_geojson = self.request.query_params.get('as_geojson', None)

        if userkey:
            try:
                uuidkey = UUID(userkey)
            except:
                raise APIException('bad userkey')
            if userkeys.objects.filter(pk=uuidkey).exists():
                self.queryset = self.queryset.filter(sequence__creator=uuidkey)
            else:
                raise APIException('userkey not found')

        if as_geojson:
            self.serializer_class = panoramas_geo_serializer
            self.pagination_class = GeoJsonPagination

        '''
        print ("COUNT",self.queryset.count(), file=sys.stderr)
        if self.queryset.count() > 10:
            if not limit:
                limit = 10 #set default limit parameter
            elif limit > 500: #set default limit parameter
                limit = 500 #set default limit parameter
            return self.queryset[:limit]
        else:
            return self.queryset
        '''

        return self.queryset


class image_object_typesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = image_object_types.objects.all()
    serializer_class = image_object_types_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)


class image_objectsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = image_objects.objects.all()
    serializer_class = image_objects_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)
    pagination_class = basePagination
    distance_filter_field = 'geom'
    bbox_filter_field = 'geom'
    filter_backends = (DjangoFilterBackend, DistanceToPointFilter, InBBoxFilter)
    filterset_fields = ('panorama', 'id', 'type')

    def get_queryset(self):
        as_geojson = self.request.query_params.get('as_geojson', None)
        if as_geojson:
            self.serializer_class = image_objects_geo_serializer
            self.pagination_class = GeoJsonPagination
        return self.queryset

class userkeysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = userkeys.objects.all()
    serializer_class = userkeys_serializer
    permission_classes = ( IsAuthenticated,)
    pagination_class = basePagination


class apikeysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = appkeys.objects.all()
    serializer_class = appkeys_serializer
    permission_classes = ( IsAuthenticated,)
    pagination_class = basePagination
