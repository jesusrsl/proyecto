/**
 * Created by jesus on 13/04/17.
 */

function seleccionar_checkbox(form,activar){
   for (i=0;i<form.elements.length;i++)
      if(form.elements[i].type == "checkbox")
         form.elements[i].checked=activar
}

function invertir_seleccion(form){
   for (i=0;i<form.elements.length;i++)
      if(form.elements[i].type == "checkbox")
         form.elements[i].checked=!form.elements[i].checked
}