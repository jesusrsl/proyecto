from collections import OrderedDict

from instituto.models import ProfesorUser, Asignatura, Grupo, Alumno, Matricula, Anotacion
from rest_framework import serializers



class ProfesorUserSerializer(serializers.ModelSerializer):
    grupo_set = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ProfesorUser
        fields = ('pk', 'first_name', 'last_name', 'username', 'email', 'is_superuser','grupo_set')
        #fields = '__all__'

class ProfesorDetailSerializer(serializers.ModelSerializer):
    asignatura_set = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ProfesorUser
        fields = ('pk', 'first_name', 'last_name','asignatura_set')

class GrupoSerializer(serializers.HyperlinkedModelSerializer):

    tutor = ProfesorUserSerializer(read_only=True)
    tutorId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfesorUser.objects.all(), source='tutor')
    cursoText = serializers.CharField(read_only=True, source='get_curso_display')

    class Meta:
        model = Grupo
        fields = ('pk', 'url', 'cursoText', 'curso', 'unidad', 'tutor', 'tutorId')

class AlumnoSerializer(serializers.ModelSerializer):
    #anotacion_set = serializers.StringRelatedField(many=True, read_only=True)
    grupo = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Alumno
        fields = ('pk', 'nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo', 'asignaturas')
        #fields = ('pk', 'nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo', 'asignaturas', 'anotacion_set')


class AsignaturaSerializer(serializers.HyperlinkedModelSerializer):
    profesor = ProfesorUserSerializer(read_only=True)
    profesorText = serializers.StringRelatedField(source='profesor')
    profesorId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfesorUser.objects.all(), source='profesor')
    #alumnos = AlumnoSerializer(many=True, read_only=True, source='alumno_set')
    grupo = GrupoSerializer
    grupoText = serializers.StringRelatedField(source='grupo')

    class Meta:
        model = Asignatura
        fields = ('pk', 'nombre', 'profesorText', 'profesor', 'profesorId', 'grupoText', 'grupo', 'distribucion')

#Alumnado de la asignatura indicada
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

class AnotacionSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer
    asignatura = AsignaturaSerializer
    class Meta:
        model = Anotacion
        fields = ('url', 'alumno', 'asignatura', 'fecha', 'falta', 'trabaja', 'positivos', 'negativos')
