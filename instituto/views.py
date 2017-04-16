from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, PageBreak, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.platypus import Table
from reportlab.lib.units import inch

from operator import itemgetter
from itertools import groupby

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView, RedirectView
from django.core.urlresolvers import reverse, reverse_lazy

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .models import Profesor, Asignatura, Grupo, Alumno, Aula, Anotacion

from datetime import date, datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.

def base(request):
    return render(request, 'base.html')

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
    header = Paragraph("Listado de Asignaturas", h1)
    asignaturas.append(header)

    headings = ['Nombre', 'Nombre del Profesor', 'Apellidos del Profesor', 'Curso', 'Unidad']
    info_asignaturas = [(a.nombre, a.profesor.nombre, a.profesor.apellidos, a.grupo.get_curso_display(), a.grupo.unidad) for a in Asignatura.objects.all()]
    t = Table([headings] + info_asignaturas)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (-1, -1), 1, colors.dodgerblue),    # bordes de las celdas (de grosor 1)
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue), # borde inferior (de mayor grosor, 2)
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)  # color de fondo (en este caso, solo la primera fila)
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


    #paginacion de la tabla de anotaciones (5 fechas-columnas por pagina)
    num_fechas = 0
    num_pagina = 1
    fecha_list = []
    key = itemgetter('fecha')
    iter = groupby(sorted(anotaciones, key=key), key=key)
    for fecha in iter:
        num_fechas += 1
        fecha_list.append(fecha[0])
        if (num_fechas % 7) == 0 and num_fechas < total_anotaciones:   #nueva pagina
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

        fila = ["%s %s %s" % (alumno.nombre, alumno.apellido1, alumno.apellido2)]

        for fecha, lista in iter:

            if fecha in listaFechas:

                anotacion = ""

                for v in lista:  # lista contiene todas las valoraciones en una determinada fecha

                    if alumno.id == v['alumno_id']:
                        if v['falta']:
                            anotacion += " F"
                        if v['trabaja']:
                            anotacion += " T"
                        if v['positivos'] is not None:
                            anotacion += " %s+" % v['positivos']
                        if v['negativos'] is not None:
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
                    resumen_anotaciones = "%dF, %dT, %d+, %d-" % (resumen[1], resumen[2], resumen[3], resumen[4])

            fila.append(resumen_anotaciones)

        # FILA COMPLETA
        info_anotaciones.append(fila)

    #se han terminado todos los alumnos

    tabla = Table([headings] + info_anotaciones)  # , colWidths='50'
    if ultimaPag is False:
        tabla.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (-1, -1), 1, colors.dodgerblue),  # bordes de las celdas (de grosor 1)
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),  # borde inferior (de mayor grosor, 2)
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue)  # color de fondo (en este caso, solo la primera fila)
        ]
        ))
    else:
        tabla.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (-1, -1), 1, colors.dodgerblue),  # bordes de las celdas (de grosor 1)
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),  # borde inferior (de mayor grosor, 2)
                ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
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


