from django.contrib.gis import admin
from django.utils.html import format_html

from .models import sequences, panoramas, image_object_types, image_objects, userkeys, appkeys

@admin.register(panoramas)
class panoramaAdmin( admin.OSMGeoAdmin):

    def eqimage_tag(self, obj):
        return format_html('<img src="{}" />'.format(obj.eqimage_thumbnail.url))

    list_display = ['eqimage_tag',]
    exclude = ('', )

admin.site.register(sequences, admin.OSMGeoAdmin)
admin.site.register(image_object_types)
admin.site.register(image_objects, admin.OSMGeoAdmin)
admin.site.register(appkeys)
admin.site.register(userkeys)
