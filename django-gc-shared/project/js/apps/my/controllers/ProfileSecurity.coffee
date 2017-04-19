app.controller "ProfileSecurityController", ($scope, $http, $modal, $q) ->
  $scope.changePassword = () ->
    $scope.setGlobalLoading true
    delete $scope.errors
    $scope.user.changePassword $scope.oldPassword, $scope.newPassword
    .finally -> $scope.setGlobalLoading false
    .then (data) ->
      $scope.oldPassword = $scope.confirmNewPassword = $scope.newPassword = null
    .catch (res) ->
      $scope.errors = res.data

  $scope.changeDevice = ->
    $scope.setGlobalLoading true
    ChangeDeviceSMSModal.open $modal, $q.defer()
    .finally -> $scope.setGlobalLoading false
    .then -> $scope.reloadUser()
