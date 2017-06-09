import moment from 'moment-timezone'
import {ReassignRequest} from '../models/ReassignRequest'

angular.module('GCRM').controller('ReassignsPage', ($scope, objects) => {
  $scope.objects = objects
  $scope.RESULTS = ReassignRequest.RESULTS

  $scope.accept = (item) => {
    if (confirm('Разрешить')) {
      item.accept().then((objects) => {
        $scope.filter()
      })
    }
  }
  $scope.reject = (item) => {
    let comment = prompt('Запретить. Комментарий:', 'Запрещено')
    if (comment) {
      item.reject(comment).then((objects) => {
        $scope.filter()
      })
    }
  }

  $scope.filter = () => $scope.objects.inlineFilter($scope.filters)
  $scope.filters = $scope.objects.inlineFilterParams
})