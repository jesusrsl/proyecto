# This Python file uses the following encoding: utf-8
import csv
from datetime import date, datetime
from io import BytesIO
from itertools import groupby
from operator import itemgetter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, PageBreak
from reportlab.platypus import Table
import xlwt
from django.contrib import messages
from django.contrib.auth import login, logout, settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, RedirectView

from .forms import RegisterForm, UpdateForm, ProfesorUpdateForm, MatriculaForm
from .models import ProfesorUser, Asignatura, Grupo, Alumno, Matricula, Anotacion



# Create your views here.

# Login User
class LoginUser(FormView):
    model = ProfesorUser
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('asignaturas-profesor')

    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(self.get_success_url())
        else:
            return super(LoginUser, self).get(request, *args, **kwargs)
            """

    def form_valid(self, form):
        login(self.request, form.get_user())
        try:
            remember = self.request.POST['remember']
            if remember:
                settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
        except MultiValueDictKeyError:
            is_private = False
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True


        if self.request.POST.get('next') != '':
            return HttpResponseRedirect(self.request.POST.get('next'))
        else:
            return redirect(self.get_success_url())


class LogoutUser(RedirectView):
    url = reverse_lazy('inicio')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LogoutUser, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutUser, self).get(request, *args, **kwargs)

#INICIO
def base(request):
    if request.user.is_authenticated():
        return render(request, 'base.html')
    else:
        return HttpResponseRedirect(reverse("login"))


def acerca(request):
    return render(request, 'about.html')

@login_required
def profesoradoPDF(request):

    response = HttpResponse(content_type='application/pdf')
    pdf_name = "profesorado.pdf"
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            showBoundary=0,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=20,
                            title = "Profesorado",
                            author = request.user.username,
                            pageBreakQuick = 1,
                            )

    profesorado = []

    styles = getSampleStyleSheet()
    h1 = styles['Heading1']
    h1.alignment = 1    #centrado
    h1.spaceAfter = 30
    #h1.pageBreakBefore=1
    #h1.backColor=colors.red
    header = Paragraph("Listado de profesores/as", h1)
    profesorado.append(header)

    if request.user.is_superuser:
        headings = ['Login', 'Nombre', 'Apellidos', 'E- mail', 'Tutor/a', 'Admin']
    else:
        headings = ['Nombre', 'Apellidos', 'E- mail', 'Tutor/a', 'Admin']

    info_profesorado = []
    for p in ProfesorUser.objects.all():
        if request.user.is_superuser:
            profesor = (p.username, p.first_name, p.last_name, p.email)
        else:
            profesor = (p.first_name, p.last_name, p.email)
        if not Grupo.objects.filter(tutor=p).exists():
            profesor += ("---",)
        else:
            profesor += (p.grupo.get_curso_display() + " " + p.grupo.unidad,)
        if p.is_superuser:
                profesor += ("Sí",)
        else:
                profesor += ("No",)
        info_profesorado.append(profesor)


    t = Table([headings] + info_profesorado)
    t.setStyle(TableStyle(
        [
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(0x009688)),  # bordes de las celdas (de grosor 1)
            # ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor(0x009688)), # borde inferior (de mayor grosor, 2)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0x009688))
            # color de fondo (en este caso, solo la primera fila)
        ]
    ))

    # NOTA de TableStyle: las filas y columnas empiezan en 0. -1 para la ultima posicion (aunque sea desconocida)
    # otras opciones:
    # ('TEXTCOLOR', (0, 0), (-1, -1), colors.blue),
    # ('VALIGN', (0,0), (-1, -1), 'MIDDLE'),

    profesorado.append(t)

    doc.build(profesorado)
    response.write(buff.getvalue())
    buff.close()
    return response
"""
@login_required
def tutoriasPDF(request):

    response = HttpResponse(content_type='application/pdf')
    pdf_name = "tutorias.pdf"
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            showBoundary=0,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=20,
                            title = "Tutorías",
                            author = request.user.username,
                            pageBreakQuick = 1,
                            )

    tutorias = []

    styles = getSampleStyleSheet()
    h1 = styles['Heading1']
    h1.alignment = 1    #centrado
    h1.spaceAfter = 30
    #h1.pageBreakBefore=1
    #h1.backColor=colors.red
    header = Paragraph("Listado de tutores/as", h1)
    tutorias.append(header)


    headings = ['Tutor/a', 'Grupo']
    info_tutorias = [(p.first_name + " " + p.last_name, p.grupo) for p in ProfesorUser.objects.filter(grupo__isnull=False).order_by('grupo')]

    t = Table([headings] + info_tutorias)
    t.setStyle(TableStyle(
        [
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(0x009688)),  # bordes de las celdas (de grosor 1)
            # ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor(0x009688)), # borde inferior (de mayor grosor, 2)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0x009688))
            # color de fondo (en este caso, solo la primera fila)
        ]
    ))

    tutorias.append(t)

    doc.build(tutorias)
    response.write(buff.getvalue())
    buff.close()
    return response
