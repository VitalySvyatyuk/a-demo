app.factory "UserDocument", ($resource, $http, $q) ->
  Resource = $resource "/api/user_document/:id",
    id: "@id"
  ,
    options:
      method: "OPTIONS"

  Resource.getFields = ->
    $q (resolve, reject) ->
      $http.get "/api/user_document/get_fields"
      .success resolve
      .catch reject

  Resource
