function init(evt){
    //pulse_in();
    //pulse_out();
    //go_there();
}

function go_there(evt){
    var tobj = evt.currentTarget;
    var oname = tobj.getAttribute('id');
    window.parent.web2py_component("/paideia/exploring/index.load/ask?loc=" + oname,"page");
}