app.factory "Country", ($resource) ->
  $resource "/api/geobase/country/:id",
    id: "@id"
