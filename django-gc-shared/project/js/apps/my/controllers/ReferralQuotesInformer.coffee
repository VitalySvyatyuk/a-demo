app.constant 'QuotesInformerConstant',
  BASE_URL: "https://#{window.location.host}/informers/quotes/?"
  COLOR_BG: "#ffffff"
  COLOR_TEXT: "#424243"
  COLOR_HEADS: "#51b097"
  IFRAME_ID: "gc_quotes"
  QUOTES_LIMIT: 8

app.controller "ReferralQuotesInformerController", ($scope, $http, QuotesInformerConstant) ->
  $scope.isQuoteChecked = (quote) ->
    quote in $scope.checkedQuotes

  $scope.checkQuote = (quote) ->
    if quote in $scope.checkedQuotes
      $scope.checkedQuotes = _.without $scope.checkedQuotes, quote
      sendMessageToIframe "remove-quote": quote
      $scope.quotesLimitReached = false
    else
      sendMessageToIframe "add-quote": quote
      $scope.checkedQuotes.push quote
      if $scope.checkedQuotes.length >= QuotesInformerConstant.QUOTES_LIMIT
        $scope.quotesLimitReached = true
    $scope.updateInformer()

  $scope.updateInformer = ->
    params =
      api_key: if $scope.selectedDomain then $scope.selectedDomain.api_key else ''
      bg: $scope.quotesColors.bg[1..]
      text: $scope.quotesColors.text[1..]
      heads: $scope.quotesColors.heads[1..]
      symbol: $scope.checkedQuotes
    informerParams.src = QuotesInformerConstant.BASE_URL + $.param params

    newAttrs = ("#{k}=\"#{v}\"" for k, v of informerParams)
    $scope.informerCode = "<iframe #{newAttrs.join(" ")}></iframe>"

  informerParams =
    frameborder: 0
    scrolling: "no"
    width: 300
    height: 400
    allowtransparency: true

  $scope.quotesColors =
    bg: QuotesInformerConstant.COLOR_BG
    text: QuotesInformerConstant.COLOR_TEXT
    heads: QuotesInformerConstant.COLOR_HEADS

  sendMessageToIframe = (msgData) ->
    informerWindow = document.getElementById(QuotesInformerConstant.IFRAME_ID).contentWindow
    informerWindow.postMessage msgData, '*'

  $scope.$watch 'quotesColors.bg', (val) ->
    sendMessageToIframe "background-color": val
    $scope.updateInformer()

  $scope.$watch 'quotesColors.text', (val) ->
    sendMessageToIframe "text-color": val
    $scope.updateInformer()

  $scope.$watch 'quotesColors.heads', (val) ->
    sendMessageToIframe "head-color": val
    $scope.updateInformer()

  $http.get "/informers/get_quotes_list/"
  .success (data) ->
    $scope.checkedQuotes = data.default_quotes
    if $scope.checkedQuotes.length >= QuotesInformerConstant.QUOTES_LIMIT
      $scope.quotesLimitReached = true
    $scope.quotes = data.quotes
    $scope.updateInformer()
  $scope.$watch 'selectedDomain', $scope.updateInformer
