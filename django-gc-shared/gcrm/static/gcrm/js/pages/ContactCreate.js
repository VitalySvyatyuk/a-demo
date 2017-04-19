angular.module('GCRM').controller('ContactCreatePage', function ($scope, $state, object) {
  $scope.object = object
  $scope.object.data.info = [{ type: "email" }, { type: "phone" }]

  $scope.check = function() {
    if (!$scope.object.data.info[0].value && !$scope.object.data.info[1].value)
      return true
  }

  $scope.save = function(continueThen) {
    $scope.object.saveChanges().then(function(newContact) {
      if (continueThen) {
        $state.go('contact.feed', { id: newContact.data.id })
      } else {
        $scope.objects.reload()
        $state.go('contacts')
      }
    })
  }
})
