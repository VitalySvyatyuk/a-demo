function setup_mask(country_select) {
   var mask = $('option:selected', country_select).attr("data-phone-mask");
   if (!mask) {mask = "(999) 999-9999";}
   country_select.next().mask(mask);
}

$(function () {
    var possible_selectors = $("#id_phone_mobile_0, #id_phone_0, #id_phone_home_0, #id_phone_work_0, #id_profile-phone_mobile_0, [name='purse_0']");
    possible_selectors.change(function() {
       setup_mask($(this));
    });
    possible_selectors.change();
});