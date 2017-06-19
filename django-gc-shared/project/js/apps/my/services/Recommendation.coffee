app.factory "Recommendation", ($resource, $http, $q, getFormData) ->
  Resource = $resource "/api/friend_recommend/"

  Resource.makeRecommendation = (reportData) ->
    self = @
    $q (resolve, reject) ->
      $http.post "/api/friend_recommend/new_recommendation", reportData
      .then resolve
      .catch (res) ->
        reject res
  Resource.makeRecommendationFormData = ->
    getFormData "/api/friend_recommend/new_recommendation"

  Resource