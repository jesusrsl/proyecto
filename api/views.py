from datetime import date, datetime
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response

from instituto.models import ProfesorUser, Asignatura, Grupo, Alumno, Matricula, Anotacion
from serializers import ProfesorUserSerializer, ProfesorDetailSerializer, GrupoSerializer, GrupoListSerializer
from serializers import AlumnadoGrupoSerializer, MisAsignaturaSerializer, DetailAsignaturaSerializer, AsignaturaSerializer, AlumnadoAsignaturaSerializer
from serializers import AlumnoSerializer, MatriculaSerializer, AnotacionSerializer
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, RetrieveAPIView
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

class AlumnoBorrarFoto(AlumnoMixin, RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        instance.foto=None      #se borra la foto del alumno
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class DetailAsignatura(RetrieveAPIView):
    serializer_class = DetailAsignaturaSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        idAsignatura = self.kwargs['pk']
        fecha = datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y')
        return {"idAsignatura": idAsignatura, "fecha": fecha}

    def get_queryset(self):
        return Asignatura.objects.all()