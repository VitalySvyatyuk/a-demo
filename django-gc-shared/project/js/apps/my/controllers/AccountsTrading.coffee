app.controller "AccountsTradingController", ($scope) ->
  $scope.$watch 'selectedCategory', (value) ->

    if value == 'trading' &&  (!$scope.account? || $scope.account.platform_type != "mt4")
      if $scope.accounts.length > 0
        for acc in $scope.accounts
          if acc.platform_type == 'mt4'
            $scope.selectAccount(acc)
            return
        $scope.selectAccount('')

    if value == 'pro' &&  (!$scope.account? || $scope.account.platform_type != "cfh")
      if $scope.accounts.length > 0
        for acc in $scope.accounts
          if acc.platform_type == 'cfh'
            $scope.selectAccount(acc)
            return
        $scope.selectAccount('')

    if value == 'invest' && (!$scope.account? || $scope.account.platform_type != "strategy_store")
      if $scope.accounts.length > 0
        for acc in $scope.accounts
          if acc.platform_type == 'strategy_store'
            $scope.selectAccount(acc)
            return
        $scope.selectAccount('')
