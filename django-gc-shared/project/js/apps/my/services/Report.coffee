app.factory "Report", ($resource, $http, $q, getFormData) ->
  Resource = $resource "/api/reports/:id",
    id: "@id"

  Resource.orderReport = (reportData) ->
    self = @
    $q (resolve, reject) ->
      $http.post "/api/reports/order_report", reportData
      .then resolve
      .catch (res) ->
        reject res
  Resource.orderReportFormData = ->
    getFormData "/api/reports/order_report"

  Resource.getCurrentResult = ->
    $q (resolve, reject) ->
      $http.get "/api/reports/get_current_result"
      .success resolve
      .catch reject

  Resource