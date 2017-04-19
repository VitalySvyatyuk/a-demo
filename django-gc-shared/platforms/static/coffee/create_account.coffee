modal = $("[data-reveal]")

modal.find("#throbber").show()
$("body").off("submit", "[data-reveal] form")
is_submitting = false

$("#create_response #continue_btn").on("click", (e)->
  modal.find("a.close-reveal-modal").show()
  $('a.close-reveal-modal').trigger('click')

  if window.location.href.indexOf('/account/trading') > -1 and angular  # refresh page to add a new account in the table
    angular.element('[ng-controller="AccountsLammInvestmentsController"]').scope().refresh_page()
)

$("[data-reveal]").on("submit", "form", (e)->
    e.preventDefault()
    if is_submitting
        return
    is_submitting = true
    modal.find("#create_form").hide()
    modal.find("#wait_for_create").show()
    form_el = $(this)
    $.post(
        form_el.attr("action"),
        form_el.serialize(),
        (data) ->
            if data.ok
                $("a.close-reveal-modal").hide()
                if data.wait
                    check_account_creation = () ->
                        $.get(data.wait, (data) ->
                                if data.ready
                                    clearInterval timer_id
                                    if ACCOUNT_CREATE_HANDLER?
                                        modal.find("#wait_for_create").hide()
                                        modal.find("#create_response #mt4_id").text data.mt4_id
                                        # if account is SS then we need login
                                        if data.platform == 'strategy_store'
                                            modal.find("#create_response #acc_login").text data.login
                                            modal.find("#create_response #account_login_row").show()
                                        else
                                            modal.find("#create_response #account_login_row").hide()
                                        modal.find("#create_response #mt4_password").text data.mt4_password

                                        modal.find("#create_response #continue_btn").attr('href', ACCOUNT_APP_URL)
                                        if WEBTRADER_URL?
                                            modal.find("#create_response #open_wt_btn").attr('href', WEBTRADER_URL + 'login?account='+ data.mt4_id)
                                        else
                                            modal.find("#create_response #open_wt_btn").hide()
                                        modal.find("#create_response").show()
                                        return
                                    if form_el.data('next-popup')
                                        a = $("<a class='hide' data-reveal-form href='" + form_el.data('next-popup') + "'></a>")
                                        $("body").append a
                                        a.click()
                                    else
                                        window.location.href = data.redirect
                        ).fail(() ->
                            clearInterval timer_id
                            modal.find("a.close-reveal-modal").show()
                            $('a.close-reveal-modal').trigger('click')
                            alert ERROR_MSG
                        )

                    timer_id = setInterval check_account_creation, 1000
                else if data.no_wait
                    if ACCOUNT_CREATE_HANDLER?
                        modal.find("#wait_for_create").hide()
                        modal.find("#create_response #mt4_id").text data.mt4_id
                        # if account is not mt4 then we need login
                        if data.platform != 'mt4'
                            modal.find("#create_response #acc_login").text data.login
                            modal.find("#create_response #account_login_row").show()
                        else
                            modal.find("#create_response #account_login_row").hide()
                        modal.find("#create_response #mt4_password").text data.mt4_password

                        modal.find("#create_response #continue_btn").attr('href', ACCOUNT_APP_URL)
                        if WEBTRADER_URL?
                            modal.find("#create_response #open_wt_btn").attr('href', WEBTRADER_URL + 'login?account='+ data.mt4_id)
                        else
                            modal.find("#create_response #open_wt_btn").hide()
                        modal.find("#create_response").show()
                        return

                    if form_el.data('next-popup')?
                        a = $("<a class='hide' data-reveal-form href='" + form_el.data('next-popup') + "'></a>")
                        $("body").append(a)
                        a.click()
                    else
                        window.location.href = data.redirect
            else if data.redirect
                window.location.href = data.redirect
            else if data.errors
                is_submitting = false
                form_el.find("tr.errors, p.errors, div.errors").hide()
                for key, error of data.errors
                    el = form_el.find(".errors##{key}")
                    el.find("span").text error
                    el.show()
            return
    ).fail(() ->
        modal.find("a.close-reveal-modal").show()
        $('a.close-reveal-modal').trigger('click')
        alert ERROR_MSG
    )
)
