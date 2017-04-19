@Calculator = class Calculator

  constructor: (@data, @exchange_rates) ->
    # User input form
    @contract_type = ko.observable ["ECN.MT", "ECN.PRO", "ECN.INVEST"]
    @contract_type_value = ko.observable()
    @contract_type_value.subscribe (val) =>
      @leverage(@data[val]["leverages"])
      if @data[val]["default_leverage"] in @data[val]["leverages"]
        @leverage_value(@data[val]["default_leverage"])

    @category = ko.computed =>
      if @contract_type_value()?
        @_getKeys @data[@contract_type_value()]["groups"]
      else
        []
    @category_value = ko.observable()
    @instrument = ko.computed =>
      if @contract_type_value()? and @category_value()?
        @_getKeys @data[@contract_type_value()]["groups"][@category_value()]
    @instrument_value = ko.observable()
    @action_type = ko.observable ["buy", "sell"]
    @action_type_value = ko.observable()
    @lots = ko.observable 1
    @open_price = ko.observable 0
    @close_price = ko.observable 0
    @balance = ko.observable 5000
    @deposit_currency = ko.computed =>
      if @contract_type_value()?
        return @data[@contract_type_value()]["currencies"]
      else
        return []
    @deposit_currency_value = ko.observable()
    @show_currency_rate1 = ko.observable()
    @show_currency_rate2 = ko.observable()
    @currency_rate1 = ko.observable()
    @currency_rate2 = ko.observable()

    @leverage_value = ko.observable()
    @leverage = ko.observable()

    @coefficient = ko.observable()
    @margin_coefficient = ko.observable()

    # Results
#    profit is calculated based on the value of the profit_mode
#    if 0 FOREX [ (Close_price - open_price) х contract_size х lots ]
#    if 1 CFD [ (Close_price - open_price)  х contract_size х lots ]
#    if 2 FUTURE [(Close_price - open_price) х tick_price / tick_size х lot]

    @result_profit = ko.computed =>
      if @contract_type_value()? and @open_price()? and @close_price()? and @lots()? and @coefficient()?
        diff = 0
        if @action_type_value()?
          if @action_type_value() is "sell"
            diff = @_parseFloat(@open_price()) - @_parseFloat(@close_price())
          else
            diff = @_parseFloat(@close_price()) - @_parseFloat(@open_price())
        current_instrument = @data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]

        if current_instrument["profit_mode"] == 0 or current_instrument["profit_mode"] == 1
          "#{@_roundFloat(diff \
          * @_parseFloat(current_instrument["contr_size"]) \
          *  @_parseFloat(@lots()) * @_parseFloat(@coefficient()), 2)} #{@deposit_currency_value()}"
        else if current_instrument["profit_mode"] == 2
          "#{@_roundFloat(diff \
          * @_parseFloat(current_instrument["tick_price"]) / @_parseFloat(current_instrument["tick_size"]) \
          *  @_parseFloat(@lots()), 2)} #{@deposit_currency_value()}"
        else
          alert "Error: incorrect value of the variable profit_mode."

    @result_profit_points = ko.computed =>
      if @contract_type_value()? and @instrument_value()? and @open_price()? and @close_price()? and @lots()?
        if @action_type_value()?
          if @action_type_value() is "sell"
            diff = @_parseFloat(@open_price()) - @_parseFloat(@close_price())
          else
            diff = @_parseFloat(@close_price()) - @_parseFloat(@open_price())
        "#{@_roundFloat(diff/@_parseFloat(@data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]["tick_size"]), 2)}"

    @result_point_price = ko.computed =>
      if @contract_type_value()? and @instrument_value()? and @open_price()? and @close_price()? and @lots()?
        if @_isForexOrCFDStock @category_value()
          "#{@_roundFloat(@_parseFloat(@data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]["contr_size"])\
          * @_parseFloat(@lots()) * @_parseFloat(@data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]["tick_size"]) * @_parseFloat(@coefficient()), 2)} #{@deposit_currency_value()}"
        else
          "#{@_roundFloat(@_parseFloat(@data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]["tick_price"]) * @_parseFloat(@lots()) * @_parseFloat(@coefficient()), 2)} #{@deposit_currency_value()}"

    @result_funds = ko.computed =>
      if @contract_type_value()? and @instrument_value()? and @result_profit()? and @balance()?
        "#{@_roundFloat(@_parseFloat(@result_profit()) + @_parseFloat(@balance()), 2)} #{@deposit_currency_value()}"

    # result_required_deposit is calculated based on the value of the profit_mode
      #Forex [ lots х contract_size / leverage х percentage /100]
      #CFD [lots х  contract_size *  market_price х percentage/100]
      #futures [ lots х initial_margin х percentage/100]
      #CFD-Index [lots х  contract_size х  market_price / tick_size х percentage/100]
      #CFD-LEVERAGE [lots х  contract_size х market_price / leverage х percentage /100]

    @result_required_deposit = ko.computed =>
      if @contract_type_value()? and @instrument_value()? and @lots()? and @leverage_value()?
        current_instrument = @data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]
        if current_instrument['margin_mode'] == 0
          "#{@_roundFloat(@_parseFloat(@lots()) * @_parseFloat(current_instrument["contr_size"]) / @_getLeverage(@leverage_value()) * @_parseFloat(current_instrument["percentage"]) / 100.0 * @margin_coefficient(), 2)} #{@deposit_currency_value()}"
        else if current_instrument['margin_mode'] == 1
          "#{@_roundFloat(@_parseFloat(@lots()) * @_parseFloat(current_instrument["contr_size"]) * @_parseFloat(@open_price()) * @_parseFloat(current_instrument["percentage"]) / 100.0 * @margin_coefficient(), 2)} #{@deposit_currency_value()}"
        else if current_instrument['margin_mode'] == 2
          "#{@_roundFloat(@_parseFloat(@lots()) * @_parseFloat(current_instrument["margin_internal"]) * @_parseFloat(current_instrument["percentage"]) / 100.0 * @margin_coefficient(), 2)} #{@deposit_currency_value()}"
        else if current_instrument['margin_mode'] == 3
          "#{@_roundFloat(@_parseFloat(@lots()) * @_parseFloat(current_instrument["contr_size"]) * @_parseFloat(@open_price()) / @_parseFloat(current_instrument["tick_size"]) * @_parseFloat(current_instrument["percentage"]) / 100.0 * @margin_coefficient(), 2)} #{@deposit_currency_value()}"
        else if current_instrument['margin_mode'] == 4
          "#{@_roundFloat(@_parseFloat(@lots()) * @_parseFloat(current_instrument["contr_size"]) * @_parseFloat(@open_price()) / @_getLeverage(@leverage_value()) * @_parseFloat(current_instrument["percentage"]) / 100.0 * @margin_coefficient(), 2)} #{@deposit_currency_value()}"
        else
          alert "Error: incorrect value of the variable margin_mode."


