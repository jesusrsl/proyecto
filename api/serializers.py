from collections import OrderedDict

from instituto.models import ProfesorUser, Asignatura, Grupo, Alumno, Matricula, Anotacion
from rest_framework import serializers



class ProfesorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfesorUser
        fields = ('pk', 'first_name', 'last_name', 'username', 'email')

class GrupoSerializer(serializers.HyperlinkedModelSerializer):

    tutor = ProfesorUserSerializer(read_only=True)
    tutorId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfesorUser.objects.all(), source='tutor')
    cursoText = serializers.CharField(read_only=True, source='get_curso_display')

    class Meta:
        model = Grupo
        fields = ('pk', 'url', 'cursoText', 'curso', 'unidad', 'tutor', 'tutorId')


class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = ('pk', 'nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo', 'asignaturas')

class AsignaturaSerializer(serializers.HyperlinkedModelSerializer):
    profesor = ProfesorUserSerializer(read_only=True)
    profesorText = serializers.StringRelatedField(source='profesor')
    profesorId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfesorUser.objects.all(), source='profesor')
    #alumnos = AlumnoSerializer(many=True, read_only=True, source='alumno_set')
    grupo = GrupoSerializer
    grupoText = serializers.StringRelatedField(source='grupo')

    class Meta:
        model = Asignatura
        fields = ('pk', 'url', 'nombre', 'profesorText', 'profesor', 'profesorId', 'grupoText', 'grupo', 'distribucion')

#Alumnado de la asignatura indicada
class AlumnadoAsignaturaSerializer(serializers.ModelSerializer):
    grupo = GrupoSerializer
    grupoText = serializers.StringRelatedField(source='grupo')
    alumnos = AlumnoSerializer(many=True, read_only=True, source='alumno_set')
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
