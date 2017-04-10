from django.contrib.auth.decorators import login_required
#from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView, RedirectView
from django.core.urlresolvers import reverse, reverse_lazy

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .models import Profesor, Asignatura, Grupo, Alumno, Aula, Anotacion

from datetime import date
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
                            pagesize=letter,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )
    asignaturas = []

    styles = getSampleStyleSheet()
    header = Paragraph("Listado de Asignaturas", styles['Heading1'])
    asignaturas.append(header)

    headings = ('Nombre', 'Nombre del Profesor', 'Apellidos del Profesor', 'Curso', 'Unidad')
    info_asignaturas = [(a.nombre, a.profesor.nombre, a.profesor.apellidos, a.grupo.get_curso_display(), a.grupo.unidad) for a in Asignatura.objects.all()]
    t = Table([headings] + info_asignaturas)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (4, -1), 1, colors.dodgerblue),    # bordes de las celdas (de grosor 1)
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

class AsignaturaDetailView(DetailView):
    model = Asignatura

    def get_context_data(self, **kwargs):
        context = super(AsignaturaDetailView, self).get_context_data(**kwargs)
        context.update({'anotacion_list': Anotacion.objects.filter(fecha=date.today(),asignatura=Asignatura.objects.get(pk=self.kwargs['pk']))})
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


"""#BOOTSTRAP MODALS --> para utilizar vistas basadas en clases junto con modals (ventanas emergentes)
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
"""

#ANOTACIONES
class AnotacionListView(ListView):
    model = Anotacion

    def get_queryset(self):
        queryset = super(AnotacionListView, self).get_queryset().filter(asignatura=self.kwargs['idAsignatura']).order_by('fecha', 'alumno')
        return queryset

class AnotacionDetailView(DetailView):
    model = Anotacion

