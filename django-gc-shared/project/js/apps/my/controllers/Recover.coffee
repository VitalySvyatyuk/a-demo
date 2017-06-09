app.controller "RecoverController", ($scope, OTPService) ->
  $scope.sendPassword = ->
    OTPService.post "/api/user/recover_password",
      'phone': $scope.phone
    #.finally -> #pass
    .then (result) ->
      data = result.data
      if data.redirect
        window.location.href = data.redirect
      #successCallback END
    .catch (reason) ->
      data = reason.data
      alert 'Произошла ошибка, попробуйте позже. Если ошибка повторится снова, обратитесь в службу поддержки.'