"""
@login_required
def gruposPDF(request):

    response = HttpResponse(content_type='application/pdf')
    pdf_name = "grupos.pdf"
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            showBoundary=0,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=20,
                            title = "Listado de grupos",
                            author = request.user.username,
                            pageBreakQuick = 1,
                            )

    contenido = []

    # definicion de estilos
    styles = getSampleStyleSheet()
    # estilo para el titulo de cabecera
    h1 = styles['Heading1']
    h1.alignment = 1  # centrado
    h1.spaceAfter = 30
    # estilo para el cuerpo
    c1 = styles['Normal']
    c1.alignment = TA_CENTER
    c1.spaceAfter = 20
    c1.fontName = 'Times-Roman'

    for grupo in Grupo.objects.all():
        header = Paragraph("Grupo %s" %(grupo.get_curso_display() + " " +  grupo.unidad), h1)
        contenido.append(header)

        texto = Paragraph("Tutor/a: %s" % (grupo.tutor.first_name + " " + grupo.tutor.last_name), c1)
        contenido.append(texto)

        t = grupoPorPagina(grupo.pk)

        contenido.append(t)
        contenido.append(PageBreak())

    doc.build(contenido)
    response.write(buff.getvalue())
    buff.close()
    return response

@login_required
def grupoPDF(request, pk):

    response = HttpResponse(content_type='application/pdf')
    grupo = Grupo.objects.get(pk=pk)
    nombre = grupo.get_curso_display()
    if grupo.unidad != "":
        nombre = nombre + " " +  grupo.unidad
    pdf_name = "grupo-%s.pdf" % nombre.replace(" ","-")
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            showBoundary=0,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=20,
                            title = "Grupo %s" %(grupo.get_curso_display() + " " +  grupo.unidad),
                            author = request.user.username,
                            pageBreakQuick = 1,
                            )

    contenido = []

    # definicion de estilos
    styles = getSampleStyleSheet()
    # estilo para el titulo de cabecera
    h1 = styles['Heading1']
    h1.alignment = 1  # centrado
    h1.spaceAfter = 30
    # estilo para el cuerpo
    styles = getSampleStyleSheet()
    c1 = styles['Normal']
    c1.alignment = TA_LEFT
    c1.leftIndent = 50
    c1.spaceAfter = 20
    c1.fontName = 'Times-Roman'


    header = Paragraph("Grupo %s" %(grupo.get_curso_display() + " " +  grupo.unidad), h1)
    contenido.append(header)

    texto = Paragraph("Tutor/a: %s" % (grupo.tutor.first_name + " " + grupo.tutor.last_name), c1)
    contenido.append(texto)

    t = grupoPorPagina(pk)

    contenido.append(t)

    doc.build(contenido)
    response.write(buff.getvalue())
    buff.close()
    return response

def grupoPorPagina(pk):
    grupo = Grupo.objects.get(pk=pk)

    headings = ['Nombre', 'Edad', 'E-mail']
    info_grupo = [(a.nombre + " " + a.apellido1 + " " + a.apellido2, edad(a.fecha_nacimiento), a.email) for a in Alumno.objects.filter(grupo=grupo)]

    #t = Table([headings] + info_grupo, hAlign='LEFT')
    tabla = Table([headings] + info_grupo)
    tabla.setStyle(TableStyle(
        [
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(0x009688)),  # bordes de las celdas (de grosor 1)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0x009688))
        ]
    ))

    return tabla

def edad(nac):
    diff = (date.today() - nac).days
    years = str(int(diff/365))
    return years

@login_required
def asignaturasPDF(request):

    response = HttpResponse(content_type='application/pdf')
    pdf_name = "asignaturas.pdf"
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            showBoundary=0,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=20,
                            title = "Asignaturas",
                            author = request.user.username,
                            pageBreakQuick = 1,
                            )

    asignaturas = []

    styles = getSampleStyleSheet()
    h1 = styles['Heading1']
    h1.alignment = 1    #centrado
    h1.spaceAfter = 30
    #h1.pageBreakBefore=1
    #h1.backColor=colors.red
    header = Paragraph("Listado de asignaturas", h1)
    asignaturas.append(header)

    headings = ['Nombre', 'Profesor/a', 'Curso', 'Unidad']
    info_asignaturas = [(a.nombre, a.profesor.first_name +" " + a.profesor.last_name, a.grupo.get_curso_display(), a.grupo.unidad) for a in Asignatura.objects.all()]
    t = Table([headings] + info_asignaturas)
    t.setStyle(TableStyle(
        [
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(0x009688)),    # bordes de las celdas (de grosor 1)
            #('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor(0x009688)), # borde inferior (de mayor grosor, 2)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0x009688))  # color de fondo (en este caso, solo la primera fila)
        ]
    ))

    # NOTA de TableStyle: las filas y columnas empiezan en 0. -1 para la ultima posicion (aunque sea desconocida)
    # otras opciones:
    # ('TEXTCOLOR', (0, 0), (-1, -1), colors.blue),
    # ('VALIGN', (0,0), (-1, -1), 'MIDDLE'),

    asignaturas.append(t)

    doc.build(asignaturas)
    response.write(buff.getvalue())
    buff.close()
    return response

@login_required
def asignaturaPDF(request, pk):

    response = HttpResponse(content_type='application/pdf')
    asignatura = Asignatura.objects.get(pk=pk)
    pdf_name = "asignatura-%s.pdf" % asignatura.nombre
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            showBoundary=0,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=20,
                            title = "Asignatura %s" % asignatura.nombre,
                            author = request.user.username,
                            pageBreakQuick = 1,
                            )

    asignatura_content = []

    styles = getSampleStyleSheet()
    h1 = styles['Heading1']
    h1.alignment = 1    #centrado
    h1.spaceAfter = 30
    header = Paragraph("Alumnado de %s" % asignatura.nombre, h1)
    asignatura_content.append(header)

    styles = getSampleStyleSheet()
    c1 = styles['Normal']
    c1.alignment = TA_LEFT
    c1.leftIndent = 50
    c1.spaceAfter = 5
    c1.fontName = 'Times-Roman'
    texto1 = Paragraph("Grupo: %s" % (asignatura.grupo.get_curso_display() + " " +  asignatura.grupo.unidad), c1)
    asignatura_content.append(texto1)

    styles = getSampleStyleSheet()
    c2 = styles['Normal']
    c2.alignment = TA_LEFT
    c2.leftIndent = 50
    c2.spaceAfter = 20
    c2.fontName = 'Times-Roman'
    texto2 = Paragraph("Profesor/a: %s" % (asignatura.profesor.first_name + " " + asignatura.profesor.last_name), c2)
    asignatura_content.append(texto2)

    headings = ['Nombre', 'Edad', 'E-mail']
    info_asignatura = [(a.nombre + " " + a.apellido1 + " " + a.apellido2, edad(a.fecha_nacimiento), a.email) for a in
                  asignatura.alumno_set.all()]

    t = Table([headings] + info_asignatura)
    t.setStyle(TableStyle(
        [
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(0x009688)),    # bordes de las celdas (de grosor 1)
            #('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor(0x009688)), # borde inferior (de mayor grosor, 2)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0x009688))  # color de fondo (en este caso, solo la primera fila)
        ]
    ))

    # NOTA de TableStyle: las filas y columnas empiezan en 0. -1 para la ultima posicion (aunque sea desconocida)
    # otras opciones:
    # ('TEXTCOLOR', (0, 0), (-1, -1), colors.blue),
    # ('VALIGN', (0,0), (-1, -1), 'MIDDLE'),

    asignatura_content.append(t)

    doc.build(asignatura_content)
    response.write(buff.getvalue())
    buff.close()
    return response

def asignaturasGrupoPDF(request, idGrupo):

    response = HttpResponse(content_type='application/pdf')
    grupo = Grupo.objects.get(pk=idGrupo)
    nombre = grupo.get_curso_display()
    if grupo.unidad != "":
        nombre = nombre + " " + grupo.unidad
    pdf_name = "asignaturas-%s.pdf" % nombre.replace(" ", "-")
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            showBoundary=0,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=20,
                            title = "Asignaturas %s" % (grupo.get_curso_display() + " " + grupo.unidad),
                            author = request.user.username,
                            pageBreakQuick = 1,
                            )

    asignaturas = []


    styles = getSampleStyleSheet()
    h1 = styles['Heading1']
    h1.alignment = 1    #centrado
    h1.spaceAfter = 30
    #h1.pageBreakBefore=1
    #h1.backColor=colors.red
    header = Paragraph("Listado de asignaturas impartidas en %s" % (grupo.get_curso_display() + " " + grupo.unidad), h1)
    asignaturas.append(header)

    headings = ['Nombre', 'Profesor/a']
    info_asignaturas = [(a.nombre, a.profesor.first_name +" " + a.profesor.last_name) for a in Asignatura.objects.filter(grupo=grupo)]
    t = Table([headings] + info_asignaturas)
    t.setStyle(TableStyle(
        [
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(0x009688)),    # bordes de las celdas (de grosor 1)
            #('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor(0x009688)), # borde inferior (de mayor grosor, 2)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0x009688))  # color de fondo (en este caso, solo la primera fila)
        ]
    ))

    asignaturas.append(t)

    doc.build(asignaturas)
    response.write(buff.getvalue())
    buff.close()
    return response

def matriculasPDF(request, idGrupo):

    response = HttpResponse(content_type='application/pdf')
    grupo = Grupo.objects.get(pk=idGrupo)
    nombre = grupo.get_curso_display()
    if grupo.unidad != "":
        nombre = nombre + " " + grupo.unidad
    pdf_name = "matriculas-%s.pdf" % nombre.replace(" ", "-")
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4, # en horizontal --> pagesize=landscape(A4),
                            showBoundary=0,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=20,
                            title="Matriculas de %s" % (grupo.get_curso_display() + " " + grupo.unidad),
                            author = request.user.username,
                            pageBreakQuick = 1,
                            )
    contenido = []

    #definicion de estilos
    styles = getSampleStyleSheet()
    #estilo para el titulo de cabecera
    h1 = styles['Heading1']
    h1.alignment = 1  # centrado
    h1.spaceAfter = 30
    #estilo para el pie de pagina
    f1 = styles['Normal']
    f1.alignment = 1  # centrado
    f1.fontName = 'Times-Italic'
    f1.spaceBefore = 20

    header = Paragraph("Matriculas del grupo % s" % (grupo.get_curso_display() + " " + grupo.unidad), h1)
    contenido.append(header)

    matriculas=Matricula.objects.filter(alumno__grupo=grupo).order_by('asignatura').values()

    #se cuenta el numero de asignaturas diferentes (= numero de matriculas de cada alumno)
    key = itemgetter('asignatura_id')
    iter = groupby(sorted(matriculas, key=key), key=key)
    total_asignaturas = 0
    for asig in iter:
        total_asignaturas += 1


    #paginacion de la tabla de matriculas (7 fechas-columnas por pagina)
    num_asignaturas = 0
    num_pagina = 1
    asignatura_list = []
    key = itemgetter('asignatura_id')
    iter = groupby(sorted(matriculas, key=key), key=key)
    for asign in iter:
        num_asignaturas += 1
        asignatura_list.append(asign[0])
        if ((num_asignaturas % 3) == 0 and num_asignaturas < total_asignaturas):   #nueva pagina
            t = matriculasPorPagina(idGrupo, asignatura_list)
            contenido.append(t)
            contenido.append(Paragraph("Pag %d" % num_pagina, f1))
            #salto de pagina
            contenido.append(PageBreak())
            asignatura_list = []
            num_pagina+=1
        elif num_asignaturas == total_asignaturas: #ultima pagina
            t = matriculasPorPagina(idGrupo, asignatura_list)
            contenido.append(t)
            contenido.append(Paragraph("Pag %d" % num_pagina, f1))

    doc.build(contenido)
    response.write(buff.getvalue())
    buff.close()
    return response

def matriculasPorPagina(idGrupo, listaAsignaturas):

    matriculas = Matricula.objects.filter(alumno__grupo__id=idGrupo).order_by('asignatura').values()

    key = itemgetter('asignatura_id')
    iter = groupby(sorted(matriculas, key=key), key=key)

    # CABECERA de la tabla
    headings = ['Alumno/a']
    for asign, lista in iter:
        if asign in listaAsignaturas:
            headings.append(Asignatura.objects.get(pk=asign).nombre)

    # Contenido de la tabla --> anotaciones de cada alumno (uno por fila)
    info_matriculas = []

    for alumno in Grupo.objects.get(pk=idGrupo).alumno_set.all():

        matriculas = Matricula.objects.filter(alumno__grupo__id=idGrupo).order_by('asignatura').values()

        key = itemgetter('asignatura_id')
        iter = groupby(sorted(matriculas, key=key), key=key)

        nombre_completo = alumno.nombre + " " +  alumno.apellido1 + " " + alumno.apellido2

        #elipsis para nombres mayores de 30 caracteres
        if len(nombre_completo) > 30:
            nuevo_nombre = nombre_completo[0:30] + "..."
            nombre_completo = nuevo_nombre

        fila = ["%s" % nombre_completo]

        for asign, lista in iter:

            if asign in listaAsignaturas:

                matricula = ""

                for m in lista:  # lista contiene todas las matriculas de una determinada asignatura

                    if alumno.id == m['alumno_id']:
                        matricula += "X"

                if len(matricula) == 0:
                    matricula = " "

                fila.append(matricula)

        # FIN del bucle con todas las matriculas del alumno


        # FILA COMPLETA
        info_matriculas.append(fila)

    #se han terminado todos los alumnos

    tabla = Table([headings] + info_matriculas)  # , colWidths='50'
    tabla.setStyle(TableStyle(
    [
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(0x009688)),  # bordes de las celdas (de grosor 1)
        #('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),  # borde inferior (de mayor grosor, 2)
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0x009688))  # color de fondo (en este caso, solo la primera fila)
    ]
    ))

    return tabla



@login_required
def anotacionesPDF(request, idAsignatura, inicio, fin):

    response = HttpResponse(content_type='application/pdf')
    pdf_name = "anotaciones-%s.pdf" % Asignatura.objects.get(pk=idAsignatura).nombre
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4, # en horizontal --> pagesize=landscape(A4),
                            showBoundary=0,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=20,
                            title = "Anotaciones de %s" % Asignatura.objects.get(pk=idAsignatura).nombre,
                            author = request.user.username,
                            pageBreakQuick = 1,
                            onPageEnd=pie    #NO FUNCIONA
                            )
    contenido = []

    #definicion de estilos
    styles = getSampleStyleSheet()
    #estilo para el titulo de cabecera
    h1 = styles['Heading1']
    h1.alignment = 1  # centrado
    h1.spaceAfter = 30
    #estilo para el pie de pagina
    f1 = styles['Normal']
    f1.alignment = 1  # centrado
    f1.fontName = 'Times-Italic'
    f1.spaceBefore = 20

    header = Paragraph("Anotaciones de la asignatura % s" % Asignatura.objects.get(pk=idAsignatura).nombre, h1)
    contenido.append(header)

    anotaciones=Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin, asignatura=Asignatura.objects.get(pk=idAsignatura)).order_by('fecha').values()

    #se cuenta el numero de fechas diferentes (= numero de anotaciones de cada alumno)
    key = itemgetter('fecha')
    iter = groupby(sorted(anotaciones, key=key), key=key)
    total_anotaciones = 0
    for fecha in iter:
        total_anotaciones += 1


    #paginacion de la tabla de anotaciones (7 fechas-columnas por pagina)
    num_fechas = 0
    num_pagina = 1
    fecha_list = []
    key = itemgetter('fecha')
    iter = groupby(sorted(anotaciones, key=key), key=key)
    for fecha in iter:
        num_fechas += 1
        fecha_list.append(fecha[0])
        if ((num_fechas % 7) == 0 and num_fechas < total_anotaciones) or ((num_fechas % 7) == 6 and num_fechas == total_anotaciones-1):   #nueva pagina
            t = anotacionesPorPagina(idAsignatura, fecha_list, inicio, fin, False)
            contenido.append(t)
            contenido.append(Paragraph("Pag %d" % num_pagina, f1))
            #salto de pagina
            contenido.append(PageBreak())
            fecha_list = []
            num_pagina+=1
        elif num_fechas == total_anotaciones: #ultima pagina
            t = anotacionesPorPagina(idAsignatura, fecha_list, inicio, fin, True)
            contenido.append(t)
            contenido.append(Paragraph("Pag %d" % num_pagina, f1))

    doc.build(contenido)
    response.write(buff.getvalue())
    buff.close()
    return response


def anotacionesPorPagina(idAsignatura, listaFechas, inicio, fin, ultimaPag):

    anotaciones=Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin, asignatura=Asignatura.objects.get(pk=idAsignatura)).order_by('fecha').values()

    key = itemgetter('fecha')
    iter = groupby(sorted(anotaciones, key=key), key=key)

    # CABECERA de la tabla
    headings = ['Alumno/a']
    for fecha, lista in iter:
        if fecha in listaFechas:
            headings.append(fecha.strftime("%d/%m/%y"))
    if ultimaPag:
        headings.append('RESUMEN')

    # Contenido de la tabla --> anotaciones de cada alumno (uno por fila)
    info_anotaciones = []

    for alumno in Asignatura.objects.get(pk=idAsignatura).alumno_set.all():

        anotaciones = Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin, asignatura=Asignatura.objects.get(pk=idAsignatura)).order_by(
            'fecha').values()

        key = itemgetter('fecha')
        iter = groupby(sorted(anotaciones, key=key), key=key)

        nombre_completo = alumno.nombre + " " +  alumno.apellido1 + " " + alumno.apellido2

        #elipsis para nombres mayores de 30 caracteres
        if len(nombre_completo) > 30:
            nuevo_nombre = nombre_completo[0:30] + "..."
            nombre_completo = nuevo_nombre

        fila = ["%s" % nombre_completo]

        for fecha, lista in iter:

            if fecha in listaFechas:

                anotacion = ""

                for v in lista:  # lista contiene todas las valoraciones en una determinada fecha

                    if alumno.id == v['alumno_id']:
                        if v['falta'] == 'I':
                            anotacion += " I"
                        elif v['falta'] == 'J':
                            anotacion += " J"
                        elif v['falta'] == 'R':
                            anotacion += " R"
                        if v['trabaja']:
                            anotacion += " T"
                        if v['positivos'] is not None and v['positivos'] != 0:
                            anotacion += " %s+" % v['positivos']
                        if v['negativos'] is not None and v['negativos'] !=0:
                            anotacion += " %s-" % v['negativos']

                if len(anotacion) == 0:
                    anotacion = " "

                fila.append(anotacion)

        # FIN del bucle con todas las anotaciones del alumno

        if ultimaPag:
            # se anyade la informacion del resumen
            resumen_list = datosResumen(idAsignatura, inicio, fin)
            resumen_anotaciones = ""
            for resumen in resumen_list:
                if resumen[0] == alumno.id:
                    resumen_anotaciones = "%dI-%dJ-%dR, %dT, %d+, %d-" % (resumen[1], resumen[2], resumen[3], resumen[4], resumen[5], resumen[6])

            fila.append(resumen_anotaciones)

        # FILA COMPLETA
        info_anotaciones.append(fila)

    #se han terminado todos los alumnos

    tabla = Table([headings] + info_anotaciones)  # , colWidths='50'
    if ultimaPag is False:
        tabla.setStyle(TableStyle(
        [
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(0x009688)),  # bordes de las celdas (de grosor 1)
            #('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),  # borde inferior (de mayor grosor, 2)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0x009688))  # color de fondo (en este caso, solo la primera fila)
        ]
        ))
    else:
        tabla.setStyle(TableStyle(
            [
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(0x009688)),  # bordes de las celdas (de grosor 1)
                #('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),  # borde inferior (de mayor grosor, 2)
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0x009688)),
                ('BACKGROUND', (-1, 1), (-1, -1), colors.lightgrey)
                # color de fondo (en este caso, solo la primera fila)
            ]
        ))

    # NOTA de TableStyle: las filas y columnas empiezan en 0. -1 para la ultima posicion (aunque sea desconocida)
    # (columna, fila)
    # otras opciones:
    # ('TEXTCOLOR', (0, 0), (-1, -1), colors.blue),
    # ('VALIGN', (0,0), (-1, -1), 'MIDDLE'),


    return tabla

"""NO FUNCIONA"""
def pie(canvas,doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.restoreState()

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        return line.encode('utf-8')

@login_required
def anotacionesCSV(request, idAsignatura, inicio, fin):

    response = HttpResponse(content_type='text/csv')
    csv_name = "anotaciones-%s.csv" % Asignatura.objects.get(pk=idAsignatura).nombre
    response['Content-Disposition'] = 'attachment; filename=%s' % csv_name

    writer = csv.writer(response)

    anotaciones = Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin,
                                           asignatura=Asignatura.objects.get(pk=idAsignatura)).order_by(
        'fecha').values()

    key = itemgetter('fecha')
    iter = groupby(sorted(anotaciones, key=key), key=key)

    # CABECERA
    headings = ['Alumno/a']
    for fecha,lista in iter:
        headings.append(fecha.strftime("%d/%m/%y"))
    headings.append('RESUMEN')

    writer.writerow(headings)


    # CONTENIDO --> anotaciones de cada alumno (uno por fila)
    for alumno in Asignatura.objects.get(pk=idAsignatura).alumno_set.all():

        anotaciones = Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin,
                                               asignatura=Asignatura.objects.get(pk=idAsignatura)).order_by(
            'fecha').values()

        key = itemgetter('fecha')
        iter = groupby(sorted(anotaciones, key=key), key=key)

        nombre = ['%s %s %s' % (alumno.nombre, alumno.apellido1, alumno.apellido2)]
        fila = []
        fila.append(utf_8_encoder(nombre))

        for fecha, lista in iter:

            anotacion = ""

            for v in lista:  # lista contiene todas las valoraciones en una determinada fecha

                if alumno.id == v['alumno_id']:
                    if v['falta'] == 'I':
                        anotacion += " I"
                    elif v['falta'] == 'J':
                        anotacion += " J"
                    elif v['falta'] == 'R':
                        anotacion += " R"
                    if v['trabaja']:
                        anotacion += " T"
                    if v['positivos'] is not None and v['positivos'] != 0:
                        anotacion += " %s+" % v['positivos']
                    if v['negativos'] is not None and v['negativos'] != 0:
                        anotacion += " %s-" % v['negativos']

            if len(anotacion) == 0:
                anotacion = " "

            fila.append(anotacion)


        # FIN del bucle con todas las anotaciones del alumno

        # se anyade la informacion del resumen
        resumen_list = datosResumen(idAsignatura, inicio, fin)
        resumen_anotaciones = ""
        for resumen in resumen_list:
            if resumen[0] == alumno.id:
                resumen_anotaciones = "%dI-%dJ-%dR %dT %d+ %d-" % (resumen[1], resumen[2], resumen[3], resumen[4], resumen[5], resumen[6])
                #NOTA: no se pueden utilizar comas para separar la informacion de resumen

        fila.append(resumen_anotaciones)


        # FILA COMPLETA
        writer.writerow(fila)

    return response

@login_required
def anotacionesXLS(request, idAsignatura, inicio, fin):

    response = HttpResponse(content_type='text/ms-excel')
    xls_name = "anotaciones-%s.xls" % Asignatura.objects.get(pk=idAsignatura).nombre
    response['Content-Disposition'] = 'attachment; filename=%s' % xls_name

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Anotaciones')

    # ENCABEZADO, primera fila
    num_fila = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.font.colour_index = 0x09
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 0x39
    font_style.pattern = pattern
    font_style.num_format_str = 'DD/MM/YY'  #formato para el objeto date

    anotaciones = Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin,
                                           asignatura=Asignatura.objects.get(pk=idAsignatura)).order_by(
        'fecha').values()

    key = itemgetter('fecha')
    iter = groupby(sorted(anotaciones, key=key), key=key)

    headings = ['Alumno/a']
    for fecha, lista in iter:
        headings.append(fecha)  #se pasa el objeto, y no la cadena
    headings.append('RESUMEN')

    for num_col in range(len(headings)):
        ws.write(num_fila, num_col, headings[num_col], font_style)   #fila 0, columna x, celda a escribir y estilo


    # CONTENIDO --> anotaciones de cada alumno (uno por fila)
    font_style = xlwt.XFStyle()

    for alumno in Asignatura.objects.get(pk=idAsignatura).alumno_set.all():

        num_fila += 1    #nueva fila

        anotaciones = Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin,
                                               asignatura=Asignatura.objects.get(pk=idAsignatura)).order_by(
            'fecha').values()

        key = itemgetter('fecha')
        iter = groupby(sorted(anotaciones, key=key), key=key)

        fila = ['%s %s %s' % (alumno.nombre, alumno.apellido1, alumno.apellido2)]

        for fecha, lista in iter:

            anotacion = ""

            for v in lista:  # lista contiene todas las valoraciones en una determinada fecha

                if alumno.id == v['alumno_id']:
                    if v['falta'] == 'I':
                        anotacion += " I"
                    elif v['falta'] == 'J':
                        anotacion += " J"
                    elif v['falta'] == 'R':
                        anotacion += " R"
                    if v['trabaja']:
                        anotacion += " T"
                    if v['positivos'] is not None and v['positivos'] != 0:
                        anotacion += " %s+" % v['positivos']
                    if v['negativos'] is not None and v['negativos'] != 0:
                        anotacion += " %s-" % v['negativos']

            if len(anotacion) == 0:
                anotacion = " "

            fila.append(anotacion)


        # FIN del bucle con todas las anotaciones del alumno

        # se anyade la informacion del resumen
        resumen_list = datosResumen(idAsignatura, inicio, fin)
        resumen_anotaciones = ""
        for resumen in resumen_list:
            if resumen[0] == alumno.id:
                resumen_anotaciones = "%dI-%dJ-%dR, %dT, %d+, %d-" % (resumen[1], resumen[2], resumen[3], resumen[4], resumen[5], resumen[6])


        fila.append(resumen_anotaciones)


        # FILA COMPLETA --> se escribe celda a celda
        for num_col in range(len(fila)):
            ws.write(num_fila, num_col, fila[num_col], font_style)

    wb.save(response)
    return response

#PROFESORES
#Permisos: todos los profesores
class ProfesorListView(LoginRequiredMixin, ListView):
    model = ProfesorUser
    #paginate_by = 10

#Permiso: todos los profesores
class ProfesorDetailView(LoginRequiredMixin, DetailView):
    model = ProfesorUser

#Permiso: solo superusers
class ProfesorCreate(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = ProfesorUser  # Put model AND form_class, otherwise a User individual is saved
    form_class = RegisterForm
    #fields = ['username', 'password', 'first_name', 'last_name', 'email']
    success_message = 'El docente %(first_name)s %(last_name)s se ha grabado correctamente' # %(field_name)s
    warning_message = 'El docente %(first_name)s %(last_name)s ya se encuentra dado de alta en el sistema'
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para crear nuevos profesores')
        return super(ProfesorCreate, self).handle_no_permission()

    #se evitan profesores duplicados
    def form_valid(self, form):
        first_name = form.instance.first_name
        last_name = form.instance.last_name
        try:
            ya_existe = ProfesorUser.objects.get(first_name=first_name, last_name=last_name)
            if ya_existe is None:
                return super(ProfesorCreate, self).form_valid(form)
            else:
                #profesor ya existente
                messages.warning(self.request, self.warning_message % dict(first_name=first_name,
                                                                           last_name=last_name))
                return HttpResponseRedirect(reverse('lista-profesores'))
        except ObjectDoesNotExist:
            return super(ProfesorCreate, self).form_valid(form)


#Permiso: solo superusers
class ProfesorUpdate(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ProfesorUser
    form_class = ProfesorUpdateForm
    permission_required = 'is_superuser'
    success_message = 'El docente %(first_name)s %(last_name)s  se ha modificado correctamente'
    warning_message = 'Los datos proporcionados ya corresponden al docente %(first_name)s %(last_name)s'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para modificar los detalles del profesorado')
        return super(ProfesorUpdate, self).handle_no_permission()

    #se evitan profesores duplicados (con mismo nombre y apellido)
    def form_valid(self, form):
        first_name = form.instance.first_name
        last_name = form.instance.last_name
        try:
            ya_existe = ProfesorUser.objects.get(first_name=first_name, last_name=last_name)
            if ya_existe is None:
                return super(ProfesorUpdate, self).form_valid(form)
            else:
                #profesor ya existente
                messages.warning(self.request, self.warning_message % dict(first_name=first_name,
                                                                           last_name=last_name))
                return HttpResponseRedirect(reverse('lista-profesores'))
        except ObjectDoesNotExist:
            return super(ProfesorUpdate, self).form_valid(form)

#Permiso: el propio usuario
class UserUpdate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = ProfesorUser
    form_class = UpdateForm
    template_name = 'instituto/user_form.html'
    success_url = reverse_lazy('asignaturas-profesor')

    success_message = 'Su información personal se ha actualizado correctamente'
    warning_message = 'Los datos proporcionados ya corresponden al docente %(first_name)s %(last_name)s'

    # se evitan profesores duplicados (con mismo nombre y apellido)
    def form_valid(self, form):
        first_name = form.instance.first_name
        last_name = form.instance.last_name
        try:
            ya_existe = ProfesorUser.objects.get(first_name=first_name, last_name=last_name)
            if ya_existe is None:
                return super(UserUpdate, self).form_valid(form)
            else:
                # profesor ya existente
                messages.warning(self.request, self.warning_message % dict(first_name=first_name,
                                                                           last_name=last_name))
                return HttpResponseRedirect(reverse('asignaturas-profesor'))
        except ObjectDoesNotExist:
            return super(UserUpdate, self).form_valid(form)

    def test_func(self):
        return (int(self.request.user.id) == int(self.kwargs['pk']))

#Permiso: solo superusers
class ProfesorDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ProfesorUser
    success_url = reverse_lazy('lista-profesores')
    success_message = 'El docente %(first_name)s %(last_name)s  se ha eliminado correctamente'
    warning_message = 'El docente %(first_name)s %(last_name)s  no se ha podido eliminar porque tiene asignaturas o grupos relacionados'

    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para eliminar profesores/as')
        return super(ProfesorDelete, self).handle_no_permission()

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            obj = self.get_object()
            #se borra el mensaje de exito
            storage = messages.get_messages(request)
            for _ in storage:
                pass

            if len(storage._loaded_messages) == 1:
                del storage._loaded_messages[0]

            messages.warning(self.request, self.warning_message % obj.__dict__)
            return HttpResponseRedirect(reverse('lista-profesores'))


    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(ProfesorDelete, self).delete(request, *args, **kwargs)

"""
#PROFESORES TUTORES
#Permisos: todos los profesores
class TutorListView(LoginRequiredMixin,ListView):
    model = ProfesorUser
    template_name = 'instituto/tutor_list_OLD.html'
    paginate_by = 4

    def get_queryset(self):
        queryset = super(TutorListView, self).get_queryset().filter(grupo__isnull=False).order_by('grupo')
        return queryset
