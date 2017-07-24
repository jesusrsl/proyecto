# This Python file uses the following encoding: utf-8
from django.contrib import admin
from django.forms import ModelForm
from .models import ProfesorUser, Grupo, Asignatura, Alumno, Matricula, Anotacion
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.core.exceptions import ObjectDoesNotExist

class ProfesorUserResource(resources.ModelResource):

    class Meta:
        model = ProfesorUser
        fields = ('username', 'first_name', 'last_name', 'email')

class AsignaturaResource(resources.ModelResource):

    class Meta:
        model = Asignatura
        fields = ('nombre', 'profesor__first_name', 'profesor__last_name', 'grupo__curso', 'grupo__unidad',)
        #exclude = ('campo_a_excluir',)
        #export_order = ('id', 'profesor', 'nombre')

class AlumnoResource(resources.ModelResource):

    class Meta:
        model = Alumno
        fields = ('nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'grupo__curso', 'grupo__unidad', )
        #exclude = ('campo_a_excluir',)
        #export_order = ('id', 'profesor', 'nombre')


class ProfesorUserAdmin(ImportExportModelAdmin):
    resource_class = ProfesorUserResource

class AsignaturaAdmin(ImportExportModelAdmin):
    resource_class = AsignaturaResource

class AlumnoAdmin(ImportExportModelAdmin):
    resource_class = AlumnoResource
"""
class AlumnoAdminForm(ModelForm):

    class Meta:
        model = Alumno
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AlumnoAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields['asignaturas'].queryset = Asignatura.objects.filter(grupo=self.instance.grupo)
        except ObjectDoesNotExist:
            pass

class AlumnoAdmin(admin.ModelAdmin):
    form = AlumnoAdminForm
    filter_horizontal = ('asignaturas',)
"""
# Register your models here.

admin.site.register(ProfesorUser, ProfesorUserAdmin) #se importa la lista de profesores, y cada usuario reseteará su contraseña
admin.site.register(Grupo)  #¿los grupos se crean desde el Front-end, seleccionando el tutor?
admin.site.register(Asignatura, AsignaturaAdmin)    #se importa la lista de asignaturas
admin.site.register(Alumno, AlumnoAdmin)    #se importa la lista de alumnos
admin.site.register(Matricula)  #el alumnado se matricula desde el Front-end
admin.site.register(Anotacion)  #las anotaciones se realizan desde el Front-end