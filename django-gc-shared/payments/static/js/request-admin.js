$(function () {
    $('a.change-committed').each(function () {
        $(this).click(function () {
            var element = $(this);
            var request_id = /\d+/.exec(element.attr('id')).pop();
            var dialog_element = $("#change-committed-dialog");

            $('div#payment_data').html('Loading payment data');

            $.getJSON(REQUEST_DATA_URL + '?id=' + request_id, function (data) {
                $('div#payment_data').html(data.html);

                dialog_element.find('textarea#public-comment').autocomplete({
                source: TYPICAL_COMMENTS['public'],
                delay: 100,
                minLength: 0
                }).focus(function () {
                        if (this.value == "") {
                            $(this).autocomplete('search', '');
                        }
                    });

                dialog_element.find('textarea#private-comment').autocomplete({
                    source: TYPICAL_COMMENTS['private'],
                    delay: 100,
                    minLength: 0
                }).focus(function () {
                        if (this.value == "") {
                            $(this).autocomplete('search', '');
                        }
                    });

                dialog_element.find('select,input,textarea').each(function () {
                    var param = $(this);
                    if (param.attr('name') == 'csrfmiddlewaretoken') {
                        return;
                    }
                    var new_value = data.object[param.attr('name')];
                    if (new_value == null) {
                        new_value = ''
                    } else {
                        new_value = new_value.toString()
                    }
                    param.val(new_value);
                });
                dialog_element.find('input[name="request_id"]').val(request_id);

//                django-clone start
                $("fieldset.collapse a.collapse-toggle", '#payment_data').toggle(function () {
                    $(this).text(gettext("Hide"));
                    $(this).closest("fieldset").removeClass("collapsed");
                    return false
                }, function () {
                    $(this).text(gettext("Show"));
                    $(this).closest("fieldset").addClass("collapsed");
                    return false
                });
//                django-clone end
            });
            dialog_element.attr('title', 'Request details');

            dialog_element.dialog("close");

            dialog_element.dialog({
                width: 350,
                modal: true,
                buttons: {
                    "Save": function () {
                        // FIXME: A better way to find the button?
                        button = $('.ui-dialog-buttonset button:contains("Save")');
                        button.attr('disabled', 'true');
                        var form = dialog_element.find('form');
                        $.ajax({
                            type: 'POST',
                            url: REQUEST_UPDATE_URL,
                            data: form.serialize(),
                            success: function (data) {
                                if ("no_money" in data) {
                                    button.removeAttr('disabled');
                                    alert("Not enough money");
                                }
                                else if ("invalid_requisit" in data) {
                                    button.removeAttr('disabled');
                                    alert("Payment details not verified. To process payment, verify them.");
                                }
                                else {
                                    // Reload the window not to fuck with partially reloading the changelist
                                    window.location.reload();
                                    // TODO: load the html content in the background, and replace
                                    // current stuff with its' contents
                                }
                            },
                            error: function () {
                                button.removeAttr('disabled');
                                alert("Failed, try again later.");
                            }
                        });
                    },
                    "Cancel": function () {
                        $(this).dialog("close");
                    }
                },
                close: function () {
                    $(this).find('input').val('');
                }
            });
        })
    })
});
