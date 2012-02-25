function init(evt){
    //pulse_in();
    //pulse_out();
    //go_there();
}

function go_there(evt){
    var tobj = evt.currentTarget;
    var oname = tobj.getAttribute('id');
    window.parent.web2py_component("/paideia/exploring/index.load?loc=" + oname,"page")
}

function pulse_in(evt){
    var tobj = evt.currentTarget;   
    
    tobj.setAttribute('stroke-opacity', '1');
    //bbox =  tobj.getBBox();
    //dX = bbox.width * (-.05);
    //dY = bbox.height * (-.1);
    //tobj.setAttribute('transform', 'scale(1.1), translate(' + dX + ', ' + dY + ')');
}

function pulse_out(evt){
    var tobj = evt.currentTarget;
    tobj.setAttribute('stroke-opacity', '0');
}
