app.controller "AccountsMasterController", ($scope, PAMMMaster, PAMMMasterManaged, OTPService, $modal, PAMMManagedConstant, PAMMMasterCreateModal, PAMMMasterCommissionModal) ->
  $scope.accountHasPendingManagedAccounts = (acc) ->
    _.findWhere acc.pamm_master.managed_accounts,
      status: PAMMManagedConstant.STATUS_PENDING

  $scope.unbindManaged = (acc, managed) ->
    investor = new PAMMMasterManaged managed
    investor.unbind()
    .then (res) ->
      angular.extend managed, res.data.object
      alert res.data.detail if res.data.detail
    .catch (res) ->
      alert res.data.detail if res.data.detail

  $scope.acceptManaged = (acc, managed) ->
    investor = new PAMMMasterManaged managed
    investor.accept().then (res) ->
      angular.extend managed, res.data.object
      alert res.data.detail if res.data.detail
    .catch (res) ->
      alert res.data.detail if res.data.detail

  $scope.rejectManaged = (acc, managed) ->
    investor = new PAMMMasterManaged managed
    investor.reject().then (res) ->
      acc.pamm_master.managed_accounts = _(acc.pamm_master.managed_accounts).without managed
    .catch (res) ->
      alert res.data.detail if res.data.detail

  $scope.accountActions.changeCommissionType = ->
    PAMMMasterCommissionModal $scope.account

  $scope.accountActions.setAutoAcceptManaged = (bool) ->
    success = -> $scope.account.pamm_master.auto_accept = bool
    master = new PAMMMaster
      id: $scope.account.pamm_master.id
      auto_accept: bool
    $scope.setGlobalLoading true
    master.$patch()
    .finally -> $scope.setGlobalLoading false
    .then success
    .catch (res) ->
      if res.status is 511
        OTPService.processResource res.data.detail, master, master.$patch
        .then success

  $scope.accountActions.becomeMaster = ->
    PAMMMasterCreateModal $scope.account

  $scope.selectAccount = (acc) ->
    $scope.$parent.selectAccount acc
    if $scope.account
      ids = _($scope.account.pamm_master.managed_accounts).pluck 'mt4_id'
      $scope.loadMt4Data _.compact(ids)

  angular.extend $scope, PAMMManagedConstant
  filter = ->
    $scope.accounts = _.filter $scope.$parent.accounts, (acc) -> acc.is_pamm_master
  filter()

  $scope.hasPendingManagedAccounts = _.any $scope.accounts, (acc) ->
    _.any acc.pamm_master.managed_accounts, (man) ->
      man.status is PAMMManagedConstant.STATUS_PENDING

  $scope.$watch 'selectedCategory', (value) ->
    if value == 'master'
      filter()
      $scope.selectAccount(if $scope.accounts.length > 0 then $scope.accounts[0] else null)