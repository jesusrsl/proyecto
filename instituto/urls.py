from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$',views.base, name='inicio'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^login/$', auth_views.logout, {'template_name': 'logout.html'}, name='logout'),

    #PROFESORES
    url(r'^profesores/$', views.ProfesorListView.as_view(), name='lista-profesores'),
    url(r'^profesor/(?P<pk>\d+)/detalle/$', views.ProfesorDetailView.as_view(), name='detalle-profesor'),
    #create
    url(r'^profesor/nuevo/$', views.ProfesorCreate.as_view(), name='nuevo-profesor'),

    #update
    url(r'^profesor/(?P<pk>\d+)/editar/$', views.ProfesorUpdate.as_view(), name='editar-profesor'),
    #delete
    url(r'^profesor/(?P<pk>\d+)/eliminar/$', views.ProfesorDelete.as_view(), name='eliminar-profesor'),

    #TUTORES
    url(r'^tutores/$', views.TutorListView.as_view(), name='lista-tutores'),

    #ASIGNATURAS
    url(r'^asignaturas/$', views.AsignaturaListView.as_view(), name='lista-asignaturas'),

    url(r'^asignaturas/(?P<idProfesor>\d+)/$', views.AsignaturaProfesorListView.as_view(), name='asignaturas-profesor'),

    #detalle de la asignatura en la fecha actual
    #url(r'^asignatura/(?P<pk>\d+)/detalle/$', views.AsignaturaDetailView.as_view(), name='detalle-asignatura'),
    #detalle de la asignatura en la fecha indicada
    url(r'^asignatura/(?P<pk>\d+)/cuad/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/detalle/$', views.AsignaturaCuadView.as_view(), name='detalle-asignatura-cuad'),

    url(
        r'^asignatura/(?P<pk>\d+)/lista/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/detalle/$',
        views.AsignaturaListaView.as_view(), name='detalle-asignatura-lista'),

    url(r'^asignatura/nueva/$', views.AsignaturaCreate.as_view(), name='nueva-asignatura'),
    url(r'^asignatura/(?P<pk>\d+)/editar/$', views.AsignaturaUpdate.as_view(), name='editar-asignatura'),
    url(r'^asignatura/(?P<pk>\d+)/eliminar/$', views.AsignaturaDelete.as_view(), name='eliminar-asignatura'),
    url(r'^asignaturas/PDF/$', views.asignaturasPDF, name="asignaturas-pdf"),
    url(r'^asignatura/(?P<pk>\d+)/ordenar/$', views.ordenarAsignatura, name='ordenar-asignatura'),

    #GRUPOS
    url(r'^grupos/$', views.GrupoListView.as_view(), name='lista-grupos'),
    url(r'^grupo/(?P<pk>\d+)/detalle/$', views.GrupoDetailView.as_view(), name='detalle-grupo'),
    url(r'^grupo/nuevo/$', views.GrupoCreate.as_view(), name='nuevo-grupo'),
    url(r'^grupo/(?P<pk>\d+)/editar/$', views.GrupoUpdate.as_view(), name='editar-grupo'),
    url(r'^grupo/(?P<pk>\d+)/eliminar/$', views.GrupoDelete.as_view(), name='eliminar-grupo'),

    #AULAS
    #url(r'^aulas/$', views.AulaListView.as_view(), name='lista-aulas'),
    #url(r'^aula/(?P<pk>\d+)/detalle/$', views.AulaDetailView.as_view(), name='detalle-aula'),
    #url(r'^aula/nueva/$', views.AulaCreate.as_view(), name='nueva-aula'),
    #url(r'^aula/(?P<pk>\d+)/editar/$', views.AulaUpdate.as_view(), name='editar-aula'),
    #url(r'^aula/(?P<pk>\d+)/eliminar/$', views.AulaDelete.as_view(), name='eliminar-aula'),

    #ALUMNOS
    url(r'^alumnos/$', views.AlumnoListView.as_view(), name='lista-alumnos'),
    url(r'^alumno/(?P<pk>\d+)/detalle/$', views.AlumnoDetailView.as_view(), name='detalle-alumno'),
    url(r'^alumno/nuevo/$', views.AlumnoCreate.as_view(), name='nuevo-alumno'),
    url(r'^alumno/(?P<pk>\d+)/editar/$', views.AlumnoUpdate.as_view(), name='editar-alumno'),
    url(r'^alumno/(?P<pk>\d+)/eliminar/$', views.AlumnoDelete.as_view(), name='eliminar-alumno'),

    #MATRICULAS
    url(r'^matriculas/$', views.MatriculaListView.as_view(), name='lista-matriculas'),
    url(r'^matricula/(?P<pk>\d+)/detalle/$', views.MatriculaDetailView.as_view(), name='detalle-matricula'),
    url(r'^matricula/nueva/$', views.MatriculaCreate.as_view(), name='nueva-matricula'),
    url(r'^matricula/(?P<pk>\d+)/editar/$', views.MatriculaUpdate.as_view(), name='editar-matricula'),
    url(r'^matricula/(?P<pk>\d+)/eliminar/$', views.MatriculaDelete.as_view(), name='eliminar-matricula'),

    #ANOTACIONES
    #url(r'^anotaciones/(?P<idAsignatura>\d+)/$', views.AnotacionListView.as_view(), name='lista-anotaciones'),
    url(r'^anotaciones/(?P<idAsignatura>\d+)/$', views.anotacionesFechas, name='lista-anotaciones'),
    #url(r'^anotaciones/(?P<idAsignatura>\d+)/PDF/$', views.anotacionesPDF, name="anotaciones-pdf"),
    #NOTA: es llamado desde fecha-anotaciones

    url(r'^anotacion/(?P<pk>\d+)/detalle/$', views.AnotacionDetailView.as_view(), name='detalle-anotacion'),

    url(r'^anotar/(?P<idAlumno>\d+)/(?P<idAsignatura>\d+)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$', views.AnotacionCreateUpdate.as_view(), name='anotar'),

    url(r'^anotacion/nueva/(?P<idAlumno>\d+)/(?P<idAsignatura>\d+)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$', views.AnotacionCreate.as_view(), name='nueva-anotacion'),
    url(r'^anotacion/(?P<pk>\d+)/editar/$', views.AnotacionUpdate.as_view(), name='editar-anotacion'),
    url(r'^anotacion/(?P<pk>\d+)/eliminar/$', views.AnotacionDelete.as_view(), name='eliminar-anotacion'),

    url(r'^anotacion/falta/(?P<idAlumno>\d+)/(?P<idAsignatura>\d+)/(?P<vista>cuad|lista)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$', views.ponerFalta, name='poner-falta'),
    url(r'^anotacion/trabaja/(?P<idAlumno>\d+)/(?P<idAsignatura>\d+)/(?P<vista>cuad|lista)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$', views.ponerTrabaja, name='poner-trabaja'),
    url(r'^anotacion/positivo/(?P<idAlumno>\d+)/(?P<idAsignatura>\d+)/(?P<vista>cuad|lista)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$', views.ponerPositivo, name='poner-positivo'),
    url(r'^anotacion/negativo/(?P<idAlumno>\d+)/(?P<idAsignatura>\d+)/(?P<vista>cuad|lista)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$', views.ponerNegativo, name='poner-negativo'),

    url(r'^anotaciones/nueva/(?P<idAsignatura>\d+)/(?P<vista>cuad|lista)/(?P<fecha>(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[012])/((19|20)\d\d))/$', views.ponerAnotaciones, name='poner-anotaciones'),

]
