$(function () {
    function goto_step2(prefix) {
        $("#" + prefix + "_step1").hide();
        $("#" + prefix + "_step2").show();
        $("#" + prefix + "_send").remove();
    }

    if (STEP_2) goto_step2("sms");
    else $("#sms_step2").hide();

    $("#sms_send").click(function (event) {
        event.preventDefault();

        var post_params = $("#otp_form, #add_sms_device").serialize();

        if (TARGET == 'preview') {
            var phone_number = $("#id_phone_mobile_0").val() + $("#id_phone_mobile_1").val();

            if (!phone_number) {
                alert(gettext("Please enter your phone number"));
                return;
            }
        }
        $.post(
            SEND_SMS_ADDRESS,
            post_params + "&target=" + TARGET,
            function (data) {
                if (data.ok) {
                    if (TARGET == "preview") $("[name='preview_hash']").val(data.hash);
                    else $("[name='hash']").val(data.hash);

                    goto_step2("sms");
                }
                else if (data.bad_phone) {
                    goto_step2("sms");
                }
                else if (data.too_much_retries) {
                    alert(gettext("You are asking for too many text messages. Please Wait 5 minutes and try again later"));
                }
                else {
                    alert(gettext("Error happened, try again later"));
                }
            }
        );
    });

    $("#make_call").click(function (event) {
        event.preventDefault();

        var post_params = $("#otp_form, #add_sms_device").serialize();

        if (TARGET == 'preview') {
            var phone_number = $("#id_phone_mobile_0").val() + $("#id_phone_mobile_1").val();
            if (!phone_number) {
                alert(gettext("Please enter your phone number"));
                return;
            }
        }
        $.post(
            MAKE_CALL_ADDRESS,
            post_params + "&target=" + TARGET,
            function (data) {
                if (data.ok) {
                    alert(gettext("The automated call was queued"));

                    if (TARGET == "preview") $("[name='preview_hash']").val(data.hash);
                    else $("[name='hash']").val(data.hash);

                    $("#div_token").find(".description").text(gettext("Enter the code you heard"));

                    $("#automated_call").hide();
                    $("#no_automated_call").show();
                }
                else if (data.bad_phone) {
                    alert(gettext("Invalid phone number"));
                }
                else if (data.too_much_retries) {
                    alert(gettext("You are asking for too many calls. Please wait 5 minutes and try again later"));
                }
                else {
                    alert(gettext("Error happened, try again later"));
                }
            }
        );
    });
});
