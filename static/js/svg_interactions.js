window.onload = function(){
    var locs = ['domus_A', 'bath', 'ne_stoa', 'agora', 'gymnasion', 'synagogue']
    for (var i = 0; i < locs.length; i++) {
        var loc = document.getElementById(locs[i]);
        loc.addEventListener('mouseover', mask_other, false);
        loc.addEventListener('mouseout', show_other, false);
        loc.addEventListener('click', go_there, false);
    };
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
    var mask = document.getElementById(maskname);
    mask.style.display = 'inline';
    mask.style.opacity = '0.4';
    var tipname = tname + '_tip';
    var tip = document.getElementById(tipname);
    tip.style.display = 'inline';
}

function show_other(evt){
    var tobj = evt.currentTarget;
    var tname = tobj.getAttribute('id');
    var maskname = tname + '_mask';
    var mask = document.getElementById(maskname);
    mask.style.display = 'none';
    mask.style.opacity = '0.4';
    var tipname = tname + '_tip';
    var tip = document.getElementById(tipname);
    tip.style.display = 'none';
}


