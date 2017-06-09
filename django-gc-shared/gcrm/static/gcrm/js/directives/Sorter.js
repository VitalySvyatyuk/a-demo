/**
 * Created by pgubin on 14.12.15.
 */
angular.module('GCRM').directive('sorter', function() {
  return {
    restrict: 'A',
    scope: {
      objects: '=',
      field: '@sorter',
    },
    transclude: true,
    template: `
      <ng-transclude></ng-transclude>
      <i class="fa" ng-class="objects.sortField!=field ? 'fa-sort':
        (objects.sortReversed ? 'fa-sort-asc' : 'fa-sort-desc' )"></i>
      `,
    controller: function ($scope, $element) {
      $element.on('click', () => {
        $scope.$apply($scope.objects.orderBy.bind($scope.objects, $scope.field))
      })
    }
  }
})