#        if @_isForexOrCFDStock(@category_value())
#          "#{@_roundFloat((@_parseFloat(@lots()) * @_parseFloat(@data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]["contr_size"]) \
#          * @margin_coefficient()) / @_getLeverage(@leverage_value()))} #{@deposit_currency_value()}"
#        else
#          "#{@_roundFloat((@_parseFloat(@lots()) * @_parseFloat(@data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]["margin_internal"]))\
#          * @margin_coefficient())} #{@deposit_currency_value()}"

    @result_max_loss = ko.computed =>
      if @contract_type_value()? and @instrument_value()? and @result_required_deposit()? and @lots()? and @balance()?
        "#{Math.abs(@_roundFloat(0.4 * @_parseFloat(@result_required_deposit()) - @_parseFloat(@balance()), 2))} #{@deposit_currency_value()}"

    @show_calculator_error = ko.computed =>
      if @contract_type_value()? and @instrument_value()? and @result_required_deposit()? and @lots()? and @balance()? and @result_max_loss()?
        if @_parseFloat(@result_required_deposit()) > @_parseFloat(@balance())
          true
        else
          false
      else
        false


    # Subscribtions
    @contract_type_value.subscribe (newValue) =>
      if not newValue?
        # if contract type is not chosen set price the values to 0
        @open_price 0
        @close_price 0
      false

    @instrument_value.subscribe (newValue) =>
      if newValue?
        if @action_type_value() is "buy"
          @open_price @_roundFloat(@data[@contract_type_value()]["groups"][@category_value()][newValue]["ask"], 5)
          @close_price @_roundFloat(@data[@contract_type_value()]["groups"][@category_value()][newValue]["bid"], 5)
        else
          @open_price @_roundFloat(@data[@contract_type_value()]["groups"][@category_value()][newValue]["bid"], 5)
          @close_price @_roundFloat(@data[@contract_type_value()]["groups"][@category_value()][newValue]["ask"], 5)

        if @deposit_currency_value()?
          from_curr = @data[@contract_type_value()]["groups"][@category_value()][newValue]["currency"]
          margin_curr = @data[@contract_type_value()]["groups"][@category_value()][newValue]["margin_currency"]
          to_curr = @deposit_currency_value()
        @currency_rate1(@_roundFloat(@_getConvertCurrencyValue(from_curr, to_curr), 5))
        if @deposit_currency_value() == @data[@contract_type_value()]["groups"][@category_value()][newValue]["currency"]
          @show_currency_rate1(false)
        else
          @show_currency_rate1(true)
        @currency_rate2(@_roundFloat(@_getConvertCurrencyValue(margin_curr, to_curr), 5))
        if @deposit_currency_value() == @data[@contract_type_value()]["groups"][@category_value()][newValue]["margin_currency"]
          @show_currency_rate2(false)
        else
          @show_currency_rate2(true)
      false

    @deposit_currency_value.subscribe (newValue) =>
      if newValue? and @instrument_value()?
        from_curr = @data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]["currency"]
        margin_curr = @data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]["margin_currency"]
        to_curr = newValue
        if from_curr isnt to_curr
          @coefficient @_getConvertCurrencyValue from_curr, to_curr
        else
          @coefficient 1
        if margin_curr isnt to_curr
          @margin_coefficient @_getConvertCurrencyValue from_curr, to_curr
        else
          @margin_coefficient 1
        @currency_rate1(@_roundFloat(@_getConvertCurrencyValue(from_curr, to_curr), 5))
        if newValue == @data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]["currency"]
          @show_currency_rate1(false)
        else
          @show_currency_rate1(true)
        @currency_rate2(@_roundFloat(@_getConvertCurrencyValue(margin_curr, to_curr), 5))
        if newValue == @data[@contract_type_value()]["groups"][@category_value()][@instrument_value()]["margin_currency"]
          @show_currency_rate2(false)
        else
          @show_currency_rate2(true)
      false

    @currency_rate1.subscribe (newValue) =>
      if newValue? and @instrument_value()? and @deposit_currency_value()?
        @coefficient(newValue)

    @currency_rate2.subscribe (newValue) =>
      if newValue? and @instrument_value()? and @deposit_currency_value()?
        @margin_coefficient(newValue)

    @lots.subscribe (newValue) =>
      # This value is in rage [0.01; 25]
      if newValue > 25
        @lots 25
      else if newValue < 0.01
        @lots 0.01
      false


  # Utility functions
  _parseFloat: (s) ->
    if typeof s == "string"
      s = s.replace(',', '.')
    parseFloat(s)

  _getKeys: (arr) ->
    result = []
    for k, v of arr
      result.push k
    result.sort()

  _isForex: (category) ->
    if (category is "Forex") or (category is "CFD Forex") or (category is "ECN Forex")
      return true
    else
      return false

  _isForexOrCFDStock: (category) ->
    if @_isForex(category) or (category is "CFD Stock")
      return true
    else
       return false

  _getLeverage: (lever) ->
    @_parseFloat lever.split(":")[1]

  _roundFloat: (x, n) ->
    if not parseInt(n)
      n = 4
    if @_parseFloat(x) is NaN
      return false
    Math.round(x*Math.pow(10, n)) / Math.pow(10, n)

  _getConvertCurrencyValue: (from_currency, to_currency) ->
    if from_currency is to_currency
      return 1
    if from_currency is "USD"
      if to_currency is "GOLD"
        if @exchange_rates["USDXAU_ask"]?
          @exchange_rates["USDXAU_ask"]
        else
          alert "Failed to get gold exchange rate"
          null
      else if to_currency is "SILVER"
        if @exchange_rates["USDXAG_ask"]?
          @exchange_rates["USDXAG_ask"]
        else
          alert "Failed to get silver exchange rate"
          null
      else if to_currency is "RUR" or to_currency is "RUB"
        @exchange_rates["USDRUR_ask"]
      else
        if @data[@contract_type_value()]["groups"][@category_value()]["USD"+to_currency]?
          @data[@contract_type_value()]["groups"][@category_value()]["USD"+to_currency]["ask"]
        else if @data[@contract_type_value()]["groups"][@category_value()][to_currency+"USD"]?
          1 / @data[@contract_type_value()]["groups"][@category_value()][to_currency+"USD"]["ask"]
        else if @data["Standard"]["groups"]["Forex"]["USD"+to_currency]?
          @data["Standard"]["groups"]["Forex"]["USD"+to_currency]["ask"]
        else
          1 / @data["Standard"]["groups"]["Forex"][to_currency+"USD"]["ask"]
    else if to_currency is "USD"
      if from_currency is "RUR" or from_currency is "RUB"
        1 / @exchange_rates["USDRUR_ask"]
      else if @data[@contract_type_value()]["groups"][@category_value()]["USD"+from_currency]
        1 / @data[@contract_type_value()]["groups"][@category_value()]["USD"+from_currency]["ask"]
      else if @data[@contract_type_value()]["groups"][@category_value()][from_currency+"USD"]
        @data[@contract_type_value()]["groups"][@category_value()][from_currency+"USD"]["ask"]
      else if @data[@contract_type_value()]["groups"][@category_value()]["USD"+from_currency+"."]
        1 / @data[@contract_type_value()]["groups"][@category_value()]["USD"+from_currency+"."]["ask"]
      else if @data[@contract_type_value()]["groups"][@category_value()][from_currency+"USD."]
        @data[@contract_type_value()]["groups"][@category_value()][from_currency+"USD."]["ask"]
      else if @data[@contract_type_value()]["groups"][@category_value()]["USD"+from_currency+"_FX"]
        1 / @data[@contract_type_value()]["groups"][@category_value()]["USD"+from_currency+"_FX"]["ask"]
      else if @data[@contract_type_value()]["groups"][@category_value()][from_currency+"USD_FX"]
        @data[@contract_type_value()]["groups"][@category_value()][from_currency+"USD_FX"]["ask"]
      else
        @data["Standard"]["groups"]["Forex"][from_currency+"USD"]["ask"]
    else
      @_getConvertCurrencyValue(from_currency, "USD") * @_getConvertCurrencyValue("USD", to_currency)
