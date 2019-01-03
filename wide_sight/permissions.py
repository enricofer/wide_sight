import sys

from rest_framework import permissions
from .models import appkeys


class baseAPIPermission(permissions.BasePermission):

    message = 'Bad apikey.'

    def has_permission(self, request, view):
        try:
            api_key = request.query_params.get('apikey', False)
            print ("api_key",api_key, file=sys.stderr)
            #api_key_post = request.query_params.post('apikey', False)
            appkeys.objects.get(key=key)# or api_key_post)
            return True
        except Exception as e:
            print ("baseAPIPermission failed",e, file=sys.stderr)
            return False
