class @OTPModal
  @ctrl: ngInject ($scope, $modalInstance, OTPData, sendData) ->
    $scope.OTPData = OTPData

    $scope.useVoice = () ->
      $scope.isTokenInvalid = false
      $scope.isLoading = true
      sendData
        otp_type: 'voice'
      .then (res) ->
        $scope.isLoading = false
        $modalInstance.close res
      .catch (res) ->
        $scope.isLoading = false
        $scope.OTPData = res.data.detail

    $scope.ok = (token) ->
      $scope.isTokenInvalid = false
      $scope.isLoading = true
      $scope.OTPData.otp_token = token
      sendData $scope.OTPData
      .finally -> $scope.isLoading = false
      .then (res) ->
        $modalInstance.close res
      .catch (res) ->
        if res.data.detail is 'invalid_otp_token'
          $scope.isTokenInvalid = true
        else
          $modalInstance.dismiss res

    $scope.cancel = ->
      $modalInstance.dismiss()

  @open: ($modal, OTPData, sendDataFunc) ->
    $modal.open
      templateUrl: "/templates/my/otp_confirm_modal.html"
      controller: @ctrl
      windowClass: "otp-confirm-modal"
      resolve:
        OTPData: -> OTPData
        sendData: -> sendDataFunc
    .result  # return promise

class @OTPRequiredModal
  @ctrl: ngInject ($scope, $modalInstance, $location) ->
    $scope.go = ->
      $location.path "profile/security"
      $modalInstance.dismiss()

    $scope.cancel = ->
      $modalInstance.dismiss()

  @open: ($modal, OTPData, sendDataFunc) ->
    $modal.open
      templateUrl: "/templates/my/otp_required_modal.html"
      controller: @ctrl
      windowClass: "otp-confirm-modal"
      resolve:
        OTPData: -> OTPData
        sendData: -> sendDataFunc
    .result  # return promise