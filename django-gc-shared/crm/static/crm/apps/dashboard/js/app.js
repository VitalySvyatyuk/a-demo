var app = angular.module('CRMDashboard', ['ngRoute', 'highcharts-ng'])

.run(function($http) {
    $http.defaults.headers.post['X-CSRFToken'] = csrftoken;
})

.config(function($routeProvider, $sceProvider) {
    $sceProvider.enabled(false);  /* Disable it so we can set src for audiorecords */
    $routeProvider.
        when('/summary', {
            templateUrl: URL_SUMMARY_TPL,
            controller: 'Summary',
            resolve: {
                data: ['$http', function($http) {
                    return $http.get('/api/crm/info/summary')
                }]
            }
        }).
        when('/summary_total', {
            templateUrl: URL_SUMMARY_TPL,
            controller: 'Summary',
            resolve: {
                data: ['$http', function($http) {
                    return $http.get('/api/crm/info/summary_total')
                }]
            }
        }).
        when('/frame/:page', {
            templateUrl: URL_FRAME_TPL,
            controller: 'Frame'
        }).
        when('/search', {
            templateUrl: URL_SEARCH_TPL,
            controller: 'Search'
        }).
        when('/calls', {
            templateUrl: URL_CALLS_TPL,
            controller: 'Calls'
        }).
        when('/viewlogs', {
            templateUrl: URL_VIEWLOGS_TPL,
            controller: 'ViewLogs'
        }).
        otherwise({
            redirectTo: '/frame/amo'
    });
})

.filter('momentFromNow', function() {
    return function(date) {
        if(!date || date == '-')
            return '-';
        var m = moment(date);
        if(Math.abs(moment().diff(m, 'hours')) > 3)
            return m.format('L LT');
        else
            return m.fromNow();
    };
})

.filter('momentHumanize', function() {
    return function(date) {
        if(!date || date == '-')
            return '-';
        return moment(date).format('LLLL z');
    };
})

.filter('momentDurationHumanize', function() {
    return function(data) {
        if(!data || data == '-')
            return '-';
        return moment.duration(data, 'seconds').humanize();
    };
})

.directive('ngEnter', function () {
    return {
        link: function (scope, elements, attrs) {
            elements.bind('keydown keypress', function (event) {
                if (event.which === 13) {
                    scope.$apply(function () {
                        scope.$eval(attrs.ngEnter);
                    });
                    event.preventDefault();
                }
            });
        }
    };
});

;
