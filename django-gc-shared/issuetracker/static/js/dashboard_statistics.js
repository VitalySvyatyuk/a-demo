Date.prototype.addDays = function(days)
{
    var dat = new Date(this.valueOf());
    dat.setDate(dat.getDate() + days);
    return dat;
};

var app = angular.module('dashboard_statistics', ['ngRoute']);

app.config(function ($interpolateProvider) {
    //allow django templates and angular to co-exist
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

app.controller('QueryController', function ($scope, $filter, $http) {
    $scope.from_date = $filter('date')((new Date().addDays(-7)), "dd.MM.yyyy");
    $scope.to_date = $filter('date')(new Date(), "dd.MM.yyyy");
    $( "#from_datepicker" ).datepicker({dateFormat:'dd.mm.yy', yearRange: "2000:2020"});
    $( "#to_datepicker" ).datepicker({dateFormat:'dd.mm.yy', yearRange: "2000:2020"});

    $scope.selected_mode = 'queries';

    $scope.get_data = function() {
        var from_date = $( "#from_datepicker" ).datepicker( "getDate" );
        var to_date = $( "#to_datepicker" ).datepicker( "getDate" );
        if (from_date > to_date) {
            $scope.occurred_error = "Некорректно указан диапазон дат";
            return;
        }

        from_date = $filter('date')(from_date, "dd.MM.yyyy");
        to_date = $filter('date')(to_date, "dd.MM.yyyy");
        if (!from_date && !to_date) {
            from_date = $scope.from_date;
            to_date = $scope.to_date;
        }

        $http({method: 'GET', url: '/my/issues_admin/statistics/get/', params: {'st_type': $scope.selected_mode, 'from_date': from_date, 'to_date': to_date}}).
        success(function (data, status) {
            $scope.data = data;
        }).
        error(function (data, status) {
            $scope.occurred_error = "Connection error! Cant get clients. Status request: " + status;
        });
    };

    $scope.get_data()
});