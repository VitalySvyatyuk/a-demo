app.factory "Banner", ($resource, $http, $q) ->
  Resource = $resource "/api/referral/banner/:id",
    id: "@id"

  Resource.getLanguages = (status, ids) ->
    $q (resolve, reject) ->
      $http.get "/api/referral/banner/languages"
      .success resolve
      .catch reject

  Resource