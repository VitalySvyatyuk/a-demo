app.service "OTPService", ($rootScope, $http, $modal, $q) ->
  self = @

  @post = (url, data) ->
    $q (resolve, reject) ->
      $http.post url, data
      .then resolve
      .catch (res) ->
        if res.status isnt 511
          reject res
        else
          self.process res.data.detail, (OTPData) ->
            if data
              newObject = angular.extend angular.copy(data), OTPData
            else
              newObject = OTPData
            $http.post url, newObject
          .then resolve, reject

  @processPOST = (OTPData, url, data) ->
    @process OTPData, (OTPData) ->
      if data
        newObject = angular.extend angular.copy(data), OTPData
      else
        newObject = OTPData
      $http.post url, newObject

  @processResource = (OTPData, object, method) ->
    @process OTPData, (OTPData) ->
      newObject = angular.extend angular.copy(object), OTPData
      method.call(newObject)

  @process = (OTPData, sendDataFunc) ->
    if OTPData is 'otp_required'
      OTPRequiredModal.open $modal
    else if Android? and Android.getOTPCode
      if Android.getOTPCode(OTPData.otp_type)
        OTPData.otp_token = Android.getOTPCode(OTPData.otp_type)
        sendDataFunc OTPData
      else
        result = $q.defer()
        window.OTPData = OTPData
        window.OTPResult = (otp_code) ->
          if otp_code == "voice"
            sendDataFunc
              otp_type: 'voice'
            .catch (res) ->
              window.OTPData = res.data.detail
              Android.getOTPCode(window.OTPData.otp_type)
          else
            window.OTPData.otp_token = otp_code
            sendDataFunc window.OTPData
            .then (res) ->
              result.resolve res
        result.promise
    else
      OTPModal.open $modal, OTPData, sendDataFunc


  @smsFormData = ->
    $q (resolve, reject) ->
      $http.get "/api/security/otp/sms_data"
      .success resolve
      .catch reject
  @


