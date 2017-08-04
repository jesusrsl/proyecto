from datetime import date, datetime
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response

from instituto.models import ProfesorUser, Asignatura, Grupo, Alumno, Matricula, Anotacion
from serializers import ProfesorUserSerializer, ProfesorDetailSerializer, GrupoSerializer, GrupoListSerializer
from serializers import AlumnadoGrupoSerializer, MisAsignaturaSerializer, DetailAsignaturaSerializer, AsignaturaSerializer, AlumnadoAsignaturaSerializer
from serializers import AlumnoSerializer, AlumnoShortSerializer, MatriculaSerializer, AnotacionSerializer, AnotacionShortSerializer
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView
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

class ProfesorUserDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfesorDetailSerializer

    def get_queryset(self):
        profesor = self.kwargs['pk']
        return ProfesorUser.objects.filter(pk=profesor)


class GrupoViewSet(viewsets.ModelViewSet):
    queryset = Grupo.objects.all()
    serializer_class = GrupoSerializer
    permission_classes = (IsAuthenticated,)


class MisAsignaturaViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = Asignatura.objects.all()
    serializer_class = MisAsignaturaSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Asignatura.objects.filter(profesor=self.request.user)

class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer
    permission_classes = (IsAuthenticated,)

class AlumnadoTutoriaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AlumnadoGrupoSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Grupo.objects.filter(tutor=self.request.user)

class AlumnadoAsignaturaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AlumnadoAsignaturaSerializer
    permission_classes = (IsAuthenticated,)


class AlumnadoGrupoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Grupo.objects.all()
    serializer_class = AlumnadoGrupoSerializer
    permission_classes = (IsAuthenticated,)

class GrupoListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Grupo.objects.all()
    serializer_class = GrupoListSerializer
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

class AlumnoBorrarFoto(AlumnoMixin, UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def perform_update(self, serializer):
        serializer.save(foto=None)

class DetailAsignaturaMixin(object):
    queryset = Asignatura.objects.all()
    serializer_class = DetailAsignaturaSerializer

class DetailAsignatura(DetailAsignaturaMixin, RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        idAsignatura = self.kwargs['pk']
        fecha = datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y')
        return {"idAsignatura": idAsignatura, "fecha": fecha, "request": self.request}


class CreateAnotacion(CreateAPIView):
    queryset = Anotacion.objects.all()
    serializer_class = AnotacionShortSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(alumno=Alumno.objects.get(pk=self.kwargs['idAlumno']),
                        asignatura=Asignatura.objects.get(pk=self.kwargs['idAsignatura']),
                        fecha=datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y') )

class UpdateAnotacion(RetrieveUpdateAPIView):
    queryset = Anotacion.objects.all()
    serializer_class = AnotacionSerializer
    permission_classes = (IsAuthenticated,)

    pass

    """def perform_update(self, serializer):
        serializer.save(alumno=Alumno.objects.get(pk=self.kwargs['idAlumno']),
                        asignatura=Asignatura.objects.get(pk=self.kwargs['idAsignatura']),
                        fecha=datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y') )"""


