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
router.register(r'lista/asignaturas', views.AsignaturaViewSet, base_name='lista-asignaturas')
router.register(r'asignaturas', views.MisAsignaturaViewSet, base_name='asignaturas')
router.register(r'lista/grupos', views.GrupoListViewSet, base_name='lista-grupos')
router.register(r'tutoria', views.AlumnadoTutoriaViewSet, base_name='tutoria')
router.register(r'alumnado/asignaturas', views.AlumnadoAsignaturaViewSet, base_name='alumnado-asignaturas')
router.register(r'alumnado/grupos', views.AlumnadoGrupoViewSet, base_name='alumnado-grupos')
#router.register(r'alumnos', views.AlumnoViewSet)
router.register(r'matriculas', views.MatriculaViewSet)
router.register(r'anotaciones', views.AnotacionViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
#PROFESORES
    url(r'^profesores/$', views.ProfesorUserList.as_view(), name='list-profesores'), #GET, POST
    url(r'^profesor/(?P<pk>\d+)/$', views.ProfesorUserDetail.as_view(), name='detail-profesor'), #GET, PUT, DELETE
#ALUMNOS
    url(r'^alumnos/$', views.AlumnoList.as_view(), name='list-alumnos'),
    url(r'^alumno/(?P<pk>\d+)/$', views.AlumnoDetail.as_view(), name='detail-alumno'),
    url(r'^alumno/(?P<pk>\d+)/borrar/foto$', views.AlumnoBorrarFoto.as_view(), name='borrar-foto-alumno'),
#ALUMNADO-ASIGNATURA-ANOTACIONES
url(r'^asignatura/(?P<pk>\d+)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/detalle/$',
        views.DetailAsignatura.as_view(), name='detail-asignatura'),

]


#urlpatterns = format_suffix_patterns(urlpatterns)