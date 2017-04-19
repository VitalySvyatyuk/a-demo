app.controller "ProfileSecurityController", ($scope, $http, $modal, $q) ->
  $scope.changeDevice = ->
    ChangeDeviceSMSModal.open $modal, $q.defer()
    .then -> location.reload()
