app.controller "AccountsLammInvestmentsController", ($scope, LAMMInvestor, $modal, $q, LAMMManagedConstant, $route) ->
  $scope.selectAccount = (acc) ->
    $scope.$parent.selectAccount acc
    if $scope.account and $scope.account.lamm_investor
      ids = _($scope.account.lamm_investor.bindings).chain().pluck('master').pluck('Investor').compact().value()
      $scope.loadMt4Data ids

  $scope.refresh_page = () ->
    $route.reload();

  $scope.quitManaged = (acc, managed) ->
    investor = new LAMMInvestor managed
    investor.unbind()
    .then (res) ->
      angular.extend managed, res.data.object
    .catch (res) ->
      alert res.data.detail if res.data.detail


  $scope.cancelManaged = (acc, managed) ->
    investor = new LAMMInvestor managed
    investor.reject().then (res) ->
      acc.lamm_investments = _(acc.lamm_investments).without managed
    .catch (res) ->
      alert res.data.detail if res.data.detail


  filter = ->
    $scope.account = _.find $scope.$parent.accounts, (acc) -> acc.is_lamm_investor
  filter()
  angular.extend $scope, LAMMManagedConstant

#  $scope.$watch 'selectedCategory', (value) ->
#    if value == 'investments'
#      filter()
#      $scope.selectAccount(if $scope.accounts.length > 0 then $scope.accounts[0] else null)
