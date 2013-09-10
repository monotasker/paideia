
window.onload = function(){
}

window.onload = function(){
    //set up location masks and location click action
    var locs = ['domus_A', 'bath', 'ne_stoa', 'agora', 'gymnasion', 'synagogue']
    for (var i = 0; i < locs.length; i++) {
        var loc = document.getElementById(locs[i]);
        loc.addEventListener('mouseover', mask_other, false);
        loc.addEventListener('mouseout', show_other, false);
        loc.addEventListener('click', go_there, false);
    };
    //set up revealing of hotspot guide
    var tgr = document.getElementById('hotspot_guide_trigger');
    tgr.addEventListener('mouseover', show_guide, false);
    tgr.addEventListener('mouseout', hide_guide, false);
}

function go_there(evt){
    var loadmask = window.parent.document.getElementById('loading-mask');
    loadmask.style.display = 'block';
    var tobj = evt.currentTarget;
    var oname = tobj.getAttribute('id');
    window.parent.web2py_component("/paideia/exploring/walk.load/step?loc=" + oname,"page");
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

function show_guide(evt){
    var guide = document.getElementById('hotspot_guide');
    guide.style.display = 'inline';
}

function hide_guide(evt){
    var guide = document.getElementById('hotspot_guide');
    guide.style.display = 'none';
}
