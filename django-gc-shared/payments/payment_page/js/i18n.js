var string_i18n = {
    enter_card_details: {
        en: "Credit card details",
        ru: "Ввод данных карты"
    },
    card_number: {
        en: "Card number",
        ru: "Номер карты"
    },
    expiry: {
        en: "Expiration",
        ru: "Срок<br>действия"
    },
    cvc: {
        en: "CVC/CVV CODE",
        ru: "CVC/CVV КОД"
    },
    cvc_description: {
        en: "Last 3 digits printed on the back side of your credit card next to the signature strip. If your card does not have this code, please enter the last 3 digits of your card number.",
        ru: "Последние 3 цифры, напечатанные на оборотной стороне карты рядом с магнитной полосой типографским способом. Если на вашей карте код отсутствует - введите последние 3 цифры номера карты."
    },
    sum: {
        en: "Sum",
        ru: "Сумма"
    },
    name: {
        en: "Name on card",
        ru: "Имя на карте"
    },
    submit: {
        en: '<input type="submit" class="button" value="Submit"/>',
        ru: '<input type="submit" class="button" value="Отправить"/>'
    },
    title: {
        en: "Payment details",
        ru: "Ввод данных платежа"
    },
    incorrect_value: {
        en: 'Value is not correct!',
        ru: 'Неверное значение!'
    },
    required: {
        en: 'A required field!',
        ru: 'Обязательное поле!'
    }
};
function get_string(slug) {
    var lang = "en";
    if (typeof merchantReturnUrl !== 'undefined' && merchantReturnUrl.match(/grandcapital\.ru/i)) {
        lang = "ru";
    }
    return string_i18n[slug][lang];
}

var counter = 0;
function defer_i18n(slug) {
    var id = "deferred_i18n_" + counter;
    document.write('<span id="' + id + '"></span>');
    counter += 1;
    $(function () {
        $("#"+id).replaceWith(get_string(slug));
    });
}
$(function () {
    $("title").text(get_string('title'));
});