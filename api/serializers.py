from collections import OrderedDict

from instituto.models import ProfesorUser, Asignatura, Grupo, Alumno, Matricula, Anotacion
from rest_framework import serializers
from datetime import date, datetime



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

class GrupoListSerializer(serializers.ModelSerializer):
    tutor = serializers.StringRelatedField(read_only=True)
    curso = serializers.CharField(read_only=True, source='get_curso_display')
    num_alumnos = serializers.IntegerField(read_only=True, source='alumno_set.count')

    class Meta:
        model = Grupo
        fields = ('pk', 'curso', 'unidad', 'tutor', 'num_alumnos')


class AlumnoSerializer(serializers.ModelSerializer):
    #anotacion_set = serializers.StringRelatedField(many=True, read_only=True)
    grupo = serializers.StringRelatedField(read_only=True)
    asignaturas = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Alumno
        fields = ('pk', 'nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo', 'asignaturas')
        #fields = ('pk', 'nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo', 'asignaturas', 'anotacion_set')


#Alumnado de la tutoria del usuario o de un grupo
class AlumnadoGrupoSerializer(serializers.ModelSerializer):
    grupo = serializers.CharField(read_only=True, source='__unicode__')
    tutor = serializers.StringRelatedField(read_only=True)
    alumnos = AlumnoSerializer(many=True, read_only=True, source='alumno_set')
    #anotaciones = AnotacionSerializer(many=True, read_only=True, source='anotacion_set')
    class Meta:
        model = Grupo
        fields = ('pk', 'grupo', 'tutor', 'alumnos')

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


class MisAsignaturaSerializer(serializers.ModelSerializer):
    #alumnos = AlumnoSerializer(many=True, read_only=True, source='alumno_set')
    grupo = serializers.StringRelatedField()

    class Meta:
        model = Asignatura
        fields = ('pk', 'nombre', 'grupo', 'distribucion')

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
    class Meta:
        model = Anotacion
        fields = ('pk', 'alumno', 'asignatura', 'fecha', 'falta', 'trabaja', 'positivos', 'negativos')

class AnotacionShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anotacion
        fields = ('pk', 'falta', 'trabaja', 'positivos', 'negativos')

class AnotacionesField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self, *args, **kwargs):
        """idAsignatura = self.kwargs['pk']
        fecha = datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y')
        queryset = Anotacion.objects.filter(asignatura__pk=idAsignatura, fecha=fecha)"""
        queryset = Anotacion.objects.all()
        return queryset

class AlumnoShortSerializer(serializers.ModelSerializer):

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
class DetailAsignaturaSerializer(serializers.ModelSerializer):
    grupo = serializers.StringRelatedField()
    alumnos = AlumnoShortSerializer(many=True, read_only=True, source='alumno_set')

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
            serializer = AlumnoShortSerializer(alumnos, many=True, read_only=True)
            return serializer.data
        else:
            return None

    class Meta:
        model = Asignatura
        fields = ('pk', 'nombre', 'grupo', 'alumnos', 'distribucion')"""