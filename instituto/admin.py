from django.contrib import admin
from .models import Profesor, Grupo, Aula, Asignatura, Alumno, Anotacion
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class ProfesorResource(resources.ModelResource):

    class Meta:
        model = Profesor

class AsignaturaResource(resources.ModelResource):

    class Meta:
        model = Asignatura
        fields = ('id', 'nombre', 'profesor__nombre', 'profesor__apellidos', 'grupo__curso', 'grupo__unidad',)
        #exclude = ('campo_a_excluir',)
        #export_order = ('id', 'profesor', 'nombre')


class ProfesorAdmin(ImportExportModelAdmin):
    resource_class = ProfesorResource

class AsignaturaAdmin(ImportExportModelAdmin):
    resource_class = AsignaturaResource

# Register your models here.

admin.site.register(Profesor, ProfesorAdmin)
admin.site.register(Grupo)
admin.site.register(Aula)
admin.site.register(Asignatura, AsignaturaAdmin)
admin.site.register(Alumno)
admin.site.register(Anotacion)