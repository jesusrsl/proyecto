/**
 * Created by jesus on 13/04/17.
 */

function seleccionar_checkbox(activar){

   if (document.getElementById("vista").value=="cuad")
    {
       nombre = "cuadriculaAlumnado";
    }
    else{
      nombre = "listaAlumnado";
    }

    for (i=0;i<document.getElementById("anotaciones_form").elements.length;i++)
      if(document.getElementById("anotaciones_form").elements[i].type == "checkbox")
         if(document.getElementById("anotaciones_form").elements[i].name == nombre)
            document.getElementById("anotaciones_form").elements[i].checked=activar;
}


function invertir_seleccion(){

   if (document.getElementById("vista").value=="cuad")
    {
       nombre = "cuadriculaAlumnado";
    }
    else{
      nombre = "listaAlumnado";
    }

   for (i=0;i<document.getElementById("anotaciones_form").elements.length;i++)
      if(document.getElementById("anotaciones_form").elements[i].name == nombre)
         document.getElementById("anotaciones_form").elements[i].checked=!document.getElementById("anotaciones_form").elements[i].checked;
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
    for (i=0;i<document.getElementById("anotaciones_form").elements.length;i++)
      if(document.getElementById("anotaciones_form").elements[i].type == "checkbox")
          document.getElementById("anotaciones_form").elements[i]=0;

   if (bloq =="cuadricula"){
      document.getElementById("vista").value = "cuad";
      document.getElementById("anotaciones_form").submit();

   }
   else {
      document.getElementById("vista").value = "lista";
      document.getElementById("anotaciones_form").submit();
   }

}

function cambiarGrupoVista(bloq) {

    var divLista = document.getElementById('grupoLista');
    var divCuad = document.getElementById('grupoCuad');

   if (bloq == "cuadricula"){
       divLista.style.display='none';
       divCuad.style.display='block';

   }
   else {
       divLista.style.display='block';
       divCuad.style.display='none';
   }

}

function cambiarTutoriaVista(bloq) {

    var divLista = document.getElementById('grupoLista');
    var divCuad = document.getElementById('grupoCuad');
    var divDistribucion = document.getElementById('distribucion');

   if (bloq == "cuadricula"){
       divLista.style.display='none';
       divCuad.style.display='block';
       divDistribucion.style.display='inline-block';

   }
   else {
       divLista.style.display='block';
       divCuad.style.display='none';
       divDistribucion.style.display='none';
   }

}

function seleccionar_alumno(idAlumno){

    if (document.getElementById("vista").value=="cuad")
    {
       nombre = "cuadriculaAlumnado";
    }
    else{
      nombre = "listaAlumnado";
    }

   for (i=0;i<document.getElementById("anotaciones_form").elements.length;i++)
       if(document.getElementById("anotaciones_form").elements[i].name == nombre)
           if(document.getElementById("anotaciones_form").elements[i].value == idAlumno)
               document.getElementById("anotaciones_form").elements[i].checked=!document.getElementById("anotaciones_form").elements[i].checked;


}

function poner_falta() {
    seleccionado = false;

    if (document.getElementById("vista").value=="cuad")
    {
       nombre = "cuadriculaAlumnado";
    }
    else{
      nombre = "listaAlumnado";
    }

    for (i=0;i<document.getElementById("anotaciones_form").elements.length;i++)
      if(document.getElementById("anotaciones_form").elements[i].type == "checkbox")
         if(document.getElementById("anotaciones_form").elements[i].name == nombre)
            if(document.getElementById("anotaciones_form").elements[i].checked){
                seleccionado=true;
                break;
            }

     if (seleccionado){
        document.getElementById('nota').value = "falta";
        document.getElementById("anotaciones_form").submit();
     }
}

function poner_trabaja() {
    seleccionado = false;

    if (document.getElementById("vista").value=="cuad")
    {
       nombre = "cuadriculaAlumnado";
    }
    else{
      nombre = "listaAlumnado";
    }

    for (i=0;i<document.getElementById("anotaciones_form").elements.length;i++)
      if(document.getElementById("anotaciones_form").elements[i].type == "checkbox")
         if(document.getElementById("anotaciones_form").elements[i].name == nombre)
            if(document.getElementById("anotaciones_form").elements[i].checked){
                seleccionado=true;
                break;
            }

    if (seleccionado) {
         document.getElementById('nota').value = "trabaja";
         document.getElementById("anotaciones_form").submit();
    }
}

function poner_positivo() {
    seleccionado = false;

    if (document.getElementById("vista").value=="cuad")
    {
       nombre = "cuadriculaAlumnado";
    }
    else{
      nombre = "listaAlumnado";
    }

    for (i=0;i<document.getElementById("anotaciones_form").elements.length;i++)
      if(document.getElementById("anotaciones_form").elements[i].type == "checkbox")
         if(document.getElementById("anotaciones_form").elements[i].name == nombre)
            if(document.getElementById("anotaciones_form").elements[i].checked){
                seleccionado=true;
                break;
            }

    if (seleccionado) {
        document.getElementById('nota').value = "positivo";
        document.getElementById("anotaciones_form").submit();
    }
}

function poner_negativo() {
    seleccionado = false;

    if (document.getElementById("vista").value=="cuad")
    {
       nombre = "cuadriculaAlumnado";
    }
    else{
      nombre = "listaAlumnado";
    }

    for (i=0;i<document.getElementById("anotaciones_form").elements.length;i++)
      if(document.getElementById("anotaciones_form").elements[i].type == "checkbox")
         if(document.getElementById("anotaciones_form").elements[i].name == nombre)
            if(document.getElementById("anotaciones_form").elements[i].checked){
                seleccionado=true;
                break;
            }

    if (seleccionado) {
        document.getElementById('nota').value = "negativo";
        document.getElementById("anotaciones_form").submit();
    }
}
