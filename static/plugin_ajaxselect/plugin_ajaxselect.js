//open modal dialog (using jquery-ui dialog) for 
$('.add_trigger').live('click', function(event){
    var the_id = $(this).attr('id');
    var parts = the_id.split('_');
    var linktable = parts[0];

    $('#' + linktable + '_adder_form').dialog({
        height:200,
        width:500,
        title:'Add new '
    });
});

$('.restrictor').live('change', function(event){
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