var SEXY_COLORS = ["#db08bf", "#e88576", "#ac63ce", "#c95c52", "#fcf76f", "#c6dfff", "#7c7bd1", "#6cdda9", "#88c9ef", "#5fe296", "#043870", "#62bdea", "#f7450e", "#ea596a", "#cc22aa", "#97fcf4", "#dab8fc", "#58cc1a", "#e8929f", "#bc3663", "#65db48", "#f1ff8c", "#43e8da", "#3bff2d", "#8ca7f2", "#d2f78f", "#46c9ea", "#2a9edd", "#ed0480", "#9cc0ed", "#f2bb8c", "#43d2ef", "#060160", "#7bce4e", "#f298d2", "#cb9ff9", "#fc4a32", "#b2ffb6", "#c997ed", "#f7d4af", "#dbbc0d", "#5dc136", "#93f2f2", "#f4e1b5", "#f7b9c4", "#1fb726", "#5f00ad", "#c66331", "#466bc9", "#cc5639", "#ea8ae7", "#352993", "#0da827", "#29bc69", "#9465c6", "#e5b27b", "#bad9f2", "#b5ed8e", "#0cd373", "#67dee0", "#6027bc", "#75b1f9", "#a60fc4", "#49a9b2", "#56acb7", "#6be0cc", "#a9c5f9", "#e527af", "#3bdd64", "#f4b49c", "#6ff265", "#cc1a3b", "#aaff91", "#f9b98e", "#ff8c90", "#f2d09d", "#57d1b4", "#09677c", "#e375e5", "#f473e1", "#f4cd84", "#b4f95e", "#f2f925", "#1d2caf", "#c42cf7", "#a9f9c3", "#f7e6b7", "#80c7d6", "#bc4012", "#7e86f7", "#baf444", "#e2bc7a", "#e0ce2c", "#f9139a", "#ff9efb", "#c40139", "#5b6cc1", "#566cb7", "#ea927c", "#91ef7c"];

app.controller('Calls', function($scope, $http, $timeout) {
    var graph_data = null;
    var setupParams = function(params) {
        $scope.params = params || {};
        $scope.params.datestate = 'none';
        $scope.params.status = 'all';

        $scope.params.per_page = 15;
        $scope.params.direction = true;
        $scope.params.sort = 'call_date';
        $scope.params.page = 1;
    };

    $scope.reload = function() {
        $scope.all_selected = false;
        $scope.is_loading = true;
        $http.get(URL_CALLS_AJAX, {
            params: $scope.params
        }).success(function(data) {
            graph_data = data.graph_data;
            updateChartData();

            $scope.stats = data.stats;
            $scope.objects = data.data;
            $scope.num_pages = data.num_pages;
            $scope.total = data.total;

            $scope.datenumbers = data.datenumbers;

            $scope.params.datestate = data.datestate;
            $scope.params.year = data.year;
            $scope.params.month = data.month;
            $scope.params.day = data.day;

            $scope.is_loading = false;
            $scope.params.page = data.page;
        });
    };


    /* GRID METHODS */
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

    $scope.play = function(url) {
        $scope.current_audio = url;
        $timeout(function(){
            console.log(angular.element('.player audio')[0].play());
        });
    };

    $scope.chooseDate = function(num) {
        if($scope.params.datestate === 'none') {
            $scope.params.year = num;
            $scope.params.month = 1;
            $scope.params.day = 1;
            $scope.params.datestate = 'year';
        } else if($scope.params.datestate === 'year') {
            $scope.params.month = num;
            $scope.params.day = 1;
            $scope.params.datestate = 'month';
        } else if($scope.params.datestate === 'month') {
            $scope.params.day = num;
            $scope.params.datestate = 'day';
        }
        $scope.params.page = 1;
        $scope.reload();
    };

    $scope.clearDate = function() {
        $scope.params.year = 1;
        $scope.params.month = 1;
        $scope.params.day = 1;
        $scope.params.datestate = 'none';
        $scope.params.page = 1;
        $scope.reload();
    };

    /* START */
    setupParams();
    $scope.reload();

    /* Damn charts */
    $scope.countChartConfig = {
        options: {
            legend: {
                align: 'left',
                layout: 'vertical',
                verticalAlign: 'top'
            },
            plotOptions: {
                series: {
                    marker: {
                        symbol: 'circle'
                    }
                }
            },
            chart: {
                type: 'spline'
            }
        },
        title: {
            text: 'Число звонков'
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: 'Дата'
            }
        },
        yAxis: {
            title: {
                text: 'Число'
            },
            min: 0
        },
        loading: false
    };
    $scope.durationChartConfig = {
        options: {
            legend: {
                align: 'left',
                layout: 'vertical',
                verticalAlign: 'top'
            },
            plotOptions: {
                series: {
                    marker: {
                        symbol: 'circle'
                    }
                }
            },
            chart: {
                type: 'spline'
            }
        },
        title: {
            text: 'Длительность звонков'
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: 'Дата'
            }
        },
        yAxis: {
            title: {
                text: 'Секунды'
            },
            min: 0
        },
        loading: false
    };
    var updateChartData = function() {
        $scope.countChartConfig.series = [];
        $scope.durationChartConfig.series = [];
        var index = 0;
        _.each(graph_data, function(stats, name) {
            var count_data = [];
            var duration_data = [];
            stats.forEach(function(stats_data) {
                count_data.push([Date.parse(stats_data[0]), stats_data[1].count]);
                duration_data.push([Date.parse(stats_data[0]), stats_data[1].duration]);
            });
            $scope.countChartConfig.series.push({
                name: name,
                data: count_data,
                color: SEXY_COLORS[index]
            });
            $scope.durationChartConfig.series.push({
                name: name,
                data: duration_data,
                color: SEXY_COLORS[index],
                dashStyle: 'shortdash'
            });

            index++;
        });
    };
});
