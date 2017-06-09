app.factory "WebinarRegistration", ($resource, $http, $q) ->
  Resource = $resource "/api/webinar_registration/:id",
    id: "@id"
   ,
    query:
      isArray: false

  Resource
