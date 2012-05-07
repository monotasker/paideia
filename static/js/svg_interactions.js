function init(evt){
    //pulse_in();
    //pulse_out();
    //go_there();
}

function go_there(evt){
    var tobj = evt.currentTarget;
    var oname = tobj.getAttribute('id');
    window.parent.web2py_component("/paideia/exploring/walk.load/ask?loc=" + oname,"page");
}

function mask_other(evt){
    var tobj = evt.currentTarget;
    var tname = tobj.getAttribute('id');
    var maskname = tname + '_mask';
    document.getElementById(maskname).style.display = 'block';
    document.getElementById(maskname).style.opacity = '1';

}
