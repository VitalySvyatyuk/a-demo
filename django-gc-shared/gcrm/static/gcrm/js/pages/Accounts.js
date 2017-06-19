import {Account} from '../models/Account'
import moment from 'moment-timezone'


angular.module('GCRM').controller('AccountsPage', ($scope, objects, types) => {
  $scope.objects = objects
  $scope.types = types

  $scope.filter = () => $scope.objects.inlineFilter($scope.filters)
  $scope.filters = $scope.objects.inlineFilterParams
})