def pie(canvas,doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.restoreState()


#PROFESORES
class ProfesorListView(ListView):
    model = Profesor

class ProfesorDetailView(DetailView):
    model = Profesor

class ProfesorCreate(SuccessMessageMixin,CreateView):
    model = Profesor
    fields = '__all__'
    success_message = 'El profesor %(nombre)s %(apellidos)s se ha grabado correctamente' # %(field_name)s

class ProfesorUpdate(SuccessMessageMixin, UpdateView):
    model = Profesor
    fields = '__all__'
    success_message = 'El profesor %(nombre)s %(apellidos)s  se ha modificado correctamente'

class ProfesorDelete(DeleteView):
    model = Profesor
    success_url = reverse_lazy('lista-profesores')
    success_message = 'El profesor %(nombre)s %(apellidos)s  se ha elimiando correctamente'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(ProfesorDelete, self).delete(request, *args, **kwargs)

#PROFESORES TUTORES
class TutorListView(ListView):
    model = Profesor
    template_name = 'instituto/tutor_list.html'

    def get_queryset(self):
        queryset = super(TutorListView, self).get_queryset().filter(grupo__isnull=False).order_by('grupo')
        return queryset

#ASIGNATURAS
class AsignaturaListView(ListView):
    model = Asignatura

    #se le pasa la fecha actual para poder mostrar el detalle de cada asignatura
    def get_context_data(self, **kwargs):
        context = super(AsignaturaListView, self).get_context_data(**kwargs)
        context.update({'fecha': date.today().strftime('%d/%m/%Y')})
        return context

"""class AsignaturaDetailView(DetailView):
    model = Asignatura

    def get_context_data(self, **kwargs):
        context = super(AsignaturaDetailView, self).get_context_data(**kwargs)
        anotaciones = Anotacion.objects.filter(fecha=date.today(),asignatura=Asignatura.objects.get(pk=self.kwargs['pk']))

        context.update({'anotacion_list': anotaciones, 'fecha':date.today().strftime('%d/%m/%Y')})
        return context
"""

class AsignaturaDetailView(DetailView):
    model = Asignatura

    def get_context_data(self, **kwargs):
        context = super(AsignaturaDetailView, self).get_context_data(**kwargs)
        fecha = datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y')
        if fecha.strftime('%A') == "Saturday" or fecha.strftime('%A') == "Sunday":
            lectivo = False
        else:
            lectivo = True

        anotaciones = Anotacion.objects.filter(fecha=fecha,asignatura=Asignatura.objects.get(pk=self.kwargs['pk']))

        context.update({'anotacion_list': anotaciones, 'fecha': self.kwargs['fecha'], 'lectivo': lectivo})
        return context

class AsignaturaCreate(SuccessMessageMixin, CreateView):
    model = Asignatura
    fields = '__all__'
    success_message = 'La asignatura %(nombre)s se ha grabado correctamente'

class AsignaturaUpdate(SuccessMessageMixin, UpdateView):
    model = Asignatura
    fields = '__all__'
    success_message = 'La asignatura %(nombre)s se ha modificado correctamente'

class AsignaturaDelete(DeleteView):
    model = Asignatura
    success_message = 'La asignatura %(nombre)s se ha eliminado correctamente'
    success_url = reverse_lazy('lista-asignaturas')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(AsignaturaDelete, self).delete(request, *args, **kwargs)

#GRUPOS
class GrupoListView(ListView):
    model = Grupo

class GrupoDetailView(DetailView):
    model = Grupo


class GrupoCreate(SuccessMessageMixin, CreateView):
    model = Grupo
    fields = '__all__'
    success_message = 'El grupo %(curso_elegido)s %(unidad)s se ha grabado correctamente'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            curso_elegido=self.object.get_curso_display(),
        )

class GrupoUpdate(SuccessMessageMixin, UpdateView):
    model = Grupo
    fields = '__all__'
    success_message = 'El grupo %(curso_elegido)s %(unidad)s se ha modificado correctamente'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            curso_elegido=self.object.get_curso_display(),
        )

class GrupoDelete(DeleteView):
    model = Grupo
    success_url = reverse_lazy('lista-grupos')
    success_message = 'El grupo %(curso_elegido)s %(unidad_elegida)s se ha eliminado correctamente'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % dict(curso_elegido=obj.get_curso_display(),unidad_elegida=obj.unidad))
        return super(GrupoDelete, self).delete(request, *args, **kwargs)

#AULAS
class AulaListView(ListView):
    model = Aula

class AulaDetailView(DetailView):
    model = Aula

class AulaCreate(SuccessMessageMixin, CreateView):
    model = Aula
    fields = '__all__'
    success_message = 'El aula %(numero)s de la planta %(planta)s, pasillo %(pasillo)s, se ha grabado correctamente'

class AulaUpdate(SuccessMessageMixin, UpdateView):
    model = Aula
    fields = '__all__'
    success_message = 'El aula %(numero)s de la planta %(planta)s, pasillo %(pasillo)s, se ha modificado correctamente'

class AulaDelete(DeleteView):
    model = Aula
    success_url = reverse_lazy('lista-aulas')
    success_message = 'El aula %(numero)s de la planta %(planta)s, pasillo %(pasillo)s, se ha eliminado correctamente'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(AulaDelete, self).delete(request, *args, **kwargs)

#ALUMNOS
class AlumnoListView(ListView):
    model = Alumno
    #paginate_by = 10

    def get_queryset(self):
       queryset = super(AlumnoListView, self).get_queryset()
       return queryset.order_by('grupo', 'apellido1', 'apellido2', 'nombre')

class AlumnoDetailView(DetailView):
    model = Alumno

class AlumnoCreate(SuccessMessageMixin, CreateView):
    model = Alumno
    fields = '__all__'
    success_message = 'El alumno %(nombre)s %(apellido1)s %(apellido2)s se ha grabado correctamente'

class AlumnoUpdate(SuccessMessageMixin, UpdateView):
    model = Alumno
    fields = '__all__'
    success_message = 'El alumno %(nombre)s %(apellido1)s %(apellido2)s se ha modificado correctamente'

