# This Python file uses the following encoding: utf-8
from django.contrib import admin
from import_export import fields
from import_export.widgets import ForeignKeyWidget

from .models import ProfesorUser, Grupo, Asignatura, Alumno, Matricula, Anotacion
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.core.exceptions import ObjectDoesNotExist

class ProfesorUserResource(resources.ModelResource):

    class Meta:
        model = ProfesorUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class GrupoResource(resources.ModelResource):

    tutor = fields.Field(
        column_name='tutor',
        attribute='tutor',
        widget=ForeignKeyWidget(ProfesorUser, 'username'))


    class Meta:
        model = Grupo
        fields = ('id', 'curso', 'unidad', 'tutor')

class GrupoForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row):
        if len(row["unidad"]) > 0:
            return self.model.objects.filter(
                curso=row["curso"],
                unidad=row["unidad"]
            )
        else:
            print "aqui"
            return self.model.objects.filter(
                curso=row["curso"],
                unidad=""
            )


class AsignaturaResource(resources.ModelResource):
    profesor = fields.Field(
        column_name='profesor',
        attribute='profesor',
        widget=ForeignKeyWidget(ProfesorUser, 'username'))

    curso = fields.Field(
        column_name='curso',
        attribute='grupo',
        widget=GrupoForeignKeyWidget(Grupo, 'curso'))

    unidad = fields.Field(
        column_name='unidad',
        attribute='grupo',
        widget=GrupoForeignKeyWidget(Grupo, 'unidad'))

    class Meta:
        model = Asignatura
        exclude = ('grupo',)
        fields = ('id', 'nombre', 'profesor', 'grupo', 'curso', 'unidad',)
        #exclude = ('campo_a_excluir',)
        #export_order = ('id', 'profesor', 'nombre')


class AlumnoResource(resources.ModelResource):
    curso = fields.Field(
        column_name='curso',
        attribute='grupo',
        widget=GrupoForeignKeyWidget(Grupo, 'curso'))

    unidad = fields.Field(
        column_name='unidad',
        attribute='grupo',
        widget=GrupoForeignKeyWidget(Grupo, 'unidad'))

    class Meta:
        model = Alumno
        exclude = ('grupo', )
        fields = ('id', 'nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'grupo', 'curso', 'unidad')
        #exclude = ('campo_a_excluir',)
        #export_order = ('id', 'profesor', 'nombre')


class ProfesorUserAdmin(ImportExportModelAdmin):
    resource_class = ProfesorUserResource

class GrupoAdmin(ImportExportModelAdmin):
    resource_class = GrupoResource

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
admin.site.register(Grupo, GrupoAdmin)  #¿los grupos se crean desde el Front-end, seleccionando el tutor?
admin.site.register(Asignatura, AsignaturaAdmin)    #se importa la lista de asignaturas
admin.site.register(Alumno, AlumnoAdmin)    #se importa la lista de alumnos
admin.site.register(Matricula)  #el alumnado se matricula desde el Front-end
admin.site.register(Anotacion)  #las anotaciones se realizan desde el Front-end