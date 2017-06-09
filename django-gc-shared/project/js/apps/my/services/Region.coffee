app.factory "Region", ($resource) ->
  $resource "/api/geobase/region/:id",
    id: "@id"
