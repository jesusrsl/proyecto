from django.shortcuts import render
from instituto.models import ProfesorUser, Asignatura, Grupo, Alumno, Matricula, Anotacion
from serializers import ProfesorUserSerializer, GrupoSerializer, AsignaturaSerializer, AlumnoSerializer, MatriculaSerializer, AnotacionSerializer
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

# Create your views here.
#REST API
"""class ProfesorUserViewSet(viewsets.ModelViewSet):

    #API endpoint that allows users to be viewed or edited.

    queryset = ProfesorUser.objects.all()
    serializer_class = ProfesorUserSerializer"""

class ProfesorUserMixin(object):
    queryset = ProfesorUser.objects.all()
    serializer_class = ProfesorUserSerializer

class ProfesorUserList(ProfesorUserMixin, ListCreateAPIView):
    pass

class ProfesorUserDetail(ProfesorUserMixin, RetrieveUpdateDestroyAPIView):
    pass

class GrupoViewSet(viewsets.ModelViewSet):
    queryset = Grupo.objects.all()
    serializer_class = GrupoSerializer

class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer

class AlumnoViewSet(viewsets.ModelViewSet):
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer

class MatriculaViewSet(viewsets.ModelViewSet):
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer

class AnotacionViewSet(viewsets.ModelViewSet):
    queryset = Anotacion.objects.all()
    serializer_class = AnotacionSerializer


class AlumnoMixin(object):
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer

class AlumnoList(AlumnoMixin, ListCreateAPIView):
    pass

class AlumnoDetail(AlumnoMixin, RetrieveUpdateDestroyAPIView):
    pass