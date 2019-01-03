"""mm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

#from django.contrib.auth.views import login, logout, password_change, password_change_done
from django.contrib.gis import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from rest_framework import routers


from wide_sight.views import viewer, sequencesViewSet, panoramasViewSet, image_object_typesViewSet, image_objectsViewSet, userkeysViewSet, apikeysViewSet

router = routers.DefaultRouter()
router.register(r'sequences', sequencesViewSet)
router.register(r'panoramas', panoramasViewSet)
router.register(r'image_object_types', image_object_typesViewSet)
router.register(r'image_objects', image_objectsViewSet)
router.register(r'userkeys', userkeysViewSet)
router.register(r'apikeys', apikeysViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^viewer/$', viewer, name='viewer'),
    url(r'^viewer/([-\w]+)/$', viewer, name='viewer'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),


    #url(r'^login/', login,{'template_name': 'registration/login.html'},name='cdu_login'),
    #url(r'^logout/', logout,{'template_name': 'registration/logged_out.html','next_page': '/certificati/'},name='cdu_login'),
    #url(r'^change-password/$', password_change,{'template_name': 'registration/password_change_form.html', 'post_change_redirect': 'cdu_password_change_done'},name='cdu_change-password'),
    #url(r'^password-changed/$', password_change_done,{'template_name': 'registration/password_change_done.html'},name='cdu_password_change_done'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
