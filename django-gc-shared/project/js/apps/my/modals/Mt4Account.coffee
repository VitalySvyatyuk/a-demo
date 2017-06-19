app.factory "RecoverPasswordModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/account_recover_password_modal.html"
    windowClass: "gc-small"
  resolve: (acc) ->
    account: -> acc
  ctrl: ngInject ($scope, $modalInstance, account) ->
    $scope.isLoading = false
    $scope.account = account

    $scope.recoverPassword = ->
      $scope.isLoading = true
      $scope.account.recoverPassword()
      .finally (res) ->
        $scope.isLoading = false
      .then (res) ->
        $modalInstance.close()

    $scope.cancel = ->
      $modalInstance.dismiss()


app.factory "ChangeLeverageModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/account_change_leverage_modal.html"
    windowClass: "gc-small"
  resolve: (acc, currentLeverage) ->
    account: -> acc
    formData: -> acc.changeLeverageFormData()
    currentLeverage: -> currentLeverage
  ctrl: ngInject ($scope, $modalInstance, account, formData, currentLeverage) ->
    $scope.isLoading = false
    $scope.account = account
    $scope.formData = formData
    $scope.form = leverage: currentLeverage

    $scope.changeLeverage = ->
      $scope.isLoading = true
      $scope.account.changeLeverage $scope.form.leverage
      .finally (res) ->
        $scope.isLoading = false
      .then (res) ->
        $modalInstance.close $scope.form.leverage
      .catch (res) ->
        $scope.errors = res.data

    $scope.cancel = ->
      $modalInstance.dismiss()


app.factory "ChangeOptionsStyleModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/account_change_options_style_modal.html"
    windowClass: "gc-small"
  resolve: (acc) ->
    account: -> acc
    formData: -> acc.changeOptionsStyleFormData()
  ctrl: ngInject ($scope, $modalInstance, account, formData) ->
    $scope.isLoading = false
    $scope.account = account
    $scope.formData = formData
    $scope.form = options_style: account.options_style

    $scope.changeStyle = ->
      $scope.isLoading = true
      $scope.account.changeOptionsStyle $scope.form.options_style
      .finally (res) ->
        $scope.isLoading = false
      .then (res) ->
        $modalInstance.close()
      .catch (res) ->
        $scope.errors = res.data

    $scope.cancel = ->
      $modalInstance.dismiss()

class @AccountHistoryModal
  @ctrl: ngInject ($scope, $modalInstance, account) ->
    $scope.isLoading = false
    $scope.account = account
    $scope.cancel = ->
      $modalInstance.dismiss()

  @open = ($modal, acc) ->
    $modal.open
      templateUrl: "/templates/my/account_history_modal.html"
      controller: @ctrl
      windowClass: "history-modal"
      resolve:
        account: -> acc
        # history: -> account.getHistory()
    .result


app.factory "ChangeRebateModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/account_change_rebate_modal.html"
    windowClass: "gc-small"
  resolve: (acc, currentRebate) ->
    account: -> acc
    currentRebate: -> currentRebate
    formData: -> acc.changeRebateFormData()
  ctrl: ngInject ($scope, $modalInstance, account, formData, currentRebate) ->
    $scope.isLoading = false
    $scope.account = account
    $scope.formData = formData
    $scope.form = value: currentRebate

    $scope.changeLeverage = ->
      $scope.isLoading = true
      $scope.account.changeRebate $scope.form.value
      .finally (res) ->
        $scope.isLoading = false
      .then (res) ->
        $modalInstance.close $scope.form.value
      .catch (res) ->
        $scope.errors = res.data

    $scope.cancel = ->
      $modalInstance.dismiss()


app.factory "DemoDepositModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/account_demo_deposit_modal.html"
    windowClass: "gc-small"
  resolve: (acc) ->
    account: -> acc
    formData: -> acc.demoDepositFormData()
  ctrl: ngInject ($scope, $modalInstance, formData, account) ->
    $scope.isLoading = false
    $scope.account = account
    $scope.formData = formData
    $scope.form = amount: 1000

    $scope.ok = ->
      $scope.isLoading = true
      $scope.account.demoDeposit $scope.form.amount
      .finally (res) ->
        $scope.isLoading = false
      .then (res) ->
        $modalInstance.close $scope.form.amount
      .catch (res) ->
        $scope.errors = res.data

    $scope.cancel = ->
      $modalInstance.dismiss()


app.factory "AccountBlockedInfoModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/account_blocked_info_modal.html"
    windowClass: "gc-small"
  resolve: (account) ->
    account: -> account
    get_chargeback_info: ngInject ($http) ->
      $http.get "/api/payments/get_chargeback_info"
  ctrl: ngInject ($scope, $modalInstance, account, $http, get_chargeback_info) ->
    $scope.isLoading = false
    $scope.acc = account
    $scope.info = get_chargeback_info

    $scope.createChargebackIssue = ->
      $scope.isLoading = true
      $http.post "/api/payments/user_requesting_chargeback_issue"
      .finally (res) ->
        $scope.isLoading = false
      .then (res) ->
        $scope.info.data.check_chargeback = true

    $scope.cancel = ->
      $modalInstance.dismiss()