var uid = null;

noop = function(e) {
    e.preventDefault();
};

on_submit = function(e) {
    e.preventDefault();

    $("body").off("submit", "[data-reveal] form", on_submit).on("submit", "[data-reveal] form", noop);
    var that = $(this);
    that.find(".errors").hide();
    $.post(
        this.action,
        that.serialize(),
        function(data) {
            if (data.ok) {

                that.find("#content").hide();
                that.find("#throbber").show();

                if (data.yandex_goal) {
                    if (typeof yaCounter911141 !== 'undefined') {
                        yaCounter911141.reachGoal(data.yandex_goal);
                    }
                }

                if (data.redirect) {
                    a = $("<a class='hide' data-reveal-form href='" + data.redirect + "'></a>");
                    $("body").append(a);
                    a.click();
                }
                else if (data.simple_redirect) {
                    window.location.href = data.simple_redirect;
                }
                else if (data.alert) {
                    alert(data.alert);
                    // close pop-up
                    $(that).parents(".inner").siblings("a.close-reveal-modal").click();
                }
            }
            else if (data.errors) {
                console.log(data.errors);
                for (var key in data.errors) {
                    var err = that.find("#" + key + ".errors").find("td, span");
                    console.log(err);
                    err.html(data.errors[key].join("<br>")).parent().show();
                }
            }
        }
    )
    .fail(function() {
        alert( "Произошла ошибка, попробуйте позже. Если ошибка повторится снова, обратитесь в службу поддержки.");
    }).always(function() {
        $("body").off("submit", "[data-reveal] form", noop).on("submit", "[data-reveal] form", on_submit);
    });
};

$("body").on("click", "button[data-reveal-form], a[data-reveal-form], span[data-reveal-form]", function(e) {
    e.preventDefault();
    $("#" + uid).remove();
    uid = "a" + UUID.genV4().hexString;
    $("body").append("<div class='reveal-modal hide reveal-modal-alt' id='" + uid + "' data-reveal></div>");
    $(document).foundation();
    var href = $(this).attr('href');
    if (typeof href === 'undefined' || href === false) {
        href = $(this).attr('data-reveal-href');
    }
    $("#" + uid).foundation('reveal', 'open', {
        url: href,
        success: function(data) {
          if (data.simple_redirect) {
             window.location.href = data.simple_redirect;
           }
        }
    });
}).on("submit", "[data-reveal] form", on_submit);

$(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
    $(this).find('input:first').focus();
});

var getUrlParameter = function (sParam) {
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++)
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam)
        {
            return sParameterName[1];
        }
    }
};

$(document).ready(function(){
    console.log(getUrlParameter('continue_registration'));
    if (getUrlParameter('continue_registration') === 'true') {
        a = $("<a class='hide' data-reveal-form href='" + '/my/accounts/register' + "'></a>");
        $("body").append(a);
        a.click();
    }
});

