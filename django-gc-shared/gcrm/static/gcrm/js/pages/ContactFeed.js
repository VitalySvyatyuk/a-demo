angular.module('GCRM').controller('ContactFeedPage', ($scope, objects) => {
  $scope.objects = objects
  $scope.$on('feedRecordAdded', (event, record) => {
    $scope.objects.items.unshift(record)
  });

  $scope.remove = (item) => {
    $scope.objects.items.splice($scope.objects.items.indexOf(item), 1)
  }
})