"""

#ASIGNATURAS
#Permisos: todos los profesores
class AsignaturaListView(LoginRequiredMixin, ListView):
    model = Asignatura
    #paginate_by = 4

    def get_queryset(self):
        filter_group = self.request.GET.get('grupo', 0)
        try:
            grupo=Grupo.objects.get(pk=filter_group)
            if grupo is None:
                return Asignatura.objects.all()
            else:
                return Asignatura.objects.filter(grupo=grupo)
        except ObjectDoesNotExist:
            return Asignatura.objects.all()

    def get_context_data(self, **kwargs):
        context = super(AsignaturaListView, self).get_context_data(**kwargs)

        filter_group = int(self.request.GET.get('grupo', 0))
        context['filter_group'] = filter_group
        grupos = Grupo.objects.all()
        if filter_group > 0:
            context.update({'grupo_list': grupos, 'grupo': Grupo.objects.get(pk=filter_group)})
        else:
            context.update({'grupo_list': grupos})
        return context



#Permisos: el propio profesor
class AsignaturasProfesorListView(LoginRequiredMixin, ListView):
    model = Asignatura
    template_name = 'instituto/asignatura_profesor_list.html'

    def get_queryset(self):
        queryset = super(AsignaturasProfesorListView, self).get_queryset().filter(profesor=self.request.user)
        #queryset = super(AsignaturasProfesorListView, self).get_queryset().filter(profesor=ProfesorUser.objects.get(pk=self.kwargs['idProfesor']))
        return queryset

    #se le pasa la fecha actual para poder mostrar el detalle de cada asignatura
    def get_context_data(self, **kwargs):
        context = super(AsignaturasProfesorListView, self).get_context_data(**kwargs)
        context.update({'fecha': date.today().strftime('%d/%m/%Y')})
        return context


#Permisos: todos los profesores
class AsignaturaDetailView(LoginRequiredMixin, DetailView):
    model = Asignatura

#Permisos: el propio profesor
class AsignaturaCuadView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Asignatura
    template_name = 'instituto/asignatura_detail_cuad.html'

    def get_context_data(self, **kwargs):
        context = super(AsignaturaCuadView, self).get_context_data(**kwargs)
        fecha = datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y')
        if fecha.strftime('%A') == "Saturday" or fecha.strftime('%A') == "Sunday":
            lectivo = False
        else:
            lectivo = True

        alumnado = Asignatura.objects.get(pk=self.kwargs['pk']).alumno_set.order_by('matricula__orden')

        anotaciones = Anotacion.objects.filter(fecha=fecha,asignatura=Asignatura.objects.get(pk=self.kwargs['pk']))

        columnas = Asignatura.objects.get(pk=self.kwargs['pk']).distribucion

        context.update({'vista':"cuad",'alumnado_list':alumnado, 'anotacion_list': anotaciones, 'fecha': self.kwargs['fecha'], 'lectivo': lectivo, 'cols': columnas})
        return context

    def test_func(self):
        return (int(self.request.user.id) == int(Asignatura.objects.get(pk=self.kwargs['pk']).profesor.id))

#Permisos: el propio profesor
class AsignaturaListaView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Asignatura
    template_name = 'instituto/asignatura_detail_lista.html'

    def get_context_data(self, **kwargs):
        context = super(AsignaturaListaView, self).get_context_data(**kwargs)
        fecha = datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y')
        if fecha.strftime('%A') == "Saturday" or fecha.strftime('%A') == "Sunday":
            lectivo = False
        else:
            lectivo = True

        anotaciones = Anotacion.objects.filter(fecha=fecha,asignatura=Asignatura.objects.get(pk=self.kwargs['pk']))

        context.update({'vista':"lista",'anotacion_list': anotaciones, 'fecha': self.kwargs['fecha'], 'lectivo': lectivo})
        return context

    def test_func(self):
        return (int(self.request.user.id) == int(Asignatura.objects.get(pk=self.kwargs['pk']).profesor.id))

#Permiso: solo superusers
class AsignaturaCreate(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Asignatura
    fields = '__all__'
    success_message = 'La asignatura %(nombre)s se ha grabado correctamente'
    warning_message = 'Ya existe la asignatura %(nombre)s en %(curso)s %(unidad)s. Utilice un nombre diferente.'
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para crear nuevas asignaturas')
        return super(AsignaturaCreate, self).handle_no_permission()

    #se evitan asignaturas duplicadas
    def form_valid(self, form):
        nombre = form.instance.nombre
        grupo = form.instance.grupo
        try:
            ya_existe = Asignatura.objects.get(nombre=nombre, grupo=grupo)
            if ya_existe is None:
                return super(AsignaturaCreate, self).form_valid(form)
            else:
                #asignatura ya existente
                messages.warning(self.request, self.warning_message % dict(nombre=nombre,
                                                                           curso=grupo.get_curso_display(),
                                                                           unidad=grupo.unidad))
                return HttpResponseRedirect(reverse('lista-asignaturas'))
        except ObjectDoesNotExist:
            return super(AsignaturaCreate, self).form_valid(form)

#Permiso: solo superusers y el propio profesor
class AsignaturaUpdate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Asignatura
    fields = '__all__'
    success_message = 'La asignatura %(nombre)s se ha modificado correctamente'
    warning_message = 'Problemas al actualizar: ya existe la asignatura %(nombre)s en %(curso)s %(unidad)s. Utilice un nombre diferente.'

    # se evitan asignaturas duplicadas
    def form_valid(self, form):
        nombre = form.instance.nombre
        grupo = form.instance.grupo
        try:
            ya_existe = Asignatura.objects.get(nombre=nombre, grupo=grupo)
            if ya_existe is None:
                return super(AsignaturaUpdate, self).form_valid(form)
            else:
                # asignatura ya existente
                messages.warning(self.request, self.warning_message % dict(nombre=nombre,
                                                                           curso=grupo.get_curso_display(),
                                                                           unidad=grupo.unidad))
                return HttpResponseRedirect(reverse('lista-asignaturas'))
        except ObjectDoesNotExist:
            return super(AsignaturaUpdate, self).form_valid(form)

    def test_func(self):
        return (self.request.user.is_superuser or int(self.request.user.id) == int(Asignatura.objects.get(pk=self.kwargs['pk']).profesor.id))

#Permiso: solo superusers
class AsignaturaDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Asignatura
    success_url = reverse_lazy('lista-asignaturas')
    success_message = 'La asignatura %(nombre)s se ha eliminado correctamente'
    warning_message = 'La asignatura %(nombre)s  no se ha podido eliminar porque tiene alumnado matriculado'
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para eliminar asignaturas')
        return super(AsignaturaDelete, self).handle_no_permission()


    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            obj = self.get_object()
            # se borra el mensaje de exito
            storage = messages.get_messages(request)
            for _ in storage:
                pass

            if len(storage._loaded_messages) == 1:
                del storage._loaded_messages[0]

            messages.warning(self.request, self.warning_message % obj.__dict__)
            return HttpResponseRedirect(reverse('lista-asignaturas'))

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(AsignaturaDelete, self).delete(request, *args, **kwargs)

#GRUPOS
#Permisos: todos los profesores
class GrupoListView(LoginRequiredMixin, ListView):
    model = Grupo
    #paginate_by = 4

#Permisos: todos los profesores
class GrupoDetailView(LoginRequiredMixin, DetailView):
    model = Grupo

# Permisos: el propio tutor
class GrupoTutorDetailView(LoginRequiredMixin, DetailView):
    model = Grupo
    template_name = 'instituto/tutoria_detail.html'

    def get_object(self):
        #NOTA: el grupo debe ser único, pero puede no existir. Si se usa el método get, podrá lanzar el error DoesNotExist.
        return Grupo.objects.filter(tutor=self.request.user).first()

    """#se le pasa la vista actual
    def get_context_data(self, **kwargs):
        context = super(GrupoTutorDetailView, self).get_context_data(**kwargs)
        context.update({'vista': self.kwargs['vista']})
        return context"""


#Permiso: solo superusers
class GrupoCreate(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Grupo
    fields = '__all__'
    success_message = 'El grupo %(curso_elegido)s %(unidad)s se ha grabado correctamente'
    warning_message = 'Ya existe el grupo %(curso)s %(unidad)s en el centro'
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para crear nuevos grupos')
        return super(GrupoCreate, self).handle_no_permission()

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            curso_elegido=self.object.get_curso_display(),
        )

    #se evitan grupos duplicados
    def form_valid(self, form):
        curso = form.instance.curso
        unidad = form.instance.unidad
        try:
            ya_existe = Grupo.objects.get(curso=curso, unidad=unidad)
            if ya_existe is None:
                return super(GrupoCreate, self).form_valid(form)
            else:
                #grupo ya existente
                messages.warning(self.request, self.warning_message % dict(curso=form.instance.get_curso_display(),
                                                                           unidad=unidad))
                return HttpResponseRedirect(reverse('lista-grupos'))
        except ObjectDoesNotExist:
            return super(GrupoCreate, self).form_valid(form)

#Permiso: solo superusers
class GrupoUpdate(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Grupo
    fields = '__all__'
    success_message = 'El grupo %(curso_elegido)s %(unidad)s se ha modificado correctamente'
    warning_message = 'Problemas al actualizar: ya existe el grupo %(curso)s %(unidad)s en el centro'
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para modificar los grupos')
        return super(GrupoUpdate, self).handle_no_permission()

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            curso_elegido=self.object.get_curso_display(),
        )
    #se evitan grupos duplicados
    def form_valid(self, form):
        curso = form.instance.curso
        unidad = form.instance.unidad
        try:
            ya_existe = Grupo.objects.get(curso=curso, unidad=unidad)
            if ya_existe is None:
                return super(GrupoUpdate, self).form_valid(form)
            else:
                #grupo ya existente
                messages.warning(self.request, self.warning_message % dict(curso=form.instance.get_curso_display(),
                                                                           unidad=unidad))
                return HttpResponseRedirect(reverse('lista-grupos'))
        except ObjectDoesNotExist:
            return super(GrupoUpdate, self).form_valid(form)

#Permiso: solo superusers
class GrupoDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Grupo
    success_url = reverse_lazy('lista-grupos')
    success_message = 'El grupo %(curso_elegido)s %(unidad_elegida)s se ha eliminado correctamente'
    warning_message = 'El grupo %(curso_elegido)s %(unidad_elegida)s no se ha podido eliminar porque tiene asignaturas o alumnado relacionado'
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para eliminar grupos')
        return super(GrupoDelete, self).handle_no_permission()

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            obj = self.get_object()
            # se borra el mensaje de exito
            storage = messages.get_messages(request)
            for _ in storage:
                pass

            if len(storage._loaded_messages) == 1:
                del storage._loaded_messages[0]

            messages.warning(self.request, self.warning_message % dict(curso_elegido=obj.get_curso_display(),unidad_elegida=obj.unidad))
            return HttpResponseRedirect(reverse('lista-grupos'))

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % dict(curso_elegido=obj.get_curso_display(),unidad_elegida=obj.unidad))
        return super(GrupoDelete, self).delete(request, *args, **kwargs)


#ALUMNOS
#Permisos: todos los profesores
class AlumnoListView(LoginRequiredMixin, ListView):
    model = Alumno
    #paginate_by = 10

    def get_queryset(self):
        filter_group = self.request.GET.get('grupo', 0)
        try:
            grupo=Grupo.objects.get(pk=filter_group)
            if grupo is None:
                return Alumno.objects.all().order_by('grupo', 'apellido1', 'apellido2', 'nombre')
            else:
                return Alumno.objects.filter(grupo=grupo).order_by('grupo', 'apellido1', 'apellido2', 'nombre')
        except ObjectDoesNotExist:
            return Alumno.objects.all().order_by('grupo', 'apellido1', 'apellido2', 'nombre')


    def get_context_data(self, **kwargs):
        context = super(AlumnoListView, self).get_context_data(**kwargs)
        filter_group = int(self.request.GET.get('grupo', 0))
        context['filter_group'] = filter_group
        grupos = Grupo.objects.all()
        if filter_group > 0:
            context.update({'grupo_list': grupos, 'grupo': Grupo.objects.get(pk=filter_group)})
        else:
            context.update({'grupo_list': grupos})
        return context



#Permisos: todos los profesores
class AlumnoDetailView(LoginRequiredMixin, DetailView):
    model = Alumno

class AlumnoTutoriaDetailView(LoginRequiredMixin, DetailView):
    model = Alumno
    template_name = 'instituto/alumno_tutoria_detail.html'

class AlumnoGrupoDetailView(LoginRequiredMixin, DetailView):
    model = Alumno
    template_name = 'instituto/alumno_grupo_detail.html'

#Permiso: solo superusers
class AlumnoCreate(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Alumno
    fields = ['nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo']
    success_message = 'El alumno %(nombre)s %(apellido1)s %(apellido2)s se ha grabado correctamente'
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para crear nuevo alumnado')
        return super(AlumnoCreate, self).handle_no_permission()

#Permiso: solo superusers y el profesor/a tutor
class AlumnoUpdate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Alumno
    fields = ['nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo']
    success_message = 'El alumno %(nombre)s %(apellido1)s %(apellido2)s se ha modificado correctamente'

    def test_func(self):
        return (self.request.user.is_superuser or
                int(self.request.user.id) == int(Alumno.objects.get(pk=self.kwargs['pk']).grupo.tutor_id))

#Permiso: solo superusers y el profesor/a tutor
class AlumnoTutoriaUpdate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Alumno
    template_name = 'instituto/alumno_tutoria_form.html'
    fields = ['nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo']
    success_message = 'El alumno %(nombre)s %(apellido1)s %(apellido2)s se ha modificado correctamente'

    def get_success_url(self):
        return reverse('detalle-alumno-tutoria', kwargs={'pk': self.kwargs['pk']})

    def test_func(self):
        return (self.request.user.is_superuser or
                int(self.request.user.id) == int(Alumno.objects.get(pk=self.kwargs['pk']).grupo.tutor_id))

#Permiso: solo superusers y el profesor/a tutor
class AlumnoGrupoUpdate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Alumno
    template_name = 'instituto/alumno_grupo_form.html'
    fields = ['nombre', 'apellido1', 'apellido2', 'fecha_nacimiento', 'email', 'foto', 'grupo']
    success_message = 'El alumno %(nombre)s %(apellido1)s %(apellido2)s se ha modificado correctamente'

    def get_success_url(self):
        return reverse('detalle-alumno-grupo', kwargs={'pk': self.kwargs['pk']})

    def test_func(self):
        return (self.request.user.is_superuser or
                int(self.request.user.id) == int(Alumno.objects.get(pk=self.kwargs['pk']).grupo.tutor_id))

#Permiso: solo superusers
class AlumnoDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Alumno
    success_url = reverse_lazy('lista-alumnos')
    success_message = 'El alumno %(nombre)s %(apellido1)s %(apellido2)s se ha eliminado correctamente'
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para eliminar alumnado')
        return super(AlumnoDelete, self).handle_no_permission()

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(AlumnoDelete, self).delete(request, *args, **kwargs)

# MATRICULAS
#Permiso: solo superusers
class MatriculaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Matricula
    #paginate_by = 10
    permission_required = 'is_superuser'

    def get_queryset(self):
        filter_group = self.request.GET.get('grupo', 1)
        try:
            grupo=Grupo.objects.get(pk=filter_group)
            if grupo is None:
                return Matricula.objects.all()
            else:
                return Matricula.objects.filter(alumno__grupo=grupo)
        except ObjectDoesNotExist:
            return Matricula.objects.all()


    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para visualizar las matrículas del alumnado')
        return super(MatriculaListView, self).handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super(MatriculaListView, self).get_context_data(**kwargs)
        context['filter_group'] = int(self.request.GET.get('grupo', 1))
        grupos = Grupo.objects.all()
        try:
            grupo=Grupo.objects.get(pk=int(self.request.GET.get('grupo', 1)))
            if grupo is None:
                alumnos = Alumno.objects.all()
                context.update({'grupo_list': grupos, 'alumno_list': alumnos})
            else:
                alumnos = Alumno.objects.filter(grupo=grupo)
                context.update({'grupo_list': grupos, 'alumno_list': alumnos, 'grupo': grupo})
        except ObjectDoesNotExist:
            alumnos = Alumno.objects.all()
            context.update({'grupo_list': grupos, 'alumno_list': alumnos})

        return context

"""#Permiso: solo superusers
class MatriculaDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Matricula
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para obtener los detalles de la matrícula')
        return super(MatriculaDetailView, self).handle_no_permission()

