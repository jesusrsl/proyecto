/**
 * Created by jesus on 13/04/17.
 */

function seleccionar_checkbox(activar){

   if (document.getElementById("vista").value=="cuad")
    {
       nombre = "cuadriculaAlumnado"
    }
    else{
      nombre = "listaAlumnado"
    }

    for (i=0;i<document.anotaciones_form.elements.length;i++)
      if(document.anotaciones_form.elements[i].type == "checkbox")
         if(document.anotaciones_form.elements[i].name == nombre)
            document.anotaciones_form.elements[i].checked=activar
}


function invertir_seleccion(){

   if (document.getElementById("vista").value=="cuad")
    {
       nombre = "cuadriculaAlumnado"
    }
    else{
      nombre = "listaAlumnado"
    }

   for (i=0;i<document.anotaciones_form.elements.length;i++)
      if(document.anotaciones_form.elements[i].name == nombre)
         document.anotaciones_form.elements[i].checked=!document.anotaciones_form.elements[i].checked
}

/*function mostrar(bloq, activar) {
   obj = document.getElementById(bloq);
   if (bloq =="cuadricula"){
      obj.style.display = (activar) ? 'block' : 'none';
      mostrar("lista", !activar);
   }
   else {
      obj.style.display = (activar) ? 'block' : 'none';
      mostrar("cuadricula", !activar);
   }

}*/

function cambiarVista(bloq) {
   //se deseleccionan todos los alumnos
    for (i=0;i<document.anotaciones_form.elements.length;i++)
      if(document.anotaciones_form.elements[i].type == "checkbox")
          document.anotaciones_form.elements[i]=0

   if (bloq =="cuadricula"){
      document.getElementById("vista").value = "cuad"
      document.anotaciones_form.submit()

   }
   else {
      document.getElementById("vista").value = "lista"
      document.anotaciones_form.submit()
   }

}

function seleccionar_alumno(idAlumno){

    if (document.getElementById("vista").value=="cuad")
    {
       nombre = "cuadriculaAlumnado"
    }
    else{
      nombre = "listaAlumnado"
    }

   for (i=0;i<document.anotaciones_form.elements.length;i++)
       if(document.anotaciones_form.elements[i].name == nombre)
           if(document.anotaciones_form.elements[i].value == idAlumno)
               document.anotaciones_form.elements[i].checked=!document.anotaciones_form.elements[i].checked


}

function poner_falta() {
    document.getElementById('nota').value = "falta";
    document.anotaciones_form.submit();
}

function poner_trabaja() {
    document.getElementById('nota').value = "trabaja";
    document.anotaciones_form.submit();
}

function poner_positivo() {
    document.getElementById('nota').value = "positivo";
    document.anotaciones_form.submit();
}

function poner_negativo() {
    document.getElementById('nota').value = "negativo";
    document.anotaciones_form.submit();
}
