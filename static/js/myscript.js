var svgDocument;

function on_load(evt){
   O=evt.target;
   svgDocument=O.ownerDocument;
   svgDocument.getElementById("insula1").onclick = click_me();
}

function click_me(){
   alert('hi');
}