#Permiso: solo superusers
class MatriculaCreate(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Matricula
    fields = ['alumno', 'asignatura']
    success_message = 'El alumno/a %(nombre_alumno)s %(apellido1_alumno)s %(apellido2_alumno)s se ha matriculado correctamente en %(nombre_asignatura)s'  # %(field_name)s
    warning_message = 'El alumno/a %(nombre_alumno)s %(apellido1_alumno)s %(apellido2_alumno)s ya se encuentra matriculado en %(nombre_asignatura)s'
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para crear nuevas matrículas')
        return super(MatriculaCreate, self).handle_no_permission()

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data, nombre_alumno=self.object.alumno.nombre,
                                           apellido1_alumno=self.object.alumno.apellido1,
            apellido2_alumno=self.object.alumno.apellido2, nombre_asignatura=self.object.asignatura.nombre)

    #se evitan matriculas duplicadas
    def form_valid(self, form):
        alumno = form.instance.alumno
        asignatura = form.instance.asignatura
        try:
            ya_matriculado = Matricula.objects.get(alumno=alumno, asignatura=asignatura)
            if ya_matriculado is None:
                return super(MatriculaCreate, self).form_valid(form)
            else:
                #alumno ya matriculado
                messages.warning(self.request, self.warning_message % dict(nombre_alumno=alumno.nombre,
                                                                           apellido1_alumno=alumno.apellido1,
                                                                           apellido2_alumno=alumno.apellido2,
                                                                           nombre_asignatura=asignatura.nombre))
                return HttpResponseRedirect(reverse('lista-matriculas'))
        except ObjectDoesNotExist:
            return super(MatriculaCreate, self).form_valid(form)
