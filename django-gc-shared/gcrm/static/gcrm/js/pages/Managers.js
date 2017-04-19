import {Manager} from '../models/Manager'


angular.module('GCRM').controller('ManagersPage', ($scope, $uibModal) => {
  $scope.showChangeName= (id) => {
    $scope.showChangeNameId = id
  }

  $scope.setPass = (item) => {
    let newPass = prompt('')
    if (newPass) {
      item.setPassword(newPass).then((data) => {
        alert(data.detail)
      }).catch((res) => {
        alert(res.data.detail || res.data.value[0])
        $scope.setPass(item)
      })
    }
  }

  $scope.revoke = (item) => {
    if (confirm('')) {
      item.revoke().then((data) => {
        $scope.Users.reload().then(() => {
          $scope.reload()
        })
      }).catch((res) => {
        alert(res.data.detail || res.data.value[0])
      })
    }
  }

  $scope.saveName = (item) => {
    item.errors = undefined
    item.setName(item.data.name.last, item.data.name.first, item.data.name.middle).then(() => {
      item.isEditing = false
    }).catch((res) => {
      item.errors = res.data
    })
  }

  $scope.addManager = () => {
    $scope.modalInstance = $uibModal.open({
      animation: true,
      templateUrl: '/gcrm/templates/modal.addManager.html',
      controller: 'AddManagerCtrl',
    }).result.then(() => {
      $scope.Users.reload().then(() => {
        $scope.reload()
      })
    })
  }

  $scope.objects = $scope.Users.offices
})
