import {Contact} from '../models/Contact'
import {Manager} from '../models/Manager'

angular.module('GCRM').controller('ContactsPage', ($scope, $uibModal, objects, languages) => {
  $scope.toggleTag = (tag) => {
    if($scope.filters.tags.indexOf(tag)+1)
      $scope.filters.tags = _.without($scope.filters.tags, tag)
    else
      $scope.filters.tags.push(tag)
    $scope.filter()
  }

  $scope.contactsReassign = () => {
    $scope.modalInstance = $uibModal.open({
      animation: true,
      templateUrl: '/gcrm/templates/modal.contactsReassign.html',
      controller: 'ContactsReassignCtrl',
      resolve: {
        objects: () => {
        $scope.objects.collectSelected()
          return $scope.objects
        },
        canSetAgentCodes: () => {
          let manager = new Manager({id: MY_USER_ID})
          return manager.canSetAgentCodes().then((res) => {
            return res.can_set_agent_codes
          })
        }
      }
    }).result.then((res) => {
      $scope.objects.reload()
      alert(res.detail)
    })
  }

  $scope.contactsAgentCode = () => {
    $scope.modalInstance = $uibModal.open({
      animation: true,
      templateUrl: '/gcrm/templates/modal.contactsAgentCode.html',
      controller: 'ContactsAgentCodeCtrl',
      resolve: {
        objects: () => {
          $scope.objects.collectSelected()
          return $scope.objects
        }
      }
    }).result.then((res) => {
      $scope.objects.reload()
      alert(res.detail)
    })
  }

  $scope.filter = () => {
    $scope.objects.inlineFilter($scope.filters)
  }

  $scope.languages = languages
  $scope.objects = objects
  $scope.filters = $scope.objects.inlineFilterParams

  if ($scope.filters &&
    (($scope.filters.countries && $scope.filters.countries.length) ||
    ($scope.filters.regions && $scope.filters.regions.length) ||
    ($scope.filters.languages && $scope.filters.languages.length) )
  )
    $scope.hideAdditionalFilters = false
  else
    $scope.hideAdditionalFilters = true
})