class AlumnoDelete(DeleteView):
    model = Alumno
    success_url = reverse_lazy('lista-alumnos')
    success_message = 'El alumno %(nombre)s %(apellido1)s %(apellido2)s se ha eliminado correctamente'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(AlumnoDelete, self).delete(request, *args, **kwargs)


#ANOTACIONES

"""
    IMPORTANE:
    puede que no sea necesaria esta clase
"""
class AnotacionListView(ListView):
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

def anotacionesFechas(request, idAsignatura):
    error = False
    mensaje_error = ""
    if 'inicio' in request.POST and 'fin' in request.POST:
        f_inicio = request.POST['inicio']
        f_fin = request.POST['fin']
        try:
            inicio = datetime.strptime(f_inicio, '%d/%m/%Y')
            fin = datetime.strptime(f_fin, '%d/%m/%Y')
            fecha = datetime.strftime(date.today(), '%d/%m/%Y')
            resumen = datosResumen(idAsignatura, inicio, fin)
            anotaciones= Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin,
                                  asignatura=Asignatura.objects.get(pk=idAsignatura)).order_by('fecha','alumno')

            #return HttpResponseRedirect(reverse('lista-anotaciones', args=(idAsignatura)))
            if anotaciones.count() == 0:    #no existen anotaciones en esas fechas
                error = True
                mensaje_error = "No existen anotaciones en las fechas indicadas. Por favor, intentelo de nuevo."
            elif "ver_anotaciones" in request.POST:
                return render(request, 'instituto/anotacion_list.html', {'fecha': fecha, 'object_list':anotaciones, 'idAsignatura': idAsignatura,'alumno_list': Asignatura.objects.get(pk=idAsignatura).alumno_set.all, 'resumen_list':resumen })
            elif "anotaciones_pdf" in request.POST:
                #return HttpResponseRedirect(reverse('anotaciones-pdf', args=(idAsignatura)))
                return anotacionesPDF(request, idAsignatura, inicio, fin)

        except ValueError:
            error = True
            mensaje_error = "Por favor, introduzca fechas de inicio y fin validas."


    return render(request,'instituto/fechas_anotaciones.html', {'error':error, 'mensaje_error':mensaje_error, 'idAsignatura':idAsignatura, 'fecha': datetime.strftime(date.today(), '%d/%m/%Y')})

def datosResumen(idAsignatura, inicio, fin):

    asignatura = Asignatura.objects.get(pk=idAsignatura)
    resumen_anotaciones = [] #lista de listas
    for alumno in asignatura.alumno_set.all():
        numFaltas = 0
        numTrabaja = 0
        numPositivos = 0
        numNegativos = 0

        for anotacion in Anotacion.objects.filter(fecha__gte=inicio, fecha__lte=fin, asignatura=idAsignatura):
            if (anotacion.alumno_id == alumno.id):
                if (anotacion.falta):
                    numFaltas+=1
                if (anotacion.trabaja):
                    numTrabaja+=1
                if (anotacion.positivos is not None):
                    numPositivos+=anotacion.positivos
                if (anotacion.negativos is not None):
                    numNegativos+=anotacion.negativos

        #se anyade una sublista con la informacion del alumno
        resumen_anotaciones.append([alumno.id, numFaltas, numTrabaja, numPositivos, numNegativos])

    return resumen_anotaciones

class AnotacionDetailView(DetailView):
    model = Anotacion

