app.controller "AccountsController", ($scope, Mt4Account, $interval, accounts, type, AccountBlockedInfoModal, RecoverPasswordModal, ChangeLeverageModal, ChangeOptionsStyleModal, DemoDepositModal) ->
  getTotalRealUSD = ->
    _($scope.accounts).reduce (memo, acc) ->
      return memo unless $scope.mt4Data[acc.mt4_id] and not acc.is_demo
      memo + $scope.mt4Data[acc.mt4_id].balance_usd_amount
    , 0

  getReferralUSD = ->
    _($scope.accounts).reduce (memo, acc) ->
      return memo unless $scope.mt4Data[acc.mt4_id] and not acc.is_demo
      memo + $scope.mt4Data[acc.mt4_id].referral_usd_amount
    , 0

  tmpObject = {
    mt4:'trading',
    cfh: 'pro',
    strategy_store: 'invest'
  }

  $scope.selectCategory = (type) ->

    if $scope.selectedCategoryList
      if type not in $scope.selectedCategoryList
        $scope.selectedCategoryList.push type
      else
        $scope.selectedCategoryList = (x for x in $scope.selectedCategoryList when x != type)
    else
      $scope.selectedCategoryList = [type, ]
    $scope.selectedCategory =  type

  $scope.markCategory = (type) ->
    $scope.selectedCategory =  type


  tmpResult = accounts.reduce ((current, val) ->
    current[val.platform_type] = current[val.platform_type] or 0
    current[val.platform_type]++
    current
  ), {}

  Object.keys(tmpResult).filter((val) ->
    tmpResult[val] > 0
  ).forEach (val) ->
    $scope.selectCategory tmpObject[val]

  $scope.loadMt4Data = (ids) ->
    return unless ids.length > 0
    Mt4Account.batchMt4Data ids
    .then (res) ->
      _($scope.mt4Data).extend res.data

  #page logic
  $scope.selectAccount = (account) ->
    $scope.account = account


  $scope.toggleShowMoney = ->
    $scope.showMoney = !$scope.showMoney

  # Some common helpers
  $scope.formatComission = (obj) ->
    obj.payout_system_display + ' - ' + obj.fee_rate + (if obj.payout_system is 2 then ' USD' else '%')

  $scope.accountBlockInfo = ->
    AccountBlockedInfoModal($scope.account, $scope.issue_chargeback_created)

  # Common methods to work with accounts
  $scope.accountActions =
    recoverPassword: ->
      RecoverPasswordModal $scope.account

    changeLeverage: ->
      ChangeLeverageModal $scope.account,
        if $scope.mt4Data then $scope.mt4Data[$scope.account.mt4_id]?.leverage else null
      .result.then (newLeverage) ->
        $scope.mt4Data[$scope.account.mt4_id].leverage = newLeverage if $scope.mt4Data

    changeOptionsStyle: ->
      ChangeOptionsStyleModal $scope.account

    openHistory: ->
      AccountHistoryModal.open $modal, $scope.account

    demoDeposit: ->
      DemoDepositModal $scope.account
      .result.then (addedBalance) ->
        if $scope.mt4Data
          $scope.account.getMt4Data().then (data)->
            $scope.mt4Data[$scope.account.mt4_id] = data

  # Init
  $scope.mt4Data = {}
  $scope.accountsPageType = type
  $scope.showMoney = true
  $scope.accounts = accounts
  $scope.totalRealUSD = null

  if $scope.accounts.length > 0
    is_partnership = $scope.accounts[0].ib_data != null
    $scope.loadMt4Data _($scope.accounts).pluck('mt4_id')
    .then (res) ->
      $scope.totalRealUSD = if is_partnership then getReferralUSD() else getTotalRealUSD()
