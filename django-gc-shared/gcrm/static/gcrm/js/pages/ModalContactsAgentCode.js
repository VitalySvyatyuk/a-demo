angular.module('GCRM').controller('ContactsAgentCodeCtrl', ($scope, $uibModalInstance, objects) => {
  $scope.cancel = () => {
    $uibModalInstance.dismiss('cancel');
  };

  $scope.batchAgentCode = (code) => {
    $scope.objects.batchAgentCode(code).then((data) => {
      $uibModalInstance.close(data)
    }, (res) =>{
      $scope.errors = res.data
      if ($scope.errors.detail)
        alert($scope.errors.detail)
    })
  }

  $scope.objects = objects
});
 
