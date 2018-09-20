from django.contrib import admin
from .models import sequences, panoramas, image_object_types, image_objects, userkeys

admin.site.register(sequences)
admin.site.register(panoramas)
admin.site.register(image_object_types)
admin.site.register(image_objects)
admin.site.register(userkeys)