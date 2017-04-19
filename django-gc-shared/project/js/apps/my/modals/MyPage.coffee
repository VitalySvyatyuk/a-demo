class @FinanceSummaryModal
  @ctrl: ngInject ($scope, $modalInstance, depositRequests, withdrawRequests) ->
    $scope.setGlobalLoading false
    $scope.isLoading = false
    $scope.depositRequests = depositRequests
    $scope.withdrawRequests = withdrawRequests
    $scope.requests = depositRequests.concat withdrawRequests

    $scope.recoverPassword = ->
      $scope.isLoading = true
      $scope.account.recoverPassword()
      .finally (res) ->
        $scope.isLoading = false
      .then (res) ->
        $modalInstance.close()

    $scope.cancel = ->
      $modalInstance.dismiss()

  @open: ($modal, OTPData, sendDataFunc) ->
    $modal.open
      templateUrl: "/templates/my/account_finance_summary_modal.html"
      controller: @ctrl
      windowClass: "finance-modal"
      resolve:
        depositRequests: ngInject (DepositRequest) -> DepositRequest.query().$promise
        withdrawRequests: ngInject (WithdrawRequest) -> WithdrawRequest.query().$promise
    .result  # return promise


class @ImageViewModal
  @ctrl: ngInject ($scope, $modalInstance, url) ->
    $scope.setGlobalLoading false
    $scope.url = url
    $scope.cancel = ->
      $modalInstance.dismiss()

  @open: ($modal, url) ->
    $modal.open
      templateUrl: "/templates/my/image_view_modal.html"
      controller: @ctrl
      windowClass: "img-modal"
      resolve:
        url: -> url
    .result


class @FriendInvitationModal
  @ctrl: ngInject ($scope, $modalInstance, Recommendation, formData) ->
    $scope.formData = formData

    $scope.form =
      ib_account: if formData.ib_account? and formData.ib_account.choices.length then formData.ib_account.choices[0].value else null
      email: null
      name: null

    $scope.spotIt = ->
      $modalInstance.spotted = true

    $scope.cancel = ->
      $modalInstance.dismiss()

    $scope.ok = ->
      $scope.isLoading = true
      Recommendation.makeRecommendation $scope.form
      .finally (res) ->
        $scope.isLoading = false
      .then (res) ->
        $modalInstance.close(res.data)
      .catch (res) ->
        $scope.errors = res.data
  
  @resolve:
    formData: ngInject (Recommendation) -> Recommendation.makeRecommendationFormData()

  @open: ($modal) ->
    $modal.open     
      templateUrl: "/templates/my/friend_invitation_modal.html"
      windowClass: "gc-small"
      controller: @ctrl
      resolve: @resolve


class @FriendInvitationSideModal extends @FriendInvitationModal
  @open: ($modal) ->
    $modal.open
      templateUrl: "/templates/my/friend_invitation_side_modal.html"
      windowClass: "gc-side-modal"
      backdrop: false
      controller: @ctrl
      resolve: @resolve