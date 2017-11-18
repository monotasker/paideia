'use strict';

function show_mask(select_string) {
    // ========= hide white mask when map is loaded ========== //
  $('div#' + select_string).velocity({opacity: "1"}, {display: "block"}, 200);
}

function hide_mask(select_string) {
    // ========= hide white mask when map is loaded ========== //
  $('div#' + select_string).velocity({opacity: "0"}, {display: "none"}, 700);
}

function fit_to_height() {
    // Handle page dimensions and spinner position
    var headroom = $('.navbar').innerHeight();
    var footroom = $('#footer').outerHeight();
    var divheight = window.innerHeight - (headroom + footroom);
    $('#page, .speaker img, #town_map').each(function () {
        $(this).height(divheight);
    });
    $('#town_map').width('100%');
    var $spinner = $('#loading-mask img, #exploring-mask img');
    $spinner.each(function(){
        $(this).css('top', (divheight / 2) - ($spinner.outerHeight() / 2) );
    });
}

function svg_go_there(evt){
    show_mask('exploring-mask');
    $(window.parent.document).find('#exploring-mask')
        .css({'display': 'block'});
    var oname = $(evt.currentTarget).attr('id');
    window.parent.web2py_component("/paideia/exploring/walk.load/step?loc=" + oname, "page");
}

function svg_mask_other(evt){
    var $tobj = $(evt.currentTarget);
    var $svg = $tobj.parents('svg');
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

function set_svg_interactions(select_string) {
    var mysvg = $('#' + select_string)[0].contentDocument;
    var $mysvg = $(mysvg);
    var locs = '#domus_A, #bath, #ne_stoa, #agora, #gymnasion, #synagogue';
    $mysvg.find(locs).each(function(){
        $(this).on('mouseenter', svg_mask_other)
            .on('mouseleave', svg_show_other)
            .on('click', svg_go_there);
    });
    //set up revealing of hotspot guide
    $mysvg.find('#hotspot_guide_trigger')
        .on('mouseenter', svg_show_guide)
        .on('mouseleave', svg_hide_guide);
}

function make_map_pan(select_string) {
    // Set svg map up to pan and scroll
    var mapelem = document.getElementById(select_string);
    mapelem.onload = function(){
        var mymap = null;
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
        hide_mask('exploring-mask');
        set_svg_interactions('town_map');
    }
}

    // function set_page_height() {
    //     var $page = $('#page');
    //     var width = $page.width();
    //     if (width >= 1200) {
    //         $('#page').css("background-size", "100% auto");
    //         $page.css('height', (width * 0.5));
    //     }
    //     else if (width >= 992) {
    //         $('#page').css("background-size", "100% auto");
    //         $page.css('height', (width * 0.55));
    //     }
    //     else if (width >= 768) {
    //         $('#page').css("background-size", "100% auto");
    //         $page.css('height', (width * 0.65));
    //     }
    //     else {
    //         console.log(width);
    //         $('#page').css("background-size", "auto 100%");
    //         $page.css('height', 600);
    //     }
    // }
    // set_page_height();

$(document).ready(function(){

    // ========== focus input when bug reporter appears =============== //
    // FIXME: Not working.
    $('.bug_reporter_modal').on('show.bs.modal', function(event){
        $('#bug_reporter_comment').focus();
    });

// ========== end document.ready ===========================//
});
