app.controller "AccountsInvestmentsController", ($scope, $modal, $q, PAMMManagedConstant, PAMMManaged, PAMMManagedChangeReplicationRatioModal) ->
  $scope.cancelManaged = (managed) ->
    investor = new PAMMManaged managed
    investor.cancel().then (res) ->
      $scope.account.pamm_investor.bindings = _(
        $scope.account.pamm_investor.bindings
      ).without managed
    .catch (res) ->
      alert res.data.detail if res.data.detail

  $scope.quitManaged = (managed) ->
    $scope.setGlobalLoading true

    PAMMManagedQuitModal.open $modal, $scope.account, managed
    .finally -> $scope.setGlobalLoading false
    .then (res) ->
      $scope.account.pamm_investor.bindings = _($scope.account.pamm_investor.bindings).without managed
    .catch (res) ->
      alert res.data.detail if res and res.data and res.data.detail

  $scope.applyMaxLoss = (managed) ->
    $q (resolve, reject) ->
      managedObj = new PAMMManaged _.pick(managed, 'id', 'minimal_equity')
      success = (res) ->
        managed.minimal_equity = managedObj.minimal_equity
        resolve()
      failure = (res) ->
        if res and res.data
          reject res.data.minimal_equity[0] if res.data.minimal_equity and res.data.minimal_equity.length > 0
          reject res.data.detail if res.data.detail

      $scope.setGlobalLoading true
      managedObj.$patch()
      .finally -> $scope.setGlobalLoading false
      .then success
      .catch (res) ->
        if res.status is 511
          OTPService.processResource res.data.detail, managed, managed.$patch
          .then success, failure
        else
          failure res

  $scope.changeReplicationRatio = (managed) ->
    PAMMManagedChangeReplicationRatioModal new PAMMManaged managed
    .result.then (newRatio) ->
      managed.replication_ratio = newRatio

  $scope.selectAccount = (acc) ->
    $scope.$parent.selectAccount acc
    if $scope.account
      ids = _($scope.account.pamm_investor.bindings).chain().pluck('master').pluck('mt4_id').compact().value()
      $scope.loadMt4Data ids


  filter = ->
    $scope.accounts = _.filter $scope.$parent.accounts, (acc) -> acc.is_pamm_investor
  filter()
  angular.extend $scope, PAMMManagedConstant

  $scope.$watch 'selectedCategory', (value) ->
    if value == 'investments'
      filter()
      $scope.selectAccount(if $scope.accounts.length > 0 then $scope.accounts[0] else null)
