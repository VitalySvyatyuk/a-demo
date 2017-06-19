app.controller "ReportsController", ($scope, Report, reports, $modal) ->
    $scope.reports = reports.results
    $scope.page = 1
    $scope.loading = false
    $scope.noMore = false
    $scope.loadItems = ->
        if $scope.loading
            return
        $scope.loading = true
        $scope.page++
        Report.get {page: $scope.page}, (res) ->
            $scope.loading = false
            $scope.reports.push res.results...
        , -> $scope.noMore = true

    $scope.orderReport = ->
        $scope.setGlobalLoading true

        modal = OrderReportModal.open $modal

        modal.opened.finally -> $scope.setGlobalLoading false
        modal.result.then (res) -> $scope.reports.push(res)