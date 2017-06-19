app.controller "AccountsContestsController", ($scope) ->
  filter = ->
    $scope.accounts = _.filter $scope.$parent.accounts, (acc) -> acc.is_contest
  filter()
  $scope.$watch 'selectedCategory', (value) ->
    if value == 'contests'
      filter()
      $scope.selectAccount(if $scope.accounts.length > 0 then $scope.accounts[0] else null)
