app.controller "AccountHistoryController", ($scope, $routeParams, Paginator, Mt4Trade, openTrades, closeTrades) ->
  reloadTrades = ->
    $scope.trades.params.date_from = $scope.dateFrom
    $scope.trades.params.date_to = $scope.dateTo
    $scope.trades.load()

  $scope.filterToday = ->
    $scope.filterMode = 'today'
    $scope.dateFrom = $scope.dateTo = moment().format("YYYY-MM-DD")
    reloadTrades()

  $scope.filterYesterday = ->
    $scope.filterMode = 'yesterday'
    $scope.dateFrom = $scope.dateTo = moment().subtract(1, 'day').format("YYYY-MM-DD")
    reloadTrades()

  $scope.filterWeek = ->
    $scope.filterMode = 'week'
    today = moment()
    $scope.dateFrom = today.startOf('week').format("YYYY-MM-DD")
    $scope.dateTo = today.endOf('week').format("YYYY-MM-DD")
    reloadTrades()

  $scope.filterMonth = ->
    $scope.filterMode = 'month'
    today = moment()
    $scope.dateFrom = today.startOf('month').format("YYYY-MM-DD")
    $scope.dateTo = today.endOf('month').format("YYYY-MM-DD")
    reloadTrades()

  $scope.clearFilter = ->
    $scope.dateFrom = $scope.dateTo = ''
    $scope.filterMode = null

  $scope.filterRange = ->
    $scope.filterMode = 'range'
    reloadTrades()

  $scope.switchTradesMode = (mode) ->
    $scope.tradesMode = mode
    $scope.trades = if mode is 'opened'
      openTrades
    else if mode is 'closed'
      closeTrades
    reloadTrades()

  $scope.mt4accountMt4ID = $routeParams.mt4account
  $scope.$watch 'trades.isLoading', $scope.setGlobalLoading
  $scope.switchTradesMode 'opened'
