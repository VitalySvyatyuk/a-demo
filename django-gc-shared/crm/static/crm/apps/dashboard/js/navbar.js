app.controller('NavBar', function($scope, $rootScope, $http, $location, $window, $interval) {
    $rootScope.is_superuser = IS_SUPERUSER;

    $scope.getNewClient = function() {
        if ($scope.newClientLoading)
            return
        $scope.newClientLoading = true
        $http.get('/api/crm/customer/get_new').success(function(data) {
            $window.open(data.link, '_blank');
            updateAvailableClients();
            $scope.newClientLoading = false;
        }).catch(function(req) {
            alert(req.data.detail);
            if(req.data.last_customer_link && confirm('Открыть карточку последнего полученного клиента?'))
                $window.open(req.data.last_customer_link, '_blank');
            $scope.newClientLoading = false;
        });
    };

    updateAvailableClients = function() {
        $http.get('/api/crm/customer/new_count').success(function(data) {
            $scope.availableClients = data;
        });
    };

    updateAvailableClients();
    $interval(updateAvailableClients, 10000);
})

;