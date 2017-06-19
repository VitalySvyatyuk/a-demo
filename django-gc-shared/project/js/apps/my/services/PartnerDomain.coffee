app.factory "PartnerDomain", ($resource, $http, $q) ->
  $resource "/api/referral/partner_domain/:id",
    id: "@id"