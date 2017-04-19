app.controller('Userpage', function($scope, $http, $timeout, Call, VMCall, Log, DepositRequest, WithdrawRequests) {
    Call.query().success(function(data) {
        $scope.calls = data;
    }).error(function(data) {
        $scope.error = data;
    });
    VMCall.query().success(function(data) {
        $scope.vmcalls = data;
    }).error(function(data) {
        $scope.error = data;
    });

    Log.query().success(function(data) {
        $scope.logs = data;
    }).error(function(data) {
        $scope.error = data;
    });

    DepositRequest.query().success(function(data) {
        $scope.depositRequests = data;
    }).error(function(data) {
        $scope.error = data;
    });

    WithdrawRequests.query().success(function(data) {
        $scope.withdrawRequests = data;
    }).error(function(data) {
        $scope.error = data;
    });

    $scope.play = function(url) {
        $scope.current_audio = url;
        $timeout(function(){
            angular.element('.player audio')[0].play();
        });
    };

    $scope.showLogDetails = function(index) {
        if($scope.selectedLog === index)
            $scope.selectedLog = null;
        else
            $scope.selectedLog = index;
    };


    $scope.showDRDetails = function(index) {
        if($scope.selectedDR === index)
            $scope.selectedDR = null;
        else
            $scope.selectedDR = index;
    };

    $scope.showWRDetails = function(index) {
        if($scope.selectedWR === index)
            $scope.selectedWR = null;
        else
            $scope.selectedWR = index;
    };

});
