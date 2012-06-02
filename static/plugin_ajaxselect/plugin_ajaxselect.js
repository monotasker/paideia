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


$('.plugin_ajaxselect select').live('change', function(event){
    //when select value is changed, update
    var $p = $(this).parents('span');
    var $td = $p.parents('td, li, div');
    var theid = $p.attr('id');
    var theinput = theid + '_input';
    var theval = $(this).val();

    var $taglist = $td.find('.taglist');
    $taglist.html('');
    //get url from beginning of request.args, and separate args from vars
    var r_url = $td.find('a.refresh_trigger').attr('href');
    var url_frag = r_url.match(/set_widget.load(.*)/);
    var url_args_vars = url_frag[1].split('?');
    var url_args = url_args_vars[0];
    var url_vars = url_args_vars[1];
    var appname = r_url.split('/')[1];
    var linktable = '{=linktable}';
    var link_base = '/' + appname + '/views/plugin_ajaxselect/set_form_wrapper.load';
    var formname = linktable + '_editlist_form';

    n = ''
    if($p.hasClass('lister_editlinks')){
        $(this).find('option:selected').each(function(event){
            var theref = $(this).text();
            var thisval = $(this).val();
            var link_url = link_base + url_args + '/' + thisval + '?' + url_vars;
            var script_string = "web2py_component('" + link_url + "', '" + formname + "')";

            n += '<li class="editlink tag">';
            n += '<a id="' + linktable + '_editlist_trigger_' + thisval + '" ';
            n += 'class="edit_trigger editlink tag" ';
            n += 'href="' + link_url + '" ';
            n += 'onclick="' + script_string + '; return false;">';
            n += theref + '</a></li>';
        });
        $taglist.append(n);
    }
    if($p.hasClass('lister_simple')){
        $(this).find('option:selected').each(function(event){
            var theref = $(this).text();
            n += '<li class="tag">' + theref + '</li>';
        });
        $taglist.append(n);
    }

    $('#' + theinput).val(theval);
    ajax('/' + appname + '/plugin_ajaxselect/setval/' + theinput, ['"' + theinput + '"'], ':eval');
    // empty input that stores the current value
    $('#' + theinput).val(null);
});

$('.restrictor select').live('change', function(event){
//constrain and refresh appropriate select widgets if restrictor widget's
//value is changed

    //get selected value of the restrictor widget to use in constraining the target widget
    var new_val = $(this).find('option:selected').val();

    //get table of the current form from id of restrictor widget
    var parts = $(this).attr('id').split('_');
    var table = parts[0];
    //get field of the restrictor widget, again from its id
    var r_field = parts[1];

    var classlist = $(this).parents('span').attr('class').split(/\s+/);
    var linktable = classlist[1]
    //constrain and refresh each widget with a corresponding 'for_' class on the restrictor widget
    //TODO: add logic in module to insert a for_ class for multiple constrained fields
    $.each(classlist, function(index,item){
       if(item.substring(0,4) == 'for_'){
           //get name of field for widget to be constrained, from the restrictor's classes
           field = item.substring(4);
           //assemble name for span wrapping the widget to be constrained
           var span_id = table + '_' + field + '_loader'
           //assemble url to use for refreshing the constrained widget
           //from url set in modules/plugin_ajaxselect.py for adder
           //this should include the vars (url params) 'fieldval' and 'multi'
           var r_url = $('#' + span_id + ' .refresh_trigger').attr('href');
           r_url += '&rval=' + new_val + '&rtable=' + linktable;
           //refresh the widget by refreshing the contents of the wrapper component
           web2py_component(r_url, span_id);
       }
    });
});


