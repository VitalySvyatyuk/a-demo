import {Call} from '../models/Call'
import moment from 'moment-timezone'


angular.module('GCRM').controller('CallsPage', ($scope, objects) => {
  $scope.objects = objects

  $scope.showPlayer = (id) => {
    $scope.currentPlayedId = id
  }

  $scope.filter = () => $scope.objects.inlineFilter($scope.filters)
  $scope.filters = $scope.objects.inlineFilterParams
})