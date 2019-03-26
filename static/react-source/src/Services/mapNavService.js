'use strict';

import Velocity from "velocity-animate";
import svgPanZoom from "svg-pan-zoom";

function show_mask() {
    // ========= hide white mask when map is loaded ========== //
  let $mask = document.querySelector('div#exploring-mask');
  Velocity($mask, {opacity: "1"}, {display: "block"}, 200);
}

function hide_mask() {
    // ========= hide white mask when map is loaded ========== //
  let $mask = document.querySelector('div#exploring-mask');
  Velocity($mask, {opacity: "0"}, {display: "none"}, 700);
}

function fit_to_height() {
    // Handle page dimensions and spinner position
    const headroom = document.querySelector('.navbar').offsetHeight;
    const divheight = window.clientHeight - headroom;
    let $vertElems = document.querySelectorAll('#page, .speaker img, #town_map');
    $vertElems.forEach((elem) => {
        elem.style.height = divheight;
    });
    document.querySelector('#town_map').style.width = '100%';
    var $spinners = document.querySelectorAll('#loading-mask img, #exploring-mask img');
    $spinners.forEach(function(spinner){
        spinner.style.top = (divheight / 2) - (spinner.offsetHeight / 2);
    });
}

function svg_go_there(evt){
    // show_mask();
    let $p = window.parent.document;
    let $mask = $p.querySelector('#exploring-mask');
    $mask.style.cssText = "display: block; opacity: 0;";
    Velocity($mask, {opacity: '1'});
    let oname = evt.target.id;
    window.parent.location = "/walk/" + oname;
}

function svg_mask_other(evt){
    let $tobj = evt.target;
    let $svg = $tobj.closest('svg');
    let $mask = $svg.querySelector('#' + $tobj.id + '_mask');
    $mask.style.cssText = "display: inline; opacity: 0;";
    Velocity($mask, {opacity: '0.4'}, 800);
    let $tip = $svg.querySelector('#' + $tobj.id + '_tip');
    $tip.style.cssText = "display: inline; opacity: 0;";
    Velocity($tip, {opacity: '1'}, 300);
}

function svg_show_other(evt){
    var $tobj = evt.target;
    var $svg = $tobj.closest('svg');
    let $mask = $svg.querySelector('#' + $tobj.id + '_mask');
    $mask.style.cssText = "display: 'none'; opacity: 0;";
    let $tip = $svg.querySelector('#' + $tobj.id + '_tip');
    $tip.style.cssText = "display: none; opacity: 0;";
}

function svg_show_guide(evt){
    let $guide = evt.target.closest('svg').querySelector('#hotspot_guide');
    $guide.style.cssText = "display: inline; opacity: 0;";
    Velocity($guide, {opacity: '1'}, 300);
}

function svg_hide_guide(evt){
    let $guide = evt.target.closest('svg').querySelector('#hotspot_guide');
    Velocity($guide, {opacity: '0'}, 500, function(me){
        me.display = 'none';
    });
}

function svg_check_guide_vis(evt){
    let $guide = evt.target.closest('svg').querySelector('#hotspot_guide');
    if ( $guide.style.opacity == '0' ) {
        return false;
    } else {
        return true;
    }
}

function set_svg_interactions(select_string) {
    let $svg = document.querySelector('#' + select_string).contentDocument;
    const locs = '#domus_A, #bath, #ne_stoa, #agora, #gymnasion, #synagogue';
    let $locs = $svg.querySelectorAll(locs);
    $locs.forEach(function(loc){
        loc.addEventListener('mouseenter', svg_mask_other);
        loc.addEventListener('touchstart', svg_mask_other);
        loc.addEventListener('mouseleave', svg_show_other);
        loc.addEventListener('click', svg_go_there);
        loc.addEventListener('touchstart', svg_go_there);
    });
    //set up revealing of hotspot guide
    let $guide = $svg.querySelector('#hotspot_guide_trigger');
    $guide.addEventListener('mouseenter', svg_show_guide);
    $guide.addEventListener('mouseleave', svg_hide_guide);
    $guide.addEventListener('touchstart', (e) => {
      if ( svg_check_guide_vis(e) === false ) {
          svg_show_guide(e);
      } else {
          svg_hide_guide(e);
      }
    });
}

function make_map_pan(select_string) {
    // Set svg map up to pan and scroll
    let mapelem = document.getElementById(select_string);
    mapelem.onload = () => {
        let mymap = null;
        const beforePan = (oldPan, newPan) => {
            const sizes = mymap.getSizes();
            // Multiply viewbox width of SVG by current zoom and subtract
            // viewport width to get amount of overflown SVG.
            const x = -((sizes.viewBox.width * sizes.realZoom) - sizes.width);
            // Multiply viewbox height of SVG by current zoom and subtract
            // viewport height to get amount of overflown SVG.
            const y = -((sizes.viewBox.height * sizes.realZoom) - sizes.height);
            // Determine what’s lower, the current drag x/y coords or zero
            const minx = Math.min(0, newPan.x);
            const miny = Math.min(0, newPan.y);
            return {
                x: Math.max(x, minx),
                y: Math.max(y, miny)
            };
        };
        const mapInit = () => {
            mymap = svgPanZoom('#' + select_string, {
                                     beforePan,
                                     zoomEnabled: true,
                                     controlIconsEnabled: false,
                        });
            fit_to_height();
            mymap.contain();
            mymap.pan({x: 0, y: 0});
        }
        mapInit();
        hide_mask();
        set_svg_interactions(select_string);
    }
}

export { make_map_pan };
