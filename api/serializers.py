# This Python file uses the following encoding: utf-8
import os, sys
from collections import OrderedDict

from instituto.models import ProfesorUser, Asignatura, Grupo, Alumno, Matricula, Anotacion
from rest_framework import serializers
from datetime import date, datetime


#Utilización: listar el profesorado
class ProfesorUserSerializer(serializers.ModelSerializer):
    grupo = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ProfesorUser
        fields = ('pk', 'first_name', 'last_name', 'username', 'email', 'is_superuser','grupo')
        #fields = '__all__'

#Utilización: ver los detalles de un profesor
class ProfesorDetailSerializer(serializers.ModelSerializer):
    asignatura_set = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ProfesorUser
        fields = ('pk', 'first_name', 'last_name','asignatura_set')

#Utilización: listar los grupos
class GrupoSerializer(serializers.HyperlinkedModelSerializer):

    tutor = ProfesorUserSerializer(read_only=True)
    tutorId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfesorUser.objects.all(), source='tutor')
    cursoText = serializers.CharField(read_only=True, source='get_curso_display')

    class Meta:
        model = Grupo
        fields = ('pk', 'url', 'cursoText', 'curso', 'unidad', 'tutor', 'tutorId', 'distribucion')

#Utilización: listar los grupos junto con el número de alumnos
class GrupoListSerializer(serializers.ModelSerializer):
    tutor = serializers.StringRelatedField(read_only=True)
    curso = serializers.CharField(read_only=True, source='get_curso_display')
    num_alumnos = serializers.IntegerField(read_only=True, source='alumno_set.count')

    class Meta:
        model = Grupo
        fields = ('pk', 'curso', 'unidad', 'tutor', 'distribucion', 'num_alumnos')

#Utilización: listar los grupos para los valores de un spinner, y cambiar su distribución
class GrupoShortSerializer(serializers.ModelSerializer):
    grupo = serializers.CharField(read_only=True, source='__unicode__')

    class Meta:
        model = Grupo
        fields = ('pk', 'grupo', 'distribucion')

#Utilización: es llamado por AlumnadoGrupoSerializer
class AlumnoSerializer(serializers.ModelSerializer):
    #anotacion_set = serializers.StringRelatedField(many=True, read_only=True)
    grupo = serializers.StringRelatedField(read_only=True)
    asignaturas = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Alumno
        fields = ('pk', 'nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo', 'asignaturas')
        #fields = ('pk', 'nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo', 'asignaturas', 'anotacion_set')

#Utilización: para ordenar al alumnado de un grupo
class AlumnoOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = ('pk', 'orden')


#Alumnado de la tutoria del usuario o de un grupo
#Utilización: listar el alumnado de un grupo (o tutoría)
class AlumnadoGrupoSerializer(serializers.ModelSerializer):
    grupo = serializers.CharField(read_only=True, source='__unicode__')
    tutor = serializers.StringRelatedField(read_only=True)
    alumnos = AlumnoSerializer(many=True, read_only=True, source='alumno_set')
    #anotaciones = AnotacionSerializer(many=True, read_only=True, source='anotacion_set')
    class Meta:
        model = Grupo
        fields = ('pk', 'grupo', 'tutor', 'distribucion', 'alumnos')

#Alumnado ordenado de la tutoria del usuario o de un grupo
#Utilización: listar el alumnado de un grupo (o tutoría) según como están sentados
class AlumnadoOrdenadoGrupoSerializer(serializers.ModelSerializer):
    grupo = serializers.CharField(read_only=True, source='__unicode__')
    tutor = serializers.StringRelatedField(read_only=True)
    alumnos = AlumnoSerializer(many=True, read_only=True, source='ordenar_alumnos')

    class Meta:
        model = Grupo
        fields = ('pk', 'grupo', 'tutor', 'distribucion', 'alumnos')

#Utilización: listar las asignaturas
class AsignaturaSerializer(serializers.ModelSerializer):
    profesor = ProfesorUserSerializer(read_only=True)
    profesorText = serializers.StringRelatedField(source='profesor')
    profesorId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfesorUser.objects.all(), source='profesor')
    #alumnos = AlumnoSerializer(many=True, read_only=True, source='alumno_set')
    grupo = GrupoSerializer
    grupoText = serializers.StringRelatedField(source='grupo')

    class Meta:
        model = Asignatura
        fields = ('pk', 'nombre', 'profesorText', 'profesor', 'profesorId', 'grupoText', 'grupo', 'distribucion')

