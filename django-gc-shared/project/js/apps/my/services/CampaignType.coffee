app.factory "CampaignType", ($resource) ->
  $resource "/api/massmail/type/:id",
    id: "@id"
