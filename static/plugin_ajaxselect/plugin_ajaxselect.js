$('.add_trigger').live('click', function(event){
//open modal dialog (using jquery-ui dialog) for adder form
    var the_id = $(this).attr('id');
    var parts = the_id.split('_');
    var linktable = parts[0];

    var dlname = linktable + '_adder_form';
    if($('#' + dlname).length){
        $('#' + dlname).html('').dialog('open');
    } else {
        var newd = $('<div id="' + dlname + '" class="ajaxselect_dialog"></div>');
        newd.dialog({
            autoOpen:false,
            closeOnEscape:false,
            height:600,
            width:700,
            title:'Edit ',
        });
        $('#' + dlname).dialog('open');
    }
    return false
});

$('.edit_trigger').live('click', function(event){
//open modal dialog (using jquery-ui dialog) for edit form
    var the_id = $(this).attr('id');
    var parts = the_id.split('_');
    var linktable = parts[0];
    var dlname = linktable + '_editlist_form';
    if($('#' + dlname).length){
        $('#' + dlname).html('').dialog('open');
    } else {
        var newd = $('<div id="' + dlname + '" class="ajaxselect_dialog"></div>');
        newd.dialog({
            autoOpen:false,
            closeOnEscape:false,
            height:600,
            width:700,
            title:'Edit ',
        });
        $('#' + dlname).dialog('open');
    }

    return false
});

//TODO: Bind a separate function to the select if multi=False or no taglist
$('.plugin_ajaxselect select option').live('click', function(event){
    //when select value is changed, update

    //get landmarks to navigate dom
    var $select = $(this).parents('select');
    var $p = $(this).parents('span');
    var $td = $p.parents('li, td');
    var theid = $p.attr('id');
    var theinput = theid + '_input';
    var $theinput = $('#' + theid + '_input');
    var $taglist = $td.find('.taglist');
    var newval = $(this).val();
    var newtext = $(this).text();
    //set the option to selected
    $(this).attr('selected', 'selected');

    //add option to stored value in hidden input
    var theval = $theinput.val();
    theval += ',' + newval;
    $theinput.val(theval);
    $select.val(theval.split(','));
    //alert($select.val());

    //get url from beginning of request.args, and separate args from vars
    var r_url = $td.find('a.refresh_trigger').attr('href');
    var url_frag = r_url.match(/set_widget.load(.*)/);
    var url_args_vars = url_frag[1].split('?');
    var url_args = url_args_vars[0];
    var url_vars = url_args_vars[1];
    var appname = r_url.split('/')[1];
    var linktable_raw = url_vars.split('&')[1];
    var linktable = linktable_raw.replace('linktable=', '');
    var link_base = '/' + appname;
    link_base += '/views/plugin_ajaxselect/set_form_wrapper.load';
    var formname = linktable + '_editlist_form';

    //add tag for this option to taglist
    var newtag = ''
    //case where tags have edit links
    if($p.hasClass('lister_editlinks')){
        var link_url = link_base + url_args + '/' + newval + '?' + url_vars;
        var script_string = "web2py_component('" + link_url + "', '" + formname + "')";

        newtag += '<li class="editlink tag" id="' + newval + '">';
        newtag += '<a class="tag_remover">X</a>';
        newtag += '<a id="' + linktable + '_editlist_trigger_' + newval + '" ';
        newtag += 'class="edit_trigger editlink tag" ';
        newtag += 'href="' + link_url + '" ';
        newtag += 'onclick="' + script_string + '; return false;">';
        newtag += 'edit' + '</a>';
        newtag += newtext + '</li>';
    }
    //case for simple tags
    else if($p.hasClass('lister_simple')){
        newtag += '<li class="tag" id="' + newval + '">';
        newtag += '<a class="tag_remover">X</a>';
        newtag += '<span>' + newtext + '</span>' + '</li>';
    }
    $taglist.append(newtag);

    //make sure newly added tag is added to sortable binding
    $('ul.sortable').sortable('refresh');

    //update back end via ajax
    ajax('/' + appname + '/plugin_ajaxselect/setval/' + theinput,
                                        ['"' + theinput + '"'], ':eval');

    //prevent default behaviour, so that other options aren't de-selected
    return false
});
//TODO: move binding of sortable here from set_widget.load and
//listandedit/edit.load using plugin to provide 'create' event.

