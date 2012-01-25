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
    var new_val = $(this).find('option:selected').val();
    var parts = $(this).attr('id').split('_');
    var table = parts[0];
    var r_field = parts[1];

    var classlist = $(this).attr('class').split(/\s+/);
    var linktable = classlist[0]
    $.each(classlist, function(index,item){
       if(item.substring(0,4) == 'for_'){
           //get name of field represented by target widget
           field = item.substring(4);
           //assemble name for target wrapper span
           var span_id = table + '_' + field + '_loader'           
           //assemble url to use for refreshing the widget
           var r_url = $('#' + span_id).next().attr('href')
           r_url += '/' + new_val + '/' + linktable;
           //refresh the widget by refreshing the contents of the wrapper component
           web2py_component(r_url, span_id);
       }
    });
});