app.controller "AccountCreateController", ($scope, $routeParams) ->
  $scope.selectedCategory = $routeParams.category or "trading"
  $scope.selectedCategoryList = ['trading',]

