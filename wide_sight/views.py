import sys
from uuid import UUID

from django.contrib.auth.models import User
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
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_condition import Or
from drf_autodocs.decorators import format_docstring

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
    List sequences matching url parameters.

    post:
    Create a new sequence instance.

    patch:
    edit and update an existing sequence.

    delete:
    permanently delete an existing sequence.
    """
    queryset = sequences.objects.all()
    serializer_class = sequences_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)
    pagination_class = basePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('creator_key', )

    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess), ) #Or(baseAPIPermission, HasAPIAccess),
        else:
            self.permission_classes = ( IsAuthenticated, )
        super(sequencesViewSet, self).initial(request, *args, **kwargs)

@format_docstring()
class panoramasViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to be view or edit panoramas.

    get:
    List panoramas matching url parameters.

    post:
    Create a new panorama instance.

    patch:
    edit and update an existing panorama.

    delete:
    permanently delete an existing panorama.
    """
    queryset = panoramas.objects.all()
    serializer_class = panoramas_serializer
    response_serializer_class = panoramas_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)
    pagination_class = basePagination
    distance_filter_field = 'geom'
    bbox_filter_field = 'geom'
    filter_backends = (DjangoFilterBackend, DistanceToPointFilter, InBBoxFilter)
    filterset_fields = ('sequence', )

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

    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess), ) #Or(baseAPIPermission, HasAPIAccess),
        else:
            self.permission_classes = ( IsAuthenticated, )
        super(panoramasViewSet, self).initial(request, *args, **kwargs)


class image_object_typesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to be view or edit image objects.

    get:
    List image objects matching url parameters.

    post:
    Create a new image object instance.

    patch:
    edit and update an existing image object.

    delete:
    permanently delete an existing image object.
    """
    queryset = image_object_types.objects.all()
    serializer_class = image_object_types_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)

    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess), ) #Or(baseAPIPermission, HasAPIAccess),
        else:
            self.permission_classes = ( IsAuthenticated, )
        super(image_object_typesViewSet, self).initial(request, *args, **kwargs)


class image_objectsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to be view or edit image objects.

    get:
    List image objects matching url parameters.

    post:
    Create a new image object instance.

    patch:
    edit and update an existing image object.

    delete:
    permanently delete an existing image object.
    """
    queryset = image_objects.objects.all()
    serializer_class = image_objects_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)
    pagination_class = basePagination
    distance_filter_field = 'geom'
    bbox_filter_field = 'geom'
    filter_backends = (DjangoFilterBackend, DistanceToPointFilter, InBBoxFilter)
    filterset_fields = ('panorama', 'type')

    def get_queryset(self):
        as_geojson = self.request.query_params.get('as_geojson', None)
        if as_geojson:
            self.serializer_class = image_objects_geo_serializer
            self.pagination_class = GeoJsonPagination
        return self.queryset

    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess), ) #Or(baseAPIPermission, HasAPIAccess),
        else:
            self.permission_classes = ( IsAuthenticated, )
        super(image_objectsViewSet, self).initial(request, *args, **kwargs)

class userkeysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = userkeys.objects.all()
    serializer_class = userkeys_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)
    pagination_class = basePagination
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('user',)

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        print ("USERNAME QUERYSET: ", username, file=sys.stderr)
        if username:
            user_selected = User.objects.get(username=username)
            self.queryset = self.queryset.filter(user=user_selected)
        return self.queryset


class apikeysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = appkeys.objects.all()
    serializer_class = appkeys_serializer
    permission_classes = ( IsAuthenticated,)
    pagination_class = basePagination


class APIRoot(APIView):
    """
    API Root ...
    """
    permission_classes = ()

    def get(self, request, format=None):
        data = {
            'sequences': reverse('sequences-list', request=request, format=format),
            'panoramas': reverse('panoramas-list', request=request, format=format),
            'image-objects': reverse('image_objects-list', request=request, format=format),
        }

        return Response(data)
