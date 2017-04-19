class @PAMMManagedQuitModal
  @ctrl: ngInject ($scope, $modalInstance, PAMMManaged, managed, account, formData) ->
    $scope.isLoading = false

    $scope.account = account
    $scope.managed = new PAMMManaged managed
    $scope.formData = formData
    $scope.type = formData.type.choices[0].value

    $scope.save = ->
      $scope.isLoading = true
      $scope.managed.quit $scope.type
      .finally -> $scope.isLoading = false
      .then (res) ->
        account.pamm_investor.bindings = _(account.pamm_investor.bindings).without managed
        $modalInstance.close()
      .catch (res) ->
        $scope.errors = res.data

    $scope.cancel = ->
      $modalInstance.dismiss()

  @open: ($modal, account, managed) ->
    $modal.open
      controller: @ctrl
      templateUrl: "/templates/my/pamm_managed_quit_modal.html"
      windowClass: "gc-small"
      resolve:
        account: -> account
        managed: -> managed
        formData: ngInject (PAMMManaged) -> (new PAMMManaged id: managed.id).quitFormData()
    .result


app.factory "PAMMManagedChangeReplicationRatioModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/pamm_managed_change_replication_ratio_modal.html"
    windowClass: "gc-small"
  resolve: (managed) ->
    managed: -> managed
    formData: -> managed.changeReplicationRatioFormData()
  ctrl: ngInject ($scope, $modalInstance, PAMMManaged, managed, formData) ->
    $scope.isLoading = false

    $scope.managed = managed
    $scope.formData = formData

    $scope.changeReplicationRatio = ->
      $scope.isLoading = true
      $scope.managed.changeReplicationRatio $scope.managed.replication_ratio
      .finally (res) ->
        $scope.isLoading = false
      .then (res) ->
        $scope.managed.replication_ratio = res.data.object.replication_ratio
        $modalInstance.close $scope.managed.replication_ratio

        acc_inv_ctrl_scope = angular.element('[ng-controller="AccountsInvestmentsController"]').scope()
        man = _.find acc_inv_ctrl_scope.account.pamm_investor.bindings, (item) -> item.id == managed.id
        man.replication_ratio = $scope.managed.replication_ratio if man

      .catch (res) ->
        $scope.errors = res.data

    $scope.cancel = ->
      $modalInstance.dismiss()