"""

@login_required
@permission_required('is_superuser')
def matricularGrupo(request, idGrupo):

    if request.method == 'POST':
        form = MatriculaForm(request.POST, idGrupo=idGrupo)

        if form.is_valid():

            alumnos = request.POST.getlist('alumnos')
            asignaturas = request.POST.getlist('asignaturas')

            matriculas_nuevas = ""
            matriculas_previas = ""

            for subject in asignaturas:
                asignatura = Asignatura.objects.get(pk=subject)

                for student in alumnos:
                    alumno = Alumno.objects.get(pk=student)

                    try:
                        ya_matriculado = Matricula.objects.get(alumno=alumno, asignatura=asignatura)

                        if ya_matriculado is None:
                            nueva_matricula = Matricula(asignatura=asignatura, alumno=alumno)
                            nueva_matricula.save()
                            if matriculas_nuevas == "":
                                matriculas_nuevas = "Nuevas matriculas: "
                            matriculas_nuevas += " %s - %s, " % (alumno.nombre + " " + alumno.apellido1, asignatura.nombre)
                        else:
                            # alumno ya matriculado
                            if matriculas_previas == "":
                                matriculas_previas = "Alumnado que ya estaba matriculado: "
                            matriculas_previas += " %s - %s, " % (alumno.nombre + " " + alumno.apellido1, asignatura.nombre)
                    except ObjectDoesNotExist:
                        nueva_matricula = Matricula(asignatura=asignatura, alumno=alumno)
                        nueva_matricula.save()
                        if matriculas_nuevas == "":
                            matriculas_nuevas = "Nuevas matriculas: "
                        matriculas_nuevas += " %s - %s, " % (alumno.nombre + " " + alumno.apellido1, asignatura.nombre)

            if matriculas_nuevas != "":
                messages.add_message(request, messages.SUCCESS, matriculas_nuevas)
            if matriculas_previas != "":
                messages.add_message(request, messages.WARNING, matriculas_previas)
            url = "%s?grupo=%s" % (reverse('lista-matriculas'), idGrupo)
            return HttpResponseRedirect(url)

    else:
        form = MatriculaForm(idGrupo=idGrupo)

    if int(idGrupo) > 0:
        grupo = Grupo.objects.get(pk=idGrupo)
        return render(request, 'instituto/matricula_form.html', {'form': form, 'idGrupo': idGrupo, 'grupo': grupo})
    else:
        return render(request, 'instituto/matricula_form.html', {'form': form, 'idGrupo': idGrupo})


"""#Permiso: solo superusers
class MatriculaUpdate(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Matricula
    fields = ['alumno', 'asignatura']
    success_message = 'Se ha modificado correctamente la matricula del alumno/a %(nombre_alumno)s %(apellido1_alumno)s %(apellido2_alumno)s  en %(nombre_asignatura)s'  # %(field_name)s
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para editar matrículas')
        return super(MatriculaUpdate, self).handle_no_permission()

    def get_success_message(self, cleaned_data):
        alumno = self.object.alumno
        asignatura = self.object.asignatura
        return self.success_message % dict(nombre_alumno=alumno.nombre,
                                           apellido1_alumno=alumno.apellido1, apellido2_alumno=alumno.apellido2,
                                           nombre_asignatura=asignatura.nombre)
"""

# Permiso: solo superusers
class MatriculaDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Matricula
    success_url = reverse_lazy('lista-matriculas')
    success_message = 'La matricula del alumno/a %(nombre_alumno)s %(apellido1_alumno)s %(apellido2_alumno)s  en %(nombre_asignatura)s se ha eliminado correctamente'  # %(field_name)s
    permission_required = 'is_superuser'

    def handle_no_permission(self):
        messages.warning(self.request, 'No tiene permiso para eliminar matrículas')
        return super(MatriculaDelete, self).handle_no_permission()

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % dict(nombre_alumno=obj.alumno.nombre, apellido1_alumno=obj.alumno.apellido1,
                                                                   apellido2_alumno=obj.alumno.apellido2, nombre_asignatura=obj.asignatura.nombre))
        return super(MatriculaDelete, self).delete(request, *args, **kwargs)


# ANOTACIONES

"""
    IMPORTANTE:
    puede que no sea necesaria esta clase

class AnotacionListView(LoginRequiredMixin, ListView):
    model = Anotacion

    def get_queryset(self):
        #inicio = datetime.strptime(self.kwargs['inicio'], '%d/%m/%Y')
        #fin = datetime.strptime(self.kwargs['fin'], '%d/%m/%Y')
        #queryset = super(AnotacionListView, self).get_queryset().filter(fecha__gte=inicio, fecha__lte=fin, asignatura=Asignatura.objects.get(pk=self.kwargs['idAsignatura'])).order_by('fecha', 'alumno')
        queryset = super(AnotacionListView, self).get_queryset().filter(asignatura=Asignatura.objects.get(pk=self.kwargs['idAsignatura'])).order_by('fecha', 'alumno')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AnotacionListView, self).get_context_data(**kwargs)

        inicio = Anotacion.objects.filter(asignatura=Asignatura.objects.get(pk=self.kwargs['idAsignatura'])).order_by('fecha').first().fecha
        fin = Anotacion.objects.filter(asignatura=Asignatura.objects.get(pk=self.kwargs['idAsignatura'])).order_by('-fecha').first().fecha
        resumen = datosResumen(self.kwargs['idAsignatura'], inicio, fin)

        fecha = datetime.strftime(date.today(), '%d/%m/%Y')

        context.update({'fecha': fecha, 'idAsignatura': self.kwargs['idAsignatura'],'alumno_list': Asignatura.objects.get(pk=self.kwargs['idAsignatura']).alumno_set.all, 'resumen_list':resumen })
        return context
