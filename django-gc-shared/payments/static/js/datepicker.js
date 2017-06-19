$(function(){
    $.datepicker.setDefaults({dateFormat:gettext('yy-mm-dd')});
    $("input.datepicker").datepicker();
});
