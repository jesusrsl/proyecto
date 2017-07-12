from instituto.models import ProfesorUser, Asignatura, Grupo, Alumno, Matricula, Anotacion
from rest_framework import serializers


class ProfesorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfesorUser
        fields = ('pk', 'first_name', 'last_name', 'username', 'email')

class GrupoSerializer(serializers.HyperlinkedModelSerializer):
    tutor = ProfesorUserSerializer(read_only=True)
    class Meta:
        model = Grupo
        fields = ('url', 'curso', 'unidad', 'tutor')


class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = ('nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo', 'asignaturas')

class AsignaturaSerializer(serializers.HyperlinkedModelSerializer):
    profesor = ProfesorUserSerializer(read_only=True)
    profesorId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfesorUser.objects.all(), source='profesor')
    alumnos = AlumnoSerializer(many=True, read_only=True, source='alumno_set')
    class Meta:
        model = Asignatura
        fields = ('url', 'nombre', 'profesor', 'profesorId', 'grupo', 'distribucion', 'alumnos')

class MatriculaSerializer(serializers.HyperlinkedModelSerializer):
    alumno = serializers.PrimaryKeyRelatedField(queryset=Alumno.objects.all())
    class Meta:
        model = Matricula
        fields = ('url', 'alumno', 'asignatura', 'orden')

class AnotacionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Anotacion
        fields = ('url', 'alumno', 'asignatura', 'fecha', 'falta', 'trabaja', 'positivos', 'negativos')
