angular.module('GCRM').controller('ContactsReassignCtrl', ($scope, $uibModalInstance, objects, canSetAgentCodes) => {
  $scope.cancel = () => {
    $uibModalInstance.dismiss('cancel');
  };

  $scope.only_managable = (manager) => {
    return manager.data.is_managable
  }

  $scope.batchReassign = (comment, withtask, taskcomment, setagentcode, agentcode) => {
    $scope.objects.batchReassign($scope.new_manager, comment, withtask, taskcomment, setagentcode, agentcode).then((data) => {
      $uibModalInstance.close(data)
    }, (res) =>{
      $scope.errors = res.data
      if ($scope.errors.detail)
        alert($scope.errors.detail)
    })
  }

  $scope.objects = objects
  $scope.new_manager = $scope.Users.me.data.id

  $scope.canSetAgentCodes = canSetAgentCodes
});
 