#Vista para redirigir y decidir si crear una nueva anotacion o editar la ya existente --> debe haber una anotacion por alumno, asignatura y fecha
class AnotacionCreateUpdate(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            anotacion=Anotacion.objects.filter(fecha=datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y'), alumno=Alumno.objects.get(pk=kwargs['idAlumno']), asignatura=Asignatura.objects.get(pk=kwargs['idAsignatura'])).first()
            if anotacion is None:
                return reverse('nueva-anotacion', kwargs={'idAlumno': kwargs['idAlumno'], 'idAsignatura': kwargs['idAsignatura'], 'fecha': self.kwargs['fecha']})
            else:
                return reverse('editar-anotacion', kwargs={'pk': anotacion.id,})
        except ObjectDoesNotExist:
            return reverse('nueva-anotacion', kwargs={'idAlumno': kwargs['idAlumno'], 'idAsignatura': kwargs['idAsignatura'], 'fecha': self.kwargs['fecha']})

#class AnotacionCreate(SuccessMessageMixin, AjaxTemplateMixin, CreateView):
class AnotacionCreate(SuccessMessageMixin, CreateView):
    model = Anotacion
    fields = ['falta', 'trabaja', 'positivos', 'negativos']
    success_message = '[%(fecha_str)s] Anotacion del alumno %(nombre_alumno)s %(apellido1_alumno)s %(apellido2_alumno)s grabada correctamente'

    def get_success_message(self, cleaned_data):
        alumno = Alumno.objects.get(pk=self.kwargs['idAlumno'])
        return self.success_message % dict(fecha_str=self.kwargs['fecha'],nombre_alumno=alumno.nombre, apellido1_alumno=alumno.apellido1, apellido2_alumno=alumno.apellido2)

    def get_context_data(self, **kwargs):
        context = super(AnotacionCreate, self).get_context_data(**kwargs)
        context.update({'fecha': self.kwargs['fecha'], 'alumno': self.kwargs['idAlumno'], 'asignatura': self.kwargs['idAsignatura']})
        return context

    def form_valid(self, form):
        form.instance.alumno = Alumno.objects.get(pk=self.kwargs['idAlumno'])
        form.instance.asignatura = Asignatura.objects.get(pk=self.kwargs['idAsignatura'])
        form.instance.fecha = datetime.strptime(self.kwargs['fecha'], '%d/%m/%Y')
        return super(AnotacionCreate, self).form_valid(form)



class AnotacionUpdate(SuccessMessageMixin, UpdateView):
    model = Anotacion
    fields = ['falta', 'trabaja', 'positivos', 'negativos']
    success_message = '[%(fecha_str)s] Anotacion del alumno %(nombre_alumno)s %(apellido1_alumno)s %(apellido2_alumno)s editada correctamente'

    def get_success_message(self, cleaned_data):
        obj = self.get_object()
        return self.success_message % dict(fecha_str=datetime.strftime(obj.fecha, '%d/%m/%Y'), nombre_alumno=obj.alumno.nombre, apellido1_alumno=obj.alumno.apellido1, apellido2_alumno=obj.alumno.apellido2)

    #a partir del pk de anotacion pasado en la url, se obtiene el alumno y la asignatura y se anaden al contexto con el que renderizara la plantilla
    def get_context_data(self, **kwargs):
        context = super(AnotacionUpdate, self).get_context_data(**kwargs)
        context.update({'fecha':datetime.strftime(Anotacion.objects.get(id=self.kwargs['pk']).fecha, '%d/%m/%Y'), 'alumno': Anotacion.objects.get(id=self.kwargs['pk']).alumno_id, 'asignatura': Anotacion.objects.get(id=self.kwargs['pk']).asignatura_id})
        return context


#NO SE UTILIZA pero SI FUNCIONA (puede utilizarle con la URL)
class AnotacionDelete(SuccessMessageMixin, DeleteView):
    model = Anotacion
    #success_url = reverse_lazy('detalle-asignatura', kwargs={'pk': Anotacion.objects.get(pk=self.kwargs['pk']).asignatura_id}) #comprobar
    success_message = 'Anotacion elimanada correctamente'

    def get_success_url(self):
        return reverse_lazy('detalle-asignatura', kwargs={'pk': Anotacion.objects.get(pk=self.kwargs['pk']).asignatura_id, 'fecha': datetime.strftime(Anotacion.objects.get(id=self.kwargs['pk']).fecha, '%d/%m/%Y')})

    def get_context_data(self, **kwargs):
        context = super(AnotacionDelete, self).get_context_data(**kwargs)
        context.update({'fecha':datetime.strftime(Anotacion.objects.get(id=self.kwargs['pk']).fecha, '%d/%m/%Y')})
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(AnotacionDelete, self).delete(request, *args, **kwargs)


#Vistas para crear anotaciones individuales

def ponerFalta(request, idAlumno, idAsignatura,fecha):

    ha_faltado = False
    try:
        anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), falta=True)
            anotacion.save()
            ha_faltado = True
        else:
            anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            falta = anotacion.first().falta
            ha_faltado = not falta
            anotacion.update(falta=not falta)

    except ObjectDoesNotExist:
        pass

    alumno = Alumno.objects.get(pk=idAlumno)
    if ha_faltado:
        messages.add_message(request, messages.SUCCESS, '[%s] Se le ha puesto falta al alumno %s %s %s' %(fecha, alumno.nombre, alumno.apellido1, alumno.apellido2))
    else:
        messages.add_message(request, messages.SUCCESS, '[%s] Se le ha quitado la falta al alumno %s %s %s' %(fecha, alumno.nombre, alumno.apellido1, alumno.apellido2))


    return HttpResponseRedirect(reverse('detalle-asignatura', args=(idAsignatura,fecha)))