#Vista para redirigir y dedcidir si crear una nueva anotacion o editar la ya existente --> debe haber una anotacion por alumno, asignatura y fecha
class AnotacionCreateUpdate(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            anotacion=Anotacion.objects.filter(fecha=date.today(), alumno=Alumno.objects.get(pk=kwargs['idAlumno']), asignatura=Asignatura.objects.get(pk=kwargs['idAsignatura'])).first()
            if anotacion is None:
                return reverse('nueva-anotacion', kwargs={'idAlumno': kwargs['idAlumno'], 'idAsignatura': kwargs['idAsignatura'], })
            else:
                return reverse('editar-anotacion', kwargs={'pk': anotacion.id,})
        except ObjectDoesNotExist:
            return reverse('nueva-anotacion', kwargs={'idAlumno': kwargs['idAlumno'], 'idAsignatura': kwargs['idAsignatura'], })

#class AnotacionCreate(SuccessMessageMixin, AjaxTemplateMixin, CreateView):
class AnotacionCreate(SuccessMessageMixin, CreateView):
    model = Anotacion
    fields = ['falta', 'trabaja', 'positivos', 'negativos']
    success_message = 'Anotacion del alumno %(nombre_alumno)s %(apellido1_alumno)s %(apellido2_alumno)s grabada correctamente'

    def get_success_message(self, cleaned_data):
        alumno = Alumno.objects.get(pk=self.kwargs['idAlumno'])
        return self.success_message % dict(nombre_alumno=alumno.nombre, apellido1_alumno=alumno.apellido1, apellido2_alumno=alumno.apellido2)

    def get_context_data(self, **kwargs):
        context = super(AnotacionCreate, self).get_context_data(**kwargs)
        context.update({'alumno': self.kwargs['idAlumno'], 'asignatura': self.kwargs['idAsignatura']})
        return context

    def form_valid(self, form):
        form.instance.alumno = Alumno.objects.get(pk=self.kwargs['idAlumno'])
        form.instance.asignatura = Asignatura.objects.get(pk=self.kwargs['idAsignatura'])
        return super(AnotacionCreate, self).form_valid(form)



class AnotacionUpdate(SuccessMessageMixin, UpdateView):
    model = Anotacion
    fields = ['falta', 'trabaja', 'positivos', 'negativos']
    success_message = 'Anotacion del alumno %(nombre_alumno)s %(apellido1_alumno)s %(apellido2_alumno)s editada correctamente'

    def get_success_message(self, cleaned_data):
        obj = self.get_object()
        return self.success_message % dict(nombre_alumno=obj.alumno.nombre, apellido1_alumno=obj.alumno.apellido1, apellido2_alumno=obj.alumno.apellido2)

    #a partir del pk de anotacion pasado en la url, se obtiene el alumno y la asignatura y se anaden al contexto con el que renderizara la plantilla
    def get_context_data(self, **kwargs):
        context = super(AnotacionUpdate, self).get_context_data(**kwargs)
        context.update({'alumno': Anotacion.objects.get(id=self.kwargs['pk']).alumno_id, 'asignatura': Anotacion.objects.get(id=self.kwargs['pk']).asignatura_id})
        return context


#NO SE UTILIZA pero SI FUNCIONA (puede utilizarle con la URL)
class AnotacionDelete(SuccessMessageMixin, DeleteView):
    model = Anotacion
    #success_url = reverse_lazy('detalle-asignatura', kwargs={'pk': Anotacion.objects.get(pk=self.kwargs['pk']).asignatura_id}) #comprobar
    success_message = 'Anotacion elimanada correctamente'

    def get_success_url(self):
        return reverse_lazy('detalle-asignatura', kwargs={'pk': Anotacion.objects.get(pk=self.kwargs['pk']).asignatura_id}) #comprobar

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(AnotacionDelete, self).delete(request, *args, **kwargs)


#Vistas para crear anotaciones individuales

def ponerFalta(request, idAlumno, idAsignatura):

    ha_faltado = False
    try:
        anotacion = Anotacion.objects.filter(fecha=date.today(), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), falta=True)
            anotacion.save()
            ha_faltado = True
        else:
            anotacion = Anotacion.objects.filter(fecha=date.today(), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            falta = anotacion.first().falta
            ha_faltado = not falta
            anotacion.update(falta=not falta)

    except ObjectDoesNotExist:
        pass

    alumno = Alumno.objects.get(pk=idAlumno)
    if ha_faltado:
        messages.add_message(request, messages.SUCCESS, 'Se le ha puesto falta al alumno %s %s %s' %(alumno.nombre, alumno.apellido1, alumno.apellido2))
    else:
        messages.add_message(request, messages.SUCCESS, 'Se le ha quitado la falta al alumno %s %s %s' %(alumno.nombre, alumno.apellido1, alumno.apellido2))


    return HttpResponseRedirect(reverse('detalle-asignatura', args=(idAsignatura)))


def ponerTrabaja(request, idAlumno, idAsignatura):

    ha_trabajado = False
    try:
        anotacion = Anotacion.objects.filter(fecha=date.today(), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), trabaja=True)
            anotacion.save()
            ha_trabajado = True
        else:
            anotacion = Anotacion.objects.filter(fecha=date.today(), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            trabaja = anotacion.first().trabaja
            ha_trabajado = not trabaja
            anotacion.update(trabaja=not trabaja)

    except ObjectDoesNotExist:
        pass

    alumno = Alumno.objects.get(pk=idAlumno)
    if ha_trabajado:
        messages.add_message(request, messages.SUCCESS, 'El alumno %s %s %s ha trabajado correctamente' % (
        alumno.nombre, alumno.apellido1, alumno.apellido2))
    else:
        messages.add_message(request, messages.SUCCESS, 'El alumno %s %s %s no ha trabajado correctamente' % (
        alumno.nombre, alumno.apellido1, alumno.apellido2))

    return HttpResponseRedirect(reverse('detalle-asignatura', args=(idAsignatura)))



def ponerPositivo(request, idAlumno, idAsignatura):

    try:
        anotacion = Anotacion.objects.filter(fecha=date.today(), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), positivos=1)
            anotacion.save()
        else:
            anotacion = Anotacion.objects.filter(fecha=date.today(), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            positivos = anotacion.first().positivos
            if positivos is None:
                positivos = 1
            else:
                positivos+=1

            anotacion.update(positivos=positivos)

    except ObjectDoesNotExist:
        pass

    alumno = Alumno.objects.get(pk=idAlumno)
    messages.add_message(request, messages.SUCCESS, 'Se le ha puesto un positivo al alumno %s %s %s' %(alumno.nombre, alumno.apellido1, alumno.apellido2))

    return HttpResponseRedirect(reverse('detalle-asignatura', args=(idAsignatura)))



def ponerNegativo(request, idAlumno, idAsignatura):

    try:
        anotacion = Anotacion.objects.filter(fecha=date.today(), alumno=Alumno.objects.get(pk=idAlumno),
                                             asignatura=Asignatura.objects.get(pk=idAsignatura)).first()
        if anotacion is None:
            anotacion = Anotacion(alumno=Alumno.objects.get(pk=idAlumno), asignatura=Asignatura.objects.get(pk=idAsignatura), negativos=1)
            anotacion.save()
        else:
            anotacion = Anotacion.objects.filter(fecha=date.today(), alumno=Alumno.objects.get(pk=idAlumno),
                                                 asignatura=Asignatura.objects.get(pk=idAsignatura))
            negativos = anotacion.first().negativos
            if negativos is None:
                negativos = 1
            else:
                negativos+=1

            anotacion.update(negativos=negativos)

    except ObjectDoesNotExist:
        pass

    alumno = Alumno.objects.get(pk=idAlumno)
    messages.add_message(request, messages.SUCCESS, 'Se le ha puesto un negativo al alumno %s %s %s' % (alumno.nombre, alumno.apellido1, alumno.apellido2))

    return HttpResponseRedirect(reverse('detalle-asignatura', args=(idAsignatura)))


#FALTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
def ponerFaltas(request, idAsignatura):



    return HttpResponseRedirect(reverse('detalle-asignatura', args=(idAsignatura)))