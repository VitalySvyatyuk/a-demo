class Receiver
    constructor: () ->
        @connected = false

    connect: () =>
        console.log "#{@class_name}. Connecting to #{@url}..."

        @client = new WebSocket(@url)

        @client.onerror = (error) ->
            console.log "Error at #{@class_name}"
            console.log error

        @client.onclose = () =>
            @connected = false
            @connect()

        @client.onopen = @on_connect

    on_connect: () =>
        @connected = true


class window.QuotesReceiver extends Receiver
    constructor: (@url=WEBSOCKET_TORNADO_URL, @class_name="QuotesReceiver", @mode="real") ->
        super()
        @to_be_connected = {}
        @subscriptions = {}
        @connect()
        @trades_callback = null
        @client.onmessage = @on_message

    on_message: (message) =>
        data = JSON.parse(message.data)
        if 'MsType' of data
            if @trades_callback
                @trades_callback message
        else
            symbol = data.symbol
            for callback of @to_be_connected[symbol]
                @to_be_connected[symbol][callback] message


    on_connect: () =>
        super()
        console.log "#{@class_name}. Connected to #{@url}. Switching mode to #{@mode}"
        @set_mode @mode
        if _.size(@to_be_connected)
            console.log "#{@class_name}. Resubscribing to #{_.size(@to_be_connected)} quote(s)..."
            for symbol of @to_be_connected
                for callback of @to_be_connected[symbol]
                    @subscribe symbol, callback, @to_be_connected[symbol][callback]
            console.log "#{@class_name}. Resubscribing complete"

    set_mode: (mode_name) =>
        @mode = mode_name
        if @connected
            @client.send "mode:#{mode_name}"

    subscribe: (symbol, uid, callback) ->
        if symbol of @to_be_connected
            @to_be_connected[symbol][uid] = callback
        else
            @to_be_connected[symbol] =
                uid: callback
        if @connected
            @client.onmessage = @on_message
            @client.send symbol

    subscribe_to_trades: (key, callback) ->
        @subscribe "trades:#{key}", null, null  # For resubscription
        @trades_callback = callback


    unsubscribe: (uid, callback) ->
        delete @to_be_connected[uid.split(",")[0]][uid]