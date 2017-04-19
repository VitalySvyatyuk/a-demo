app.controller('Search', function($scope, $routeParams, $http, $location) {
   var setupParams = function(params) {
        $scope.params = params || {};

        $scope.params.per_page = 15;
        $scope.params.direction = true;
        $scope.params.sort = 'call_date';
        $scope.params.page = 1;
        $scope.params.method = 'clients';
    };

    $scope.reload = function() {
        $scope.all_selected = false;
        $scope.is_loading = true;
        $http.get(URL_SEARCH_AJAX, {
            params: $scope.params
        }).success(function(data) {
            $scope.objects = data.data;
            $scope.num_pages = data.num_pages;
            $scope.total = data.total;

            $scope.is_loading = false;
            $scope.params.page = data.page;
        });
    };


    var loadUserMoreData = function(user) {
        $scope.is_loading_more = true;
        $http.get(URL_USER_MORE_AJAX, {
            params: {user_id: user.id}
        }).success(function(data) {
            user.more = data;
            $scope.is_loading_more = false;
        });
    };

    /* GRID METHODS */
    $scope.select = function(user) {
        $scope.selected_id = user.id;
        loadUserMoreData(user);
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
