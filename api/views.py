from django.shortcuts import render
from instituto.models import ProfesorUser, Asignatura, Grupo, Alumno, Matricula, Anotacion
from serializers import ProfesorUserSerializer, GrupoSerializer, AsignaturaSerializer, AlumnadoAsignaturaSerializer, AlumnoSerializer, MatriculaSerializer, AnotacionSerializer
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

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
    permission_classes = (IsAuthenticated,)
    pass

class ProfesorUserDetail(ProfesorUserMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    pass

class GrupoViewSet(viewsets.ModelViewSet):
    queryset = Grupo.objects.all()
    serializer_class = GrupoSerializer
    permission_classes = (IsAuthenticated,)

class AsignaturaViewSet(viewsets.ModelViewSet):
    #queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Asignatura.objects.filter(profesor=self.request.user)

class AlumnadoAsignaturaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AlumnadoAsignaturaSerializer
    permission_classes = (IsAuthenticated,)

"""class AlumnoViewSet(viewsets.ModelViewSet):
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer"""

class MatriculaViewSet(viewsets.ModelViewSet):
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer
    permission_classes = (IsAuthenticated,)

class AnotacionViewSet(viewsets.ModelViewSet):
    queryset = Anotacion.objects.all()
    serializer_class = AnotacionSerializer
    permission_classes = (IsAuthenticated,)


class AlumnoMixin(object):
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer

class AlumnoList(AlumnoMixin, ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    pass

class AlumnoDetail(AlumnoMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    pass