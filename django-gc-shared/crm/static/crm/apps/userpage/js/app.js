var app = angular.module('CRMUserpage', [])

.run(function($http) {
    $http.defaults.headers.post['X-CSRFToken'] = csrftoken;
})

.config(function($sceProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
    $sceProvider.enabled(false);  /* Disable it so we can set src for audiorecords */
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
        return moment(date).format('LLLL');
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
