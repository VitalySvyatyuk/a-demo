class @OrderReportModal
  @ctrl: ngInject ($scope, $modalInstance, formData, Report) ->
    $scope.isLoading = false
    $scope.formData = formData
    $scope.form =
      report_type: formData.report_type.choices[0].value
      account: if formData.account.choices? and formData.account.choices.length then formData.account.choices[0].value else null
      start: null
      end: null
      user: null
      account_group_include: null
      account_group_exclude: null

    $scope.orderReport = ->
      $scope.isLoading = true
      Report.orderReport $scope.form
      .finally (res) ->
        $scope.isLoading = false
      .then (res) ->
        $modalInstance.close(res.data)
      .catch (res) ->
        $scope.errors = res.data

    $scope.cancel = ->
      $modalInstance.dismiss()

  @open = ($modal) ->
    $modal.open
      templateUrl: "/templates/my/reports_order_modal.html"
      controller: @ctrl
      windowClass: "gc-small"
      resolve:
        formData: ngInject (Report) -> Report.orderReportFormData()