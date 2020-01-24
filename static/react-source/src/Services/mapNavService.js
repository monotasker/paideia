'use strict';

import Velocity from "velocity-animate";
import svgPanZoom from "svg-pan-zoom";

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
    Velocity($guide, {opacity: '0'}, 500, function(){
        $guide.style.display = 'none';
    });
}

function svg_check_guide_vis(evt){
    let $guide = evt.target.closest('svg').querySelector('#hotspot_guide');
    return ( $guide.style.opacity == '0' ) ? false : true;
}

function set_svg_interactions(select_string, navFunction) {
    let $svg = document.querySelector('#' + select_string).contentDocument;
    const locs = '#domus_A, #bath, #ne_stoa, #agora, #gymnasion, #synagogue';
    let $locs = $svg.querySelectorAll(locs);
    let $p = window.parent.document;
    $locs.forEach(function(loc){
        loc.addEventListener('mouseenter', svg_mask_other);
        loc.addEventListener('touchstart', svg_mask_other);
        loc.addEventListener('mouseleave', svg_show_other);
        loc.addEventListener('click', (evt) => {
          navFunction(evt.currentTarget.id);
          evt.preventDefault();
        });
        loc.addEventListener('touchstart', (evt) => {
          navFunction(evt.currentTarget.id);
          evt.preventDefault();
        });
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

function make_map_pan(select_string, navFunction) {
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
            mymap.contain();
            mymap.pan({x: 0, y: 0});
        }
        mapInit();
        set_svg_interactions(select_string, navFunction);
    }
}

export { make_map_pan };
