import moment from 'moment-timezone'
import {Task} from '../models/Task'

angular.module('GCRM').controller('TasksAllPage', ($scope, objects) => {
  $scope.objects = objects
  $scope.TASK_TYPES = TASK_TYPES
  $scope.TYPES_ICON = Task.TYPES_ICON

  $scope.toggleType = (type) => {
    if ($scope.filters.task_type.indexOf(type) + 1)
      $scope.filters.task_type = _.without($scope.filters.task_type, type)
    else
      $scope.filters.task_type.push(type)
    $scope.filter()
  }

  $scope.filter = () => $scope.objects.inlineFilter($scope.filters)
  $scope.filters = $scope.objects.inlineFilterParams
})
