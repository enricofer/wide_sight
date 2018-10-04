from django.contrib.gis import admin
from .models import sequences, panoramas, image_object_types, image_objects, userkeys, appkeys

admin.site.register(sequences, admin.OSMGeoAdmin)
admin.site.register(panoramas, admin.OSMGeoAdmin)
admin.site.register(image_object_types)
admin.site.register(image_objects)
admin.site.register(appkeys)
admin.site.register(userkeys)
