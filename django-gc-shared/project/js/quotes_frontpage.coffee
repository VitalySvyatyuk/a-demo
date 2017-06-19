$(() ->
    client = new QuotesReceiver()

    for symbol in symbol_list
        client.subscribe(symbol, symbol+'_frontpage', (message) ->
            quote = JSON.parse message.data
            el = $("tr.quotes##{quote.symbol}")

            open_price = parseFloat el.data("open-price").toString().replace(",", ".")
            spread_digits = el.data("spread-digits")

            bid = quote.bid
            ask = quote.ask

            old_bid = parseFloat(el.find(".bid").text().replace(",", "."))

            if bid > old_bid
                el.removeClass "down"
                el.addClass "up"
            else if bid < old_bid
                el.removeClass "up"
                el.addClass "down"

            symbol = if bid > open_price then "+" else ""

            percents = ((bid - open_price)/open_price * 100).toFixed 2

            el.find(".bid").text bid.toFixed(el.data("digits"))
            el.find(".ask").text ask.toFixed(el.data("digits"))
            el.find(".percents").text "#{symbol}#{percents}%"
            el.find(".spread").text (((ask-bid)*spread_digits)/10).toFixed(1)
            return
        )
    return
)
