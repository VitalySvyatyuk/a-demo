app.controller "AccountsPartnershipController", ($scope, $q, ChangeRebateModal) ->
  loadAgents = (acc) ->
    $scope.agents = $scope.demoAgents = null
    $scope.setGlobalLoading true
    $scope.isAgentsLoading = true
    $q.all [acc.getAgents(), acc.getAgents(true)]
    .finally ->
      $scope.setGlobalLoading false
      $scope.isAgentsLoading = false
    .then (data) ->
      return unless $scope.account is acc
      [$scope.agents, $scope.demoAgents] = data

  $scope.selectAccount = (acc) ->
    $scope.$parent.selectAccount acc
    loadAgents $scope.account if $scope.account

  $scope.accountActions.changeRebate = ->
    if $scope.mt4Data[$scope.account.mt4_id]
      ChangeRebateModal $scope.account, $scope.mt4Data[$scope.account.mt4_id].rebate
      .result.then (newRebate) ->
        $scope.mt4Data[$scope.account.mt4_id].rebate = newRebate

  $scope.isAgentsLoading = false
