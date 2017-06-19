import {Manager} from '../models/Manager'
import moment from 'moment-timezone'


angular.module('GCRM').controller('AnalyticsPage', ($scope, objects) => {

  $scope.resetFilters = () => {
    $scope.filters = {
      stats_date_0: moment().startOf('day').toDate(),
      stats_date_1: moment().endOf('day').toDate()
     }
   }

  $scope.filter = () => Manager.getStats($scope.filters).then(processData)

  let processData = (objects) => {
    $scope.objects = {}
    for(let obj of objects){
      obj.manager = $scope.Users.mapping[obj.manager]

      if(!$scope.objects[obj.manager.data.office.id])
        $scope.objects[obj.manager.data.office.id] = {summary: {}, objects: []}
      $scope.objects[obj.manager.data.office.id].objects.push(obj)

      $scope.objects[obj.manager.data.office.id].summary = _.mergeWith(
        $scope.objects[obj.manager.data.office.id].summary,
        _.cloneDeep(obj),
        (lval, rval) => isNaN(lval) ? undefined : (lval + rval)
      )
    }
  }

  $scope.orderer = {
    sortReversed: true,
    sortField: 'payments.total',
    orderBy: (field) => {
      if ($scope.orderer.sortField === field)
        $scope.orderer.sortReversed = !$scope.orderer.sortReversed
      $scope.orderer.sortField = field
    }
  }

  $scope.objects = objects

  processData(objects)
  $scope.resetFilters()
})