#funcion para poner falta al alumno (la tenga o no la tenga ya). No muestra mensaje ni redirige
def falta(request, idAlumno, idAsignatura, fecha):

    try:
        anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), falta=True)
            anotacion.save()
        else:
            anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            anotacion.update(falta=True)

    except ObjectDoesNotExist:
        pass


def ponerTrabaja(request, idAlumno, idAsignatura, fecha):

    ha_trabajado = False
    try:
        anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), trabaja=True)
            anotacion.save()
            ha_trabajado = True
        else:
            anotacion = Anotacion.objects.filter(fecha=datetime.strptime(fecha, '%d/%m/%Y'), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            trabaja = anotacion.first().trabaja
            ha_trabajado = not trabaja
            anotacion.update(trabaja=not trabaja)

    except ObjectDoesNotExist:
        pass

    alumno = Alumno.objects.get(pk=idAlumno)
    if ha_trabajado:
        messages.add_message(request, messages.SUCCESS, '[%s] El alumno %s %s %s ha trabajado correctamente' % (
        fecha, alumno.nombre, alumno.apellido1, alumno.apellido2))
    else:
        messages.add_message(request, messages.SUCCESS, '[%s] El alumno %s %s %s no ha trabajado correctamente' % (
        fecha, alumno.nombre, alumno.apellido1, alumno.apellido2))

    return HttpResponseRedirect(reverse('detalle-asignatura', args=(idAsignatura, fecha)))

#funcion para poner que trabaja el alumno (lo tenga o no lo tenga ya indicado). No muestra mensaje ni redirige
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

def ponerPositivo(request, idAlumno, idAsignatura, fecha):

    positivo(request,idAlumno,idAsignatura, fecha)

    alumno = Alumno.objects.get(pk=idAlumno)
    messages.add_message(request, messages.SUCCESS, '[%s] Se le ha puesto un positivo al alumno %s %s %s' %(fecha, alumno.nombre, alumno.apellido1, alumno.apellido2))

    return HttpResponseRedirect(reverse('detalle-asignatura', args=(idAsignatura, fecha)))

#funcion para poner un positivo al alumno, sin mostrar mensaje ni redirigir
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



def ponerNegativo(request, idAlumno, idAsignatura, fecha):

    negativo(request, idAlumno, idAsignatura, fecha)

    alumno = Alumno.objects.get(pk=idAlumno)
    messages.add_message(request, messages.SUCCESS, '[%s] Se le ha puesto un negativo al alumno %s %s %s' % (fecha, alumno.nombre, alumno.apellido1, alumno.apellido2))

    return HttpResponseRedirect(reverse('detalle-asignatura', args=(idAsignatura, fecha)))

#funcion para poner un negativo al alumno, sin mostrar mensaje ni redirigir
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
def ponerAnotaciones(request, idAsignatura, fecha):
    if "listaAlumnado" in request.POST and "poner_faltas" in request.POST:
        lista = request.POST.getlist('listaAlumnado')
        for alumno in lista:
            falta(request, alumno, idAsignatura, fecha)
        messages.add_message(request, messages.SUCCESS, '[%s] Falta(s) puesta(s) correctamente' % fecha)
    elif "listaAlumnado" in request.POST and "poner_trabaja" in request.POST:
        lista = request.POST.getlist('listaAlumnado')
        for alumno in lista:
            trabaja(request, alumno, idAsignatura, fecha)
        messages.add_message(request, messages.SUCCESS, '[%s] Anotacion(es) de trabajo puesta(s) correctamente' % fecha)
    elif "listaAlumnado" in request.POST and "poner_positivo" in request.POST:
        lista = request.POST.getlist('listaAlumnado')
        for alumno in lista:
            positivo(request, alumno, idAsignatura, fecha)
        messages.add_message(request, messages.SUCCESS, '[%s] Positivo(s) puesto(s) correctamente' % fecha)
    elif "listaAlumnado" in request.POST and "poner_negativo" in request.POST:
        lista = request.POST.getlist('listaAlumnado')
        for alumno in lista:
            negativo(request, alumno, idAsignatura, fecha)
        messages.add_message(request, messages.SUCCESS, '[%s] Negativo(s) puesto(s) correctamente' % fecha)
    elif "fecha" in request.POST:
        fecha = request.POST.get('fecha')

    #FALTA CONSERVAR la seleccion
    return HttpResponseRedirect(reverse('detalle-asignatura', args=(idAsignatura, fecha)))
