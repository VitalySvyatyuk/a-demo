app.controller "WebinarsController", ($scope, registrations) ->
  $scope.registrations = registrations
  $scope.registrations.perPageChoices = [10, 20, 50]
  $scope.$watch 'registrations.isLoading', $scope.setGlobalLoading
