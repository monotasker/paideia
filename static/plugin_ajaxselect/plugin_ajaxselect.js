
$('.add_trigger').live('click', function(event){
//open modal dialog (using jquery-ui dialog) for adder form
    var the_id = $(this).attr('id');
    var parts = the_id.split('_');
    var linktable = parts[0];

    $('#' + linktable + '_adder_form').dialog({
        height:600,
        width:600,
        title:'Add new '
    });
});

$('.edit_trigger').live('click', function(event){
//open modal dialog (using jquery-ui dialog) for edit form
    var the_id = $(this).attr('id');
    var parts = the_id.split('_');
    var linktable = parts[0];

    $('#' + linktable + '_editlist_form').dialog({
        height:600,
        width:600,
        title:'Edit '
    });
});

$('.plugin_ajaxselect select').live('change', function(event){
    var $p = $(this).parents('span');
    var theid = $p.attr('id');   
    var theinput = theid + '_input';
    var theval = $(this).val();

    var $taglist = $p.parents('td').find('.taglist');
    $taglist.html('');
    $(this).find('option:selected').each(function(event){
        var theref = $(this).text();
        $taglist.append('<li class="tag">' + theref + '</li>');
    });
    $('#' + theinput).val(theval);
    ajax('/paideia/plugin_ajaxselect/setval/' + theinput, ['"' + theinput + '"'], ':eval');
    // empty input that stores the current value
    $('#' + theinput).val(null);
});

$('.restrictor').live('change', function(event){
//constrain and refresh appropriate select widgets if restrictor widget's value is changed
	//get selected value of the restrictor widget to use in constraining the target widget
    var new_val = $(this).find('option:selected').val();

    //get table of the current form from id of restrictor widget
    var parts = $(this).attr('id').split('_');
    var table = parts[0];
    //get field of the restrictor widget, again from its id
    var r_field = parts[1];

    var classlist = $(this).attr('class').split(/\s+/);
    var linktable = classlist[0]
	//constrain and refresh each widget with a corresponding 'for_' class on the restrictor widget
    $.each(classlist, function(index,item){
       if(item.substring(0,4) == 'for_'){
           //get name of field for widget to be constrained, from the restrictor's classes
           field = item.substring(4);
           //assemble name for span wrapping the widget to be constrained
           var span_id = table + '_' + field + '_loader'
           //assemble url to use for refreshing the constrained widget 
           //from url set in modules/plugin_ajaxselect.py for adder
           //this should include the vars (url params) 'fieldval' and 'multi'
           var r_url = $('#' + span_id).next().attr('href')
           r_url += 'restrictor=' + new_val + 'rtable' + linktable;
           //refresh the widget by refreshing the contents of the wrapper component
           web2py_component(r_url, span_id);
       }
    });
});