#Utilización: listar las asignaturas del usuario (diario de clase)
class MisAsignaturasSerializer(serializers.ModelSerializer):
    #alumnos = AlumnoSerializer(many=True, read_only=True, source='alumno_set')
    grupo = serializers.StringRelatedField()

    class Meta:
        model = Asignatura
        fields = ('pk', 'nombre', 'grupo', 'distribucion')

#Alumnado de la asignatura indicada
#Utilización: ver los detalles de una asignatura junto con su alumnado
class AlumnadoAsignaturaSerializer(serializers.ModelSerializer):
    grupo = GrupoSerializer
    grupoText = serializers.StringRelatedField(source='grupo')
    alumnos = AlumnoSerializer(many=True, read_only=True, source='alumno_set')
    #anotaciones = AnotacionSerializer(many=True, read_only=True, source='anotacion_set')
    class Meta:
        model = Asignatura
        fields = ('pk', 'nombre', 'grupoText', 'alumnos', 'distribucion')


class MatriculaSerializer(serializers.HyperlinkedModelSerializer):
    alumno = serializers.PrimaryKeyRelatedField(queryset=Alumno.objects.all())
    class Meta:
        model = Matricula
        fields = ('url', 'alumno', 'asignatura', 'orden')

#Serializadores para realizar las anotaciones
class AnotacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anotacion
        fields = ('pk', 'alumno', 'asignatura', 'fecha', 'falta', 'trabaja', 'positivos', 'negativos')

#Utilización: valoraciones de las que se compone una anotación
class AnotacionShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anotacion
        fields = ('pk', 'falta', 'trabaja', 'positivos', 'negativos')


"""class AnotacionesField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self, *args, **kwargs):
        //idAsignatura = self.kwargs['pk']
        //fecha = datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y')
        //queryset = Anotacion.objects.filter(asignatura__pk=idAsignatura, fecha=fecha)
        queryset = Anotacion.objects.all()
        return queryset"""

#Utilización: ver a un alumno (nombre y apellidos) junto con sus anotaciones en la fecha indicada
class AlumnoAnotacionSerializer(serializers.ModelSerializer):

    anotacion = serializers.SerializerMethodField('obtenerAnotaciones')

    def obtenerAnotaciones(self, obj):
        idAsignatura = self.context.get("idAsignatura")
        fecha = self.context.get("fecha")

        anotaciones = Anotacion.objects.filter(asignatura__id=idAsignatura, fecha=fecha, alumno=obj)

        if anotaciones:
            serializer = AnotacionSerializer(anotaciones.first())
            return serializer.data
        else:
            return None

    class Meta:
        model = Alumno
        #ordering = ('pk',)
        fields = ('pk', 'nombre', 'apellido1', 'apellido2','foto', 'anotacion')

#Alumnado de la asignatura indicada
#Utilización: ver al alumnado de una asignatura para añadirle anotaciones (diario de clase)
class DetailAsignaturaSerializer(serializers.ModelSerializer):
    grupo = serializers.StringRelatedField()
    alumnos = AlumnoAnotacionSerializer(many=True, read_only=True, source='alumno_set')

    class Meta:
        model = Asignatura
        fields = ('pk', 'nombre', 'grupo', 'alumnos', 'distribucion')

"""class DetailAsignaturaSerializer(serializers.ModelSerializer):
    grupo = serializers.StringRelatedField()
    alumnos = serializers.SerializerMethodField('obtenerAlumnado')

    def obtenerAlumnado(self, obj):

        alumnos = Asignatura.objects.get(pk=obj.pk).alumno_set.order_by('matricula__orden')

        print alumnos
        if alumnos:
            serializer = AlumnoAnotacionSerializer(alumnos, many=True, read_only=True)
            return serializer.data
        else:
            return None

    class Meta:
        model = Asignatura
        fields = ('pk', 'nombre', 'grupo', 'alumnos', 'distribucion')"""