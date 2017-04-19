app.controller "AccountsLammMasterController", ($scope, LAMMMaster, PAMMMaster, PAMMMasterManaged, OTPService, $modal, LAMMManagedConstant) ->
  $scope.accountHasPendingManagedAccounts = (acc) ->
    if acc.lamm_master
      return _.findWhere acc.lamm_master.lamm_investors.items,
        acc.lamm_master.lamm_investors.items
        InvestStatus: LAMMManagedConstant.STATUS_PENDING
    false

  $scope.unbindManaged = (acc, managed) ->
    investor = new LAMMMaster managed
    investor.unbind()
    .then (res) ->
      angular.extend managed, res.data.object
    .catch (res) ->
      alert res.data.detail if res.data.detail

  $scope.acceptManaged = (acc, managed) ->
    investor = new LAMMMaster managed
    investor.accept().then (res) ->
      angular.extend managed, res.data.object
    .catch (res) ->
      alert res.data.detail if res.data.detail

  $scope.rejectManaged = (acc, managed) ->
    investor = new LAMMMaster managed
    investor.reject().then (res) ->
      acc.lamm_master.lamm_investors.items = _(acc.lamm_master.lamm_investors.items).without managed
    .catch (res) ->
      alert res.data.detail if res.data.detail

  $scope.selectAccount = (acc) ->
    $scope.$parent.selectAccount acc
    if $scope.account and $scope.account.lamm_master
      ids = _($scope.account.lamm_master.lamm_investors.items).pluck 'Manager'
      $scope.loadMt4Data _.compact(ids)

  angular.extend $scope, LAMMManagedConstant
  filter = ->
    $scope.accounts = _.filter $scope.$parent.accounts, (acc) -> acc.is_lamm_master
  filter()

  $scope.hasPendingManagedAccounts = _.any $scope.accounts, (acc) ->
    _.any acc.lamm_master.lamm_investors.items, (man) ->
      man.InvestStatus is LAMMManagedConstant.STATUS_PENDING

  $scope.$watch 'selectedCategory', (value) ->
    if value == 'lammMaster'
      filter()
      $scope.selectAccount(if $scope.accounts.length > 0 then $scope.accounts[0] else null)