//TODO: Add stop: function(event, ui){ ... } param to sortable setup to
//copy new order to hidden input
//update the widget value when someone reorders tags in taglist
function whenSortStops($taglist){
    var $p = $taglist.first().parents('span');
    var $select = $p.find('select');
    var $theinput = $p.find('input');
    var $td = $p.parents('li, td');

    vals = new Array();
    $taglist.each(function(){
        var theid = $(this).attr('id');
        vals.push(theid);
    });
    valstring = String(vals.join(','));
    alert(valstring);

    //set the hidden input to the newly ordered value
    $theinput.val(valstring);
    theinput = $theinput.attr('id');

    //set the select widget to the newly ordered value
    $select.val(vals);

    //get app name from URL stored on refresh_trigger link
    var r_url = $td.find('a.refresh_trigger').attr('href');
    var appname = r_url.split('/')[1];
    //update back end via ajax
    ajax('/' + appname + '/plugin_ajaxselect/setval/' + theinput,
                                        ['"' + theinput + '"'], ':eval');

}

//remove an option by clicking on the remover icon in a tag
$('.tag_remover').live('click', function(event){
    var $prnt = $(this).parent('li');
    var $p = $(this).parents('span');
    var $td = $p.parents('li, td');
    var $select = $p.find('select');
    var val = $prnt.attr('id');
    //remove the actual DOM element for the tag
    $prnt.remove();
    var $theinput = $p.find('input');
    startval = $theinput.val()
    var vlist = startval.split(',');
    if (vlist.length > 1){
        var i = vlist.indexOf(val);
        vlist.splice(i, 1);
        var newval = vlist.join();
    }
    //if the last item is being removed
    else {
        var newval = null;
    }

    //set the hidden input to the new value
    $theinput.val(newval);
    theinput = $theinput.attr('id');

    //set the select widget to the new value
    $select.val(newval.split(','));

    //get app name from URL stored on refresh_trigger link
    var r_url = $td.find('a.refresh_trigger').attr('href');
    var appname = r_url.split('/')[1];
    //update back end via ajax
    ajax('/' + appname + '/plugin_ajaxselect/setval/' + theinput,
                                        ['"' + theinput + '"'], ':eval');

    event.preventDefault();

});

$('.restrictor select').live('change', function(event){
//constrain and refresh appropriate select widgets if restrictor widget's
//value is changed

    //get selected value of the restrictor widget to use in constraining the
    //target widget
    var new_val = $(this).find('option:selected').val();

    //get table of the current form from id of restrictor widget
    var parts = $(this).attr('id').split('_');
    var table = parts[0];
    //get field of the restrictor widget, again from its id
    var r_field = parts[1];

    var classlist = $(this).parents('span').attr('class').split(/\s+/);
    var linktable = classlist[1]
    //constrain and refresh each widget with a corresponding 'for_' class on
    //the restrictor widget
    //TODO: add logic in module to insert a for_ class for multiple
    //constrained fields
    $.each(classlist, function(index,item){
       if(item.substring(0,4) == 'for_'){
           //get name of field for widget to be constrained, from the
           //restrictor's classes
           field = item.substring(4);
           //assemble name for span wrapping the widget to be constrained
           var span_id = table + '_' + field + '_loader'
           //assemble url to use for refreshing the constrained widget
           //from url set in modules/plugin_ajaxselect.py for adder
           //this should include the vars (url params) 'fieldval' and
           //'multi'
           var r_url = $('#' + span_id + ' .refresh_trigger').attr('href');
           r_url += '&rval=' + new_val + '&rtable=' + linktable;
           //refresh the widget by refreshing the contents of the wrapper
           //component
           web2py_component(r_url, span_id);
       }
    });
});

//supply .indexOf function to ie browsers before ie8
if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (searchElement /*, fromIndex */ ) {
        "use strict";
        if (this == null) {
            throw new TypeError();
        }
        var t = Object(this);
        var len = t.length >>> 0;
        if (len === 0) {
            return -1;
        }
        var n = 0;
        if (arguments.length > 0) {
            n = Number(arguments[1]);
            if (n != n) { // shortcut for verifying if it's NaN
                n = 0;
            } else if (n != 0 && n != Infinity && n != -Infinity) {
                n = (n > 0 || -1) * Math.floor(Math.abs(n));
            }
        }
        if (n >= len) {
            return -1;
        }
        var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);
        for (; k < len; k++) {
            if (k in t && t[k] === searchElement) {
                return k;
            }
        }
        return -1;
    }
}
