angular.module('GCRM').controller('ContactPaymentsPage', ($scope, objects) => {
  $scope.objects = objects.items

  $scope.totals = {
    deposit: _($scope.objects)
      .filter({data: {status: 'done'}})
      .filter({data: {type: 'deposit'}})
      .map((o) => o.data.amount_USD.amount)
      .sum(),
    withdraw: _($scope.objects)
      .filter({data: {status: 'done'}})
      .filter({data: {type: 'withdraw'}})
      .map((o) => o.data.amount_USD.amount)
      .sum()
  }
})
