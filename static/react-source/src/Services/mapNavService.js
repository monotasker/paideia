'use strict';

import { velocity } from "velocity";

function show_mask() {
    // ========= hide white mask when map is loaded ========== //
  document.querySelector('div#exploring-mask')
    .velocity({opacity: "1"}, {display: "block"}, 200);
}

function hide_mask() {
    // ========= hide white mask when map is loaded ========== //
  document.querySelector('div#exploring-mask')
    .velocity({opacity: "0"}, {display: "none"}, 700);
}

function fit_to_height() {
    // Handle page dimensions and spinner position
    const headroom = document.querySelector('.navbar').offsetHeight;
    const divheight = window.clientHeight - headroom;
    let $vertElems = window.querySelectorAll('#page, .speaker img, #town_map')
    $vertElems.forEach(function (elem) {
        elem.height(divheight);
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
    $mask.style.display = "block";
    $mask.style.opacity = "0";
    $mask.velocity({opacity: '1'});
    let oname = evt.target.id;
    window.parent.location("/walk/" + oname);
}

function svg_mask_other(evt){
    let $tobj = evt.target;
    let $svg = $tobj.parents('svg');
    $svg.find('#' + $tobj.attr('id') + '_mask')
        .css({display: 'inline', opacity: '0'})
        .animate({opacity: '0.4'}, 800);
    $svg.find('#' + $tobj.attr('id') + '_tip')
        .css({display: 'inline', opacity: '0'})
        .animate({opacity: '1'}, 300);
}

function svg_show_other(evt){
    var $tobj = $(evt.currentTarget);
    var $svg = $tobj.parents('svg');
    $svg.find('#' + $tobj.attr('id') + '_mask')
        .css({display: 'none'}, {opacity: '0'});
    $svg.find('#' + $tobj.attr('id') + '_tip')
        .css({display: 'none'}, {opacity: '0'});
}

function svg_show_guide(evt){
    $(evt.currentTarget).parents('svg').find('#hotspot_guide')
        .css({display: 'inline', opacity: '0'})
        .animate({opacity: '1'}, 300);
}

function svg_hide_guide(evt){
    $(evt.currentTarget).parents('svg').find('#hotspot_guide')
        .animate({opacity: '0'}, 500, function(){
            $(this).css({display: 'none'});
        });
}

function svg_check_guide_vis(evt){
    var myguide = $(evt.currentTarget).parents('svg').find('#hotspot_guide');
    if ( myguide.css('opacity') == '0' ) {
        return false;
    } else {
        return true;
    }
}

function set_svg_interactions(select_string) {
    var mysvg = $('#' + select_string)[0].contentDocument;
    var $mysvg = $(mysvg);
    var locs = '#domus_A, #bath, #ne_stoa, #agora, #gymnasion, #synagogue';
    $mysvg.find(locs).each(function(){
        $(this).on('mouseenter touchstart', svg_mask_other)
            .on('mouseleave', svg_show_other)
            .on('click touchstart', svg_go_there);
            // .on('mousedown touchstart', function( e ) {
            //   e.stopImmediatePropagation();
            // });
    });
    //set up revealing of hotspot guide
    $mysvg.find('#hotspot_guide_trigger')
        .on('mouseenter', svg_show_guide)
        .on('mouseleave', svg_hide_guide)
        .on('touchstart', function(e) {
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
    mapelem.onload = function(){
        let mymap = null;
        const beforePan = function(oldPan, newPan) {
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
        var mapInit = function(){
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
        set_svg_interactions('town_map');
    }
}

export {};
