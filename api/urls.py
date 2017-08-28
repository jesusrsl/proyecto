# This Python file uses the following encoding: utf-8
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
router.register(r'lista/asignaturas', views.AsignaturaViewSet, base_name='list-asignaturas')
router.register(r'asignaturas', views.MisAsignaturasViewSet, base_name='asignaturas')
router.register(r'lista/grupos', views.GrupoListViewSet, base_name='list-grupos')
router.register(r'spinner/grupos', views.GrupoShortViewSet, base_name='spinner-grupos')
router.register(r'tutoria', views.AlumnadoTutoriaViewSet, base_name='tutoria')
router.register(r'orden/tutoria', views.AlumnadoOrdenadoTutoriaViewSet, base_name='tutoria-orden')
router.register(r'alumnado/asignaturas', views.AlumnadoAsignaturaViewSet, base_name='alumnado-asignaturas')
router.register(r'alumnado/grupos', views.AlumnadoGrupoViewSet, base_name='alumnado-grupos')
router.register(r'alumnado/orden/grupos', views.AlumnadoOrdenadoGrupoViewSet, base_name='alumnado-orden-grupos')
#router.register(r'alumnos', views.AlumnoViewSet)
router.register(r'matriculas', views.MatriculaViewSet)
#router.register(r'anotaciones', views.AnotacionViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
#PROFESORES
    url(r'^profesores/$', views.ProfesorUserList.as_view(), name='list-profesores'), #GET, POST
    url(r'^profesor/(?P<pk>\d+)/$', views.ProfesorUserDetail.as_view(), name='detail-profesor'), #GET, PUT, DELETE

#GRUPOS
    #cambiar el número de columnas del grupo
    url(r'^grupo/(?P<pk>\d+)/distribucion/$', views.UpdateDistribucionGrupo.as_view(), name='distribucion-grupo'),
    #cambiar la disposición u orden del alumnado dentro del grupo
    url(r'^grupo/(?P<pk>\d+)/disposicion/$', views.UpdateDisposicionGrupo.as_view(), name='disposicion-grupo'),

#ASIGNATURAS POR GRUPOS
    url(r'^grupo/(?P<idGrupo>\d+)/asignaturas/$', views.AsignaturasGrupo.as_view(), name='list-asignaturas-grupo'), #GET, POST
#ALUMNOS
    url(r'^alumnos/$', views.AlumnoList.as_view(), name='list-alumnos'),
    url(r'^alumno/(?P<pk>\d+)/$', views.AlumnoDetail.as_view(), name='detail-alumno'),
    url(r'^alumno/(?P<pk>\d+)/borrar/foto$', views.AlumnoBorrarFoto.as_view(), name='borrar-foto-alumno'),
#ALUMNADO-ASIGNATURA-ANOTACIONES
    url(r'^asignatura/(?P<pk>\d+)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/detalle/$',
        views.DetailAsignatura.as_view(), name='detail-asignatura'),

#ANOTACIONES
    url(r'^anotacion/nueva/(?P<idAlumno>\d+)/(?P<idAsignatura>\d+)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$',views.CreateAnotacion.as_view(), name='new-anotacion'),
    url(r'^anotacion/(?P<pk>\d+)/editar/$', views.UpdateAnotacion.as_view(), name='edit-anotacion'),

    url(r'^anotaciones/PDF/$', views.ver_anotaciones, name='anotaciones-pdf'),
    url(r'^anotacion/falta/$',views.poner_anotaciones, name='put-falta'),
    #url(r'^anotacion/trabaja/(?P<idAlumno>\d+)/(?P<idAsignatura>\d+)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$',views.ponerTrabaja, name='put-trabaja'),
    #url(r'^anotacion/positivo/(?P<idAlumno>\d+)/(?P<idAsignatura>\d+)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$',views.ponerPositivo, name='put-positivo'),
    #url(r'^anotacion/negativo/(?P<idAlumno>\d+)/(?P<idAsignatura>\d+)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$',views.ponerNegativo, name='put-negativo'),

    #url(r'^anotaciones/nueva/(?P<idAsignatura>\d+)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$',views.ponerAnotaciones, name='put-anotaciones'),

]
