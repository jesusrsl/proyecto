from django.conf.urls import url, include
from django.contrib import admin
from api import views
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.urlpatterns import format_suffix_patterns


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
#router.register(r'profesores', views.ProfesorUserViewSet)
router.register(r'grupos', views.GrupoViewSet)
router.register(r'asignaturas', views.AsignaturaViewSet)
#router.register(r'alumnos', views.AlumnoViewSet)
router.register(r'matriculas', views.MatriculaViewSet)
router.register(r'anotaciones', views.AnotacionViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
#PROFESORES
    url(r'^profesores/$', views.ProfesorUserList.as_view(), name='lista-profesores'),
    url(r'^profesor/(?P<pk>\d+)/$', views.ProfesorUserDetail.as_view(), name='detalle-profesor'),
#ALUMNOS
    url(r'^alumnos/$', views.AlumnoList.as_view(), name='lista-alumnos'),
    url(r'^alumno/(?P<pk>\d+)/$', views.AlumnoDetail.as_view(), name='detalle-alumno'),
]


#urlpatterns = format_suffix_patterns(urlpatterns)