"""

def validate_own_user(user, asignatura):
    # performing some custom type of logic
    if user.id != Asignatura.objects.get(pk=asignatura).profesor_id:
        raise PermissionDenied

#Permisos: el propio profesor
@login_required
def anotacionesFechas(request, idAsignatura, vista):
    #se valida el usuario (si no es una de sus asignaturas, se lanza error 403)
    validate_own_user(request.user, idAsignatura)
    error = False
    mensaje_error = ""
    asignatura = Asignatura.objects.get(pk=idAsignatura)
    fecha = datetime.strftime(date.today(), '%d/%m/%Y')

    if 'inicio' in request.POST and 'fin' in request.POST:
        f_inicio = request.POST['inicio']
        f_fin = request.POST['fin']
        try:
            inicio = datetime.strptime(f_inicio, '%d/%m/%Y')
            fin = datetime.strptime(f_fin, '%d/%m/%Y')
            resumen = datosResumen(idAsignatura, inicio, fin)
            anotaciones= Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin,
                                  asignatura=Asignatura.objects.get(pk=idAsignatura)).order_by('fecha','alumno')

            if anotaciones.count() == 0:    #no existen anotaciones en esas fechas
                error = True
                mensaje_error = "No existen anotaciones en las fechas indicadas. Por favor, inténtelo de nuevo."
            elif "ver_anotaciones" in request.POST:
                return render(request, 'instituto/anotacion_list.html', {'fecha': fecha, 'vista': vista, 'object_list':anotaciones, 'nombreAsignatura': asignatura.nombre, 'idAsignatura': idAsignatura,'alumno_list': asignatura.alumno_set.all, 'resumen_list':resumen })
            elif "anotaciones_pdf" in request.POST:
                #return HttpResponseRedirect(reverse('anotaciones-pdf', args=(idAsignatura)))
                return anotacionesPDF(request, idAsignatura, inicio, fin)
            elif "anotaciones_csv" in request.POST:
                return anotacionesCSV(request, idAsignatura, inicio, fin)
            elif "anotaciones_xls" in request.POST:
                return anotacionesXLS(request, idAsignatura, inicio, fin)

        except ValueError:
            error = True
            mensaje_error = "Por favor, introduzca fechas de inicio y fin validas."


    return render(request, 'instituto/fechas_anotaciones_form.html', {'error':error, 'mensaje_error':mensaje_error, 'vista': vista, 'nombreAsignatura': asignatura.nombre, 'idAsignatura':idAsignatura, 'fecha': fecha})

def datosResumen(idAsignatura, inicio, fin):

    asignatura = Asignatura.objects.get(pk=idAsignatura)
    resumen_anotaciones = [] #lista de listas
    for alumno in asignatura.alumno_set.all():
        numInjustificadas = 0
        numJustificadas = 0
        numRetrasos = 0
        numTrabaja = 0
        numPositivos = 0
        numNegativos = 0

        for anotacion in Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin, asignatura=idAsignatura):
            if (anotacion.alumno_id == alumno.id):
                if (anotacion.falta=='I'):
                    numInjustificadas+=1
                elif (anotacion.falta == 'J'):
                    numJustificadas += 1
                elif (anotacion.falta == 'R'):
                    numRetrasos += 1
                if (anotacion.trabaja):
                    numTrabaja+=1
                if (anotacion.positivos is not None):
                    numPositivos+=anotacion.positivos
                if (anotacion.negativos is not None):
                    numNegativos+=anotacion.negativos

        #se anyade una sublista con la informacion del alumno
        resumen_anotaciones.append([alumno.id, numInjustificadas, numJustificadas, numRetrasos, numTrabaja, numPositivos, numNegativos])

    return resumen_anotaciones

#Vista para redirigir y decidir si crear una nueva anotacion o editar la ya existente --> debe haber una anotacion por alumno, asignatura y fecha
# Permiso: solo el propio profesor
class AnotacionCreateUpdate(LoginRequiredMixin, UserPassesTestMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            anotacion=Anotacion.objects.filter(fecha=datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y'), alumno=Alumno.objects.get(pk=kwargs['idAlumno']), asignatura=Asignatura.objects.get(pk=kwargs['idAsignatura'])).first()
            if anotacion is None:
                return reverse('nueva-anotacion', kwargs={'idAlumno': kwargs['idAlumno'], 'idAsignatura': kwargs['idAsignatura'], 'vista': kwargs['vista'], 'fecha': self.kwargs['fecha']})
            else:
                return reverse('editar-anotacion', kwargs={'pk': anotacion.id, 'vista': kwargs['vista']})
        except ObjectDoesNotExist:
            return reverse('nueva-anotacion', kwargs={'idAlumno': kwargs['idAlumno'], 'idAsignatura': kwargs['idAsignatura'], 'vista': kwargs['vista'], 'fecha': self.kwargs['fecha']})

    def test_func(self):
        return (int(self.request.user.id) == int(Asignatura.objects.get(pk=self.kwargs['idAsignatura']).profesor.id))

class AjaxTemplateMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'ajax_template_name'):
            split = self.template_name.split('.html')
            split[-1] = '_inner'
            split.append('.html')
            self.ajax_template_name = ''.join(split)
        if request.is_ajax():
            self.template_name = self.ajax_template_name

        return super(AjaxTemplateMixin, self).dispatch(request, *args, **kwargs)

# Permiso: solo el propio profesor
class AnotacionCreate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, AjaxTemplateMixin, CreateView):
    model = Anotacion
    template_name = 'instituto/anotacion_form_create.html'
    fields = ['falta', 'trabaja', 'positivos', 'negativos']
    #success_message = '[%(fecha_str)s] Anotacion del alumno %(nombre_alumno)s %(apellido1_alumno)s %(apellido2_alumno)s grabada correctamente'

    """def get_success_message(self, cleaned_data):
        alumno = Alumno.objects.get(pk=self.kwargs['idAlumno'])
        return self.success_message % dict(fecha_str=self.kwargs['fecha'],nombre_alumno=alumno.nombre, apellido1_alumno=alumno.apellido1, apellido2_alumno=alumno.apellido2)
    """

    def get_context_data(self, **kwargs):
        context = super(AnotacionCreate, self).get_context_data(**kwargs)
        context.update({'fecha': self.kwargs['fecha'], 'alumno': self.kwargs['idAlumno'], 'asignatura': self.kwargs['idAsignatura'], 'vista': self.kwargs['vista']})
        return context

    def get_success_url(self):
        if self.kwargs['vista'] == "cuad":
            return reverse('detalle-asignatura-cuad', kwargs={'pk': self.kwargs['idAsignatura'], 'fecha': self.kwargs['fecha']})
        else:
            return reverse('detalle-asignatura-lista',
                           kwargs={'pk': self.kwargs['idAsignatura'], 'fecha': self.kwargs['fecha']})

    def form_valid(self, form):
        form.instance.alumno = Alumno.objects.get(pk=self.kwargs['idAlumno'])
        form.instance.asignatura = Asignatura.objects.get(pk=self.kwargs['idAsignatura'])
        form.instance.fecha = datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y')
        return super(AnotacionCreate, self).form_valid(form)

    def test_func(self):
        return (int(self.request.user.id) == int(Asignatura.objects.get(pk=self.kwargs['idAsignatura']).profesor.id))

# Permiso: solo el propio profesor
class AnotacionUpdate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, AjaxTemplateMixin, UpdateView):
    model = Anotacion
    template_name = 'instituto/anotacion_form_update.html'
    fields = ['falta', 'trabaja', 'positivos', 'negativos']
    #success_message = '[%(fecha_str)s] Anotacion del alumno %(nombre_alumno)s %(apellido1_alumno)s %(apellido2_alumno)s editada correctamente'

    """def get_success_message(self, cleaned_data):
        obj = self.get_object()
        return self.success_message % dict(fecha_str=datetime.strftime(obj.fecha, '%d/%m/%Y'), nombre_alumno=obj.alumno.nombre, apellido1_alumno=obj.alumno.apellido1, apellido2_alumno=obj.alumno.apellido2)
    """

    #a partir del pk de anotacion pasado en la url, se obtiene el alumno y la asignatura y se anaden al contexto con el que renderizara la plantilla
    def get_context_data(self, **kwargs):
        context = super(AnotacionUpdate, self).get_context_data(**kwargs)
        context.update({'vista':self.kwargs['vista'], 'fecha':datetime.strftime(Anotacion.objects.get(id=self.kwargs['pk']).fecha, '%d/%m/%Y'), 'alumno': Anotacion.objects.get(id=self.kwargs['pk']).alumno_id, 'asignatura': Anotacion.objects.get(id=self.kwargs['pk']).asignatura_id})
        return context

    def get_success_url(self):
        if self.kwargs['vista'] == "cuad":
            return reverse('detalle-asignatura-cuad', kwargs={'pk': Anotacion.objects.get(id=self.kwargs['pk']).asignatura_id, 'fecha':datetime.strftime(Anotacion.objects.get(id=self.kwargs['pk']).fecha, '%d/%m/%Y')})
        elif self.kwargs['vista'] == "lista":
            return reverse('detalle-asignatura-lista',
                           kwargs={'pk': Anotacion.objects.get(id=self.kwargs['pk']).asignatura_id, 'fecha':datetime.strftime(Anotacion.objects.get(id=self.kwargs['pk']).fecha, '%d/%m/%Y')})
        else:
            return reverse('td-anotacion', kwargs={'pk': self.kwargs['pk']})

    def test_func(self):
        return (int(self.request.user.id) == int(Anotacion.objects.get(id=self.kwargs['pk']).asignatura.profesor.id))


# Permiso: solo el propio profesor
#Esta vista se utiliza para ver el resultado de la anotación editada desde la tabla de anotaciones
class AnotacionTdContent(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Anotacion
    template_name = 'instituto/anotacion_td_content.html'

    def test_func(self):
        return (int(self.request.user.id) == int(Anotacion.objects.get(pk=self.kwargs['pk']).asignatura.profesor.id))



"""#NO SE UTILIZA pero SI FUNCIONA (puede utilizarle con la URL)
# Permisos: solo el propio profesor
class AnotacionDelete(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Anotacion
    #success_url = reverse_lazy('detalle-asignatura', kwargs={'pk': Anotacion.objects.get(pk=self.kwargs['pk']).asignatura_id}) #comprobar
    success_message = 'Anotacion elimanada correctamente'

    def get_success_url(self):
        return reverse_lazy('detalle-asignatura-cuad', kwargs={'pk': Anotacion.objects.get(pk=self.kwargs['pk']).asignatura_id, 'fecha': datetime.strftime(Anotacion.objects.get(id=self.kwargs['pk']).fecha, '%d/%m/%Y')})

    def get_context_data(self, **kwargs):
        context = super(AnotacionDelete, self).get_context_data(**kwargs)
        context.update({'fecha':datetime.strftime(Anotacion.objects.get(id=self.kwargs['pk']).fecha, '%d/%m/%Y')})
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(AnotacionDelete, self).delete(request, *args, **kwargs)

    def test_func(self):
        return (int(self.request.user.id) == int(Anotacion.objects.get(pk=self.kwargs['pk']).asignatura.profesor.id))
"""

#Vistas para crear anotaciones individuales
@login_required
@csrf_exempt
def ponerFalta(request, idAlumno, idAsignatura, vista, fecha):
    # se borran los alumnos seleccionados, si los hubiera
    request.session['lista'] = []

    try:
        anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            #La primera vez es falta injustificada
            anotacion = Anotacion(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), falta='I')
            anotacion.save()
        else:
            anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            falta = anotacion.first().falta
            #se indica el siguiente tipo de falta, siguiendo el orden I, J, R, nada
            if(falta=='I'):
                anotacion.update(falta='J')
            elif(falta=='J'):
                anotacion.update(falta='R')
            elif (falta == 'R'):
                anotacion.update(falta='')
            else:
                anotacion.update(falta='I')


    except ObjectDoesNotExist:
        pass

    if vista == "cuad":
        return HttpResponseRedirect(reverse('detalle-asignatura-cuad', args=(idAsignatura, fecha)))
    else:
        return HttpResponseRedirect(reverse('detalle-asignatura-lista', args=(idAsignatura, fecha)))


#funcion para poner falta injustificada al alumno (la tenga o no la tenga ya). No redirige
@login_required
def falta(request, idAlumno, idAsignatura, fecha):

    try:
        anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), falta='I')
            anotacion.save()
        else:
            anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            anotacion.update(falta='I')

    except ObjectDoesNotExist:
        pass

@login_required
@csrf_exempt
def ponerTrabaja(request, idAlumno, idAsignatura, vista, fecha):

    # se borran los alumnos seleccionados, si los hubiera
    request.session['lista'] = []

    try:
        anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), trabaja=True)
            anotacion.save()
        else:
            anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            trabaja = anotacion.first().trabaja
            anotacion.update(trabaja=not trabaja)

    except ObjectDoesNotExist:
        pass

    if vista == "cuad":
        return HttpResponseRedirect(reverse('detalle-asignatura-cuad', args=(idAsignatura, fecha)))
    else:
        return HttpResponseRedirect(reverse('detalle-asignatura-lista', args=(idAsignatura, fecha)))

#funcion para poner que trabaja el alumno (lo tenga o no lo tenga ya indicado). No redirige
@login_required
def trabaja(request, idAlumno, idAsignatura, fecha):

    try:
        anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), trabaja=True)
            anotacion.save()
        else:
            anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            anotacion.update(trabaja=True)

    except ObjectDoesNotExist:
        pass

@login_required
@csrf_exempt
def ponerPositivo(request, idAlumno, idAsignatura, vista, fecha):

    # se borran los alumnos seleccionados, si los hubiera
    request.session['lista'] = []

    positivo(request,idAlumno,idAsignatura, fecha)

    if vista == "cuad":
        return HttpResponseRedirect(reverse('detalle-asignatura-cuad', args=(idAsignatura, fecha)))
    else:
        return HttpResponseRedirect(reverse('detalle-asignatura-lista', args=(idAsignatura, fecha)))

#funcion para poner un positivo al alumno, sin redirigir
@login_required
def positivo(request, idAlumno, idAsignatura, fecha):

    try:
        anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(fecha=datetime.strptime(fecha, '%d/%m/%Y'),alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), positivos=1)
            anotacion.save()
        else:
            anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            positivos = anotacion.first().positivos
            if positivos is None:
                positivos = 1
            else:
                positivos+=1

            anotacion.update(positivos=positivos)

    except ObjectDoesNotExist:
        pass


@login_required
@csrf_exempt
def ponerNegativo(request, idAlumno, idAsignatura, vista, fecha):

    # se borran los alumnos seleccionados, si los hubiera
    request.session['lista'] = []

    negativo(request, idAlumno, idAsignatura, fecha)

    if vista == "cuad":
        return HttpResponseRedirect(reverse('detalle-asignatura-cuad', args=(idAsignatura, fecha)))
    else:
        return HttpResponseRedirect(reverse('detalle-asignatura-lista', args=(idAsignatura, fecha)))

#funcion para poner un negativo al alumno, sin redirigir
@login_required
def negativo(request, idAlumno, idAsignatura, fecha):

    try:
        anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), negativos=1)
            anotacion.save()
        else:
            anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            negativos = anotacion.first().negativos
            if negativos is None:
                negativos = 1
            else:
                negativos+=1

            anotacion.update(negativos=negativos)

    except ObjectDoesNotExist:
        pass

#vista para realizar anotaciones a multiples alumnos a la vez
@login_required
def ponerAnotaciones(request, idAsignatura, vista, fecha):

    if "cuadriculaAlumnado" in request.POST: #vista cuadricula
        lista = request.POST.getlist('cuadriculaAlumnado')
        lista_int = []
        for i in lista:
            lista_int.append(int(i))
        request.session['lista'] = lista_int
    elif "listaAlumnado" in request.POST:   #vista lista
        lista = request.POST.getlist('listaAlumnado')
        lista_int = []
        for i in lista:
            lista_int.append(int(i))
        request.session['lista'] = lista_int
    else:
        lista = None
        request.session['lista'] = []


    if lista is not None and request.POST.get('nota') == "falta":
        for alumno in lista:
            falta\
                (request, alumno, idAsignatura, fecha)
        #messages.add_message(request, messages.SUCCESS, '[%s] Falta(s) puesta(s) correctamente' % fecha)

    elif lista is not None and request.POST.get('nota') == "trabaja":
        for alumno in lista:
            trabaja(request, alumno, idAsignatura, fecha)
        #messages.add_message(request, messages.SUCCESS, '[%s] Anotacion(es) de trabajo puesta(s) correctamente' % fecha)

    elif lista is not None and request.POST.get('nota') == "positivo":
        for alumno in lista:
            positivo(request, alumno, idAsignatura, fecha)
        #messages.add_message(request, messages.SUCCESS, '[%s] Positivo(s) puesto(s) correctamente' % fecha)

    elif lista is not None and request.POST.get('nota') == "negativo":
        for alumno in lista:
            negativo(request, alumno, idAsignatura, fecha)
        #messages.add_message(request, messages.SUCCESS, '[%s] Negativo(s) puesto(s) correctamente' % fecha)
    elif "fecha" in request.POST and "vista" in request.POST:
        #se borran los alumnos seleccionados
        request.session['lista'] = []
        # Cambio de numero de columnas de la asignatura
        if "columnas" in request.POST:
            asignatura = Asignatura.objects.get(pk=idAsignatura)
            asignatura.distribucion = request.POST.get('columnas')
            asignatura.save()

        fecha = request.POST.get('fecha')
        vista = request.POST.get('vista')

    if vista == "cuad":
        return HttpResponseRedirect(reverse('detalle-asignatura-cuad', args=(idAsignatura, fecha)))
    else:
        return HttpResponseRedirect(reverse('detalle-asignatura-lista', args=(idAsignatura, fecha)))

@csrf_exempt
def ordenarAsignatura(request, pk):

    asignatura = Asignatura.objects.get(pk=pk)
    for index, alumno_pk in enumerate(request.POST.getlist('alumno[]')):
        #alumno a ordenar
        alumno = get_object_or_404(Alumno, pk=int(str(alumno_pk)))

        #matricula cuyo orden se va a cambiar
        matricula = Matricula.objects.get(asignatura=asignatura, alumno=alumno)

        matricula.orden = int(str(index)) + 1
        matricula.save()

    return HttpResponse('')

@csrf_exempt
def ordenarTutoria(request):

    for index, alumno_pk in enumerate(request.POST.getlist('alumno[]')):
        #alumno a ordenar
        alumno = get_object_or_404(Alumno, pk=int(str(alumno_pk)))

        alumno.orden = int(str(index)) + 1
        alumno.save()

    return HttpResponse('')
