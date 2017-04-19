app.controller('ViewLogs', function($scope, $routeParams, $http, $location) {
   var setupParams = function(params) {
        $scope.params = params || {};
        $scope.params.page = 1;
    };

    $scope.reload = function() {
        $scope.is_loading = true;
        $http.get(URL_VIEWLOGS_AJAX, {
            params: $scope.params
        }).success(function(data) {
            $scope.objects = data.data;
            $scope.num_pages = data.num_pages;
            $scope.total = data.total;

            $scope.is_loading = false;
            $scope.params.page = data.page;
        });
    };

    $scope.pagesRange = function() {
        var result = [];
        [-3, -2, -1, 0, 1, 2, 3].forEach(function(i){
            var num = i + $scope.params.page;
            if((num > 0) && (num <= $scope.num_pages))
                result.push(i + $scope.params.page);
        });
        return result;
    };
    $scope.goto = function(page) {
        if($scope.params.page != page) {
            $scope.params.page = page;
            $scope.reload();
        }
    };
    $scope.gotoNext = function() {
        $scope.goto(_.min([$scope.num_pages, $scope.params.page + 1]));
    };
    $scope.gotoPrev = function() {
        $scope.goto(_.max([1, $scope.params.page - 1]));
    };

    /* START */
    setupParams();
    $scope.reload();
})

;
