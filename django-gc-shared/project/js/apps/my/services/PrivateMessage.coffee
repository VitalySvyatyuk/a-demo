app.factory "PrivateMessage", ($resource, $http, $q, OTPService, $modal) ->
  Resource = $resource "/api/message/:id/:action",
    id: "@id"
  ,
    query:
      isArray: false

  Resource.batchMark = (status, ids) ->
    $http.post "/api/message/batch_mark",
      id: ids
      status: status

  Resource
