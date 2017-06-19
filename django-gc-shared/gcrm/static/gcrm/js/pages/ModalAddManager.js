import {Manager} from '../models/Manager'

angular.module('GCRM').controller('AddManagerCtrl', ($scope, $uibModalInstance) => {

  $scope.searchByEmail = (value) => {
    $scope.searchString = value
    $scope.selectedManager = undefined
    Manager.findManagers(value).then((data) => {
      $scope.managers = data
    })
  }

  $scope.setAsManager = () => {
    Manager.setAsManager($scope.selectedManager.id, $scope.selectedOffice.id).then(() => {
      $uibModalInstance.close('ok')
    })
  }

  $scope.cancel = () => {
    $uibModalInstance.dismiss('cancel');
  };

  $scope.select = (id) => {
    $scope.selectedManager = id
  };

  let processData = (objects) => {
    let offices = {}
    for(let obj of objects)
      if (obj.data.is_managable)
        offices[obj.data.office.id] = obj.data.office
    $scope.offices = _.values(offices)
    if ($scope.offices.length)
      $scope.selectedOffice = $scope.offices[$scope.offices.length-1]
  }

  $scope.managers = {}
  $scope.selectedManager = undefined
  $scope.searchString = undefined

  processData($scope.Users.objects.items)
});