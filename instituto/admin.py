from django.contrib import admin
from django.forms import ModelForm
from .models import Profesor, Grupo, Aula, Asignatura, Alumno, Anotacion
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.core.exceptions import ObjectDoesNotExist

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

# Register your models here.

admin.site.register(Profesor, ProfesorAdmin)
admin.site.register(Grupo)
admin.site.register(Aula)
admin.site.register(Asignatura, AsignaturaAdmin)
admin.site.register(Alumno, AlumnoAdmin)
admin.site.register(Anotacion)