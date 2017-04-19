app.controller('Frame', function($scope, $routeParams, $http, $location) {
    var PAGES = {
        amo: 'https://grandcapital.amocrm.ru/private/',
        gc: 'https://grandcapital.ru/'
    };
    $scope.page = PAGES[$routeParams.page];
})

;
