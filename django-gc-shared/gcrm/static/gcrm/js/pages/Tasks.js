import moment from 'moment-timezone'
import {Task} from '../models/Task'

angular.module('GCRM').controller('TasksPage', ($scope, overdue, today, tomorrow) => {
  $scope.today = today
  $scope.tomorrow = tomorrow
  $scope.overdue = overdue
})
