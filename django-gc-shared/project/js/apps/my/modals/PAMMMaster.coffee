app.factory "PAMMMasterCommissionModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/pamm_master_comission_modal.html"
    windowClass: "gc-small"
  resolve: (account) ->
    account: -> account
    profitAccounts: ngInject (Mt4Account) -> Mt4Account.query(group: ["realmicro", "realstandard", "real_options_us"]).$promise
    formData: ngInject (PAMMMaster) -> PAMMMaster.formData()
  ctrl: ngInject ($scope, $modalInstance, profitAccounts, PAMMMaster, OTPService, account, formData) ->
    $scope.isLoading = false

    fields = ['id', 'profit_account', 'payout_system', 'fee_rate', 'interval_length']
    $scope.master = new PAMMMaster _.pick(account.pamm_master, fields)

    $scope.profitAccountChoices = profitAccounts
    $scope.account = account
    $scope.formData = formData

    $scope.save = ->
      success = ->
        angular.extend account.pamm_master, _.pick($scope.master, fields)
        $modalInstance.close()

      $scope.isLoading = true
      $scope.master.$patch()
      .finally -> $scope.isLoading = false
      .then success
      .catch (res) ->
        if res.status is 511
          OTPService.processResource res.data.detail, $scope.master, $scope.master.$patch
          .then success
        else
          $scope.errors = res.data

    $scope.cancel = ->
      $modalInstance.dismiss()


app.factory "PAMMMasterCreateModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/pamm_master_create_modal.html"
    windowClass: "gc-small"
  resolve: (account) ->
    account: -> account
    profitAccounts: ngInject (Mt4Account) -> Mt4Account.query(group: ["realmicro", "realstandard", "real_options_us"]).$promise
    formData: ngInject (PAMMMaster) -> PAMMMaster.formData()
  ctrl: ngInject ($scope, $modalInstance, profitAccounts, PAMMMaster, account, formData) ->
    $scope.isLoading = false

    $scope.account = account

    $scope.formData = formData
    $scope.profitAccountChoices = profitAccounts

    $scope.master = new PAMMMaster
      account: account.id
      profit_account: account.id
      payout_system: formData.payout_system.choices[0].value

    $scope.save = ->
      success = ->
        account.refresh()
        .finally $modalInstance.close

      $scope.isLoading = true
      $scope.master.$save()
      .then success
      .catch (res) ->
        $scope.isLoading = false
        $scope.errors = res.data

    $scope.cancel = ->
      $modalInstance.dismiss()