window.update_balance = (form_elem=$(document.body))->

    accounts = get_accounts_list form_elem

    currency = form_elem.find "[name='currency']"

    url = conf.balance_url

    params = {}

    params["accounts"] = (acc.mt4_id for acc in accounts)

    if currency.length
        params["currency"] = currency.val()

    $.getJSON(url, params, (xhr)->

        if xhr.status != "ok" or xhr.payload == null
            return

        data = xhr.payload

        # обновляем список счетов информацией о балансе
        for elem in accounts
            mt4_id = elem.mt4_id
            if data[mt4_id] != undefined and data[mt4_id]["balance"] != ""
                $(elem).text("#{elem.text_orig}: #{data[mt4_id]["balance"]}")
                elem.balance = data[mt4_id]["balance"]
        return
    )
    return

get_accounts_list = (form_elem) ->
    accounts = []
    # в разных формах список счетов может быть назван 'account' или 'sender'
    if form_elem.find("[name='account']").length
        opts = form_elem.find("[name='account'] option")
    else
        opts = form_elem.find("[name='sender'] option")

    for elem in opts
        if not elem.text.match("^----") and not elem.text_orig and not elem.mt4_id
            elem.text_orig = elem.text
            elem.mt4_id = elem.text.match("^[0-9]+")[0]
        accounts.push(elem)

#    if conf.show_link_to_deposit
#
#        price = parseInt(currency.prev().text().match("^[0-9]+"))
#        selectbox.after($("<div id='deposit' style='display:none;'>
#                           <a href=''>Пополнить счет</a></div>
#                           <div class='clear'></div>"))
#        selectbox.css("float", "left")
#        selectbox.css("margin-right", "30px")
#
#        selectbox.change(()->
#            opt = $(selected)[0]
#            d = $("#deposit")
#            if opt.balance < price
#                d.find("a")[0].href = conf.deposit_url.replace("123456", opt.account)
#                d.show()
#            else
#                d.hide()
#            return
#        )

    return accounts


if conf.load_balances_on_init
    $(() ->
        currency = $("[name='currency']")
        currency.change(() ->
            update_balance()
        )

        update_balance()
        return
    )
