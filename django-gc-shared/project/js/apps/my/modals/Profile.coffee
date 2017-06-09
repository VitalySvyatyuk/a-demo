class @ChangeDeviceSMSModal
  @ctrl: ngInject ($scope, $modalInstance, $http, OTPService, deferred, $modal, formData, $rootScope) ->
    OTPInit = ->
      $scope.isLoading = true
      delete $scope.errors
      $http.post '/api/security/otp/bind', $scope.OTPInfo
      .catch (res) ->
        $scope.isLoading = false
        if res.status is 511
          $scope.OTPStep = 'confirm'
          $scope.OTPData = res.data.detail
        else
          $scope.errors = res.data

    $scope.OTPInitSMS = ->
      OTPInit()

    $scope.OTPInitVoice = ->
      $scope.OTPInfo.type = 'voice'
      OTPInit()

    $scope.OTPBind = ->
      $scope.isLoading = true
      $scope.isTokenInvalid = false
      delete $scope.errors

      success = (res) ->
        $scope.isLoading = false
        deferred.resolve()
        $modalInstance.close()
      error = (res) ->
        deferred.reject()
        $modalInstance.dismiss()

      $http.post '/api/security/otp/bind',
        angular.extend angular.copy($scope.OTPData), $scope.OTPInfo
      .then success
      .catch (res) ->
        $scope.isLoading = false
        if res.status is 511
          $scope.OTPInfo.verified = true
          OTPService.processPOST res.data.detail, '/api/security/otp/bind', $scope.OTPInfo
          .then success, error
        else
          $scope.isTokenInvalid = true

    $scope.toTOTP = ->
      ChangeDeviceTOTPModal.open $modal, deferred
      $modalInstance.dismiss()

    $scope.cancel = ->
      deferred.reject()
      $modalInstance.dismiss()

    $scope.formatPhoneCodeLabel = (option) ->
      s = _.ljust option.phone_code, 7
      "+#{s} (#{option.name})".replace ///\ ///g, '&nbsp;'

    $scope.formData = formData
    $scope.OTPStep = 'init'
    $scope.OTPInfo =
      type: 'sms'
      phone_number:
        country: 1
        tail: ''

  @open: ($modal, deferred) ->
    $modal.open
      templateUrl: "/templates/my/profile_security_otp_modal_sms.html"
      controller: @ctrl
      windowClass: "otp-sms-modal"
      resolve:
        deferred: -> deferred
        formData: ngInject (OTPService) -> OTPService.smsFormData()
    .result  # return promise
    deferred.promise


class @ChangeDeviceTOTPModal
  @ctrl: ngInject ($scope, $modalInstance, $http, OTPService, deferred, $modal) ->
    OTPInit = ->
      $scope.isLoading = true
      delete $scope.errors
      $http.post '/api/security/otp/bind', $scope.OTPInfo
      .catch (res) ->
        $scope.isLoading = false
        if res.status is 511
          $scope.OTPStep = 'confirm'
          $scope.OTPData = res.data.detail
          #since we should preserve key from totp device
          # as part of device info, sneak it into OTPInfo
          $scope.OTPInfo.key = $scope.OTPData.key
        else
          $scope.errors = res.data

    $scope.OTPBind = ->
      $scope.isLoading = true
      $scope.isTokenInvalid = false
      delete $scope.errors

      success = (res) ->
        $scope.isLoading = false
        deferred.resolve()
        $modalInstance.close()
      error = (res) ->
        deferred.reject()
        $modalInstance.dismiss()

      $http.post '/api/security/otp/bind',
        angular.extend angular.copy($scope.OTPData), $scope.OTPInfo
      .then success
      .catch (res) ->
        $scope.isLoading = false
        if res.status is 511
          $scope.OTPInfo.verified = true
          OTPService.processPOST res.data.detail, '/api/security/otp/bind', $scope.OTPInfo
          .then success, error
        else
          $scope.isTokenInvalid = true

    $scope.toSMS = ->
      ChangeDeviceSMSModal.open $modal, deferred
      $modalInstance.dismiss()

    $scope.cancel = ->
      deferred.reject()
      $modalInstance.dismiss()

    $scope.OTPStep = 'init'
    $scope.OTPInfo =
      type: 'totp'
    OTPInit()

  @open: ($modal, deferred) ->
    $modal.open
      templateUrl: "/templates/my/profile_security_otp_modal_totp.html"
      controller: @ctrl
      windowClass: "totp-modal"
      resolve:
        deferred: -> deferred
    .result  # return promise
    deferred.promise
