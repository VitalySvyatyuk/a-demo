app.factory "Mt4Account", ($resource, $http, $q, OTPService, getFormData) ->
  Resource = $resource "/api/mt4account/:id/:action",
    id: "@id"

  Resource.getAllMt4Data = ->
    $http.get "/api/mt4account/batch_mt4_data"

  Resource.batchMt4Data = (ids) ->
    $http.get "/api/mt4account/batch_mt4_data",
      params:
        id: ids

  Resource::getMt4Data = ->
    self = @
    $q (resolve, reject) ->
      $http.get "/api/mt4account/batch_mt4_data",
        params:
          id: self.mt4_id
      .catch reject
      .then (res) ->
        resolve res.data[self.mt4_id]

  Resource::refresh = ->
    self = @
    $q (resolve, reject) ->
      Resource.get id: self.id
      .$promise.catch reject
      .then (data) ->
        angular.extend self, data
        resolve self


  Resource::recoverPassword = ->
    OTPService.post "/api/mt4account/#{@id}/recover_password"


  Resource::changeLeverage = (newLeverage) ->
    OTPService.post "/api/mt4account/#{@id}/change_leverage",
      leverage: newLeverage
  Resource::changeLeverageFormData = ->
    getFormData "/api/mt4account/#{@id}/change_leverage"


  Resource::changeOptionsStyle = (newStyle) ->
    self = @
    OTPService.post "/api/mt4account/#{@id}/change_options_style",
      style: newStyle
    .then (res) ->
      angular.extend self, res.data.object
  Resource::changeOptionsStyleFormData = ->
    getFormData "/api/mt4account/#{@id}/change_options_style"


  Resource::changeRebate = (value) ->
    OTPService.post "/api/mt4account/#{@id}/change_rebate",
      value: value
    .then (res) ->
      angular.extend self, res.data.object
  Resource::changeRebateFormData = ->
    getFormData "/api/mt4account/#{@id}/change_rebate"


  Resource::restoreFromArchive = ->
    self = @
    $http.post "/api/mt4account/#{@id}/restore"
    .then (res) ->
      angular.extend self, res.data.object


  Resource::getAgents = (demo)->
    data = if demo then demo: true else null
    self = @
    $q (resolve, reject) ->
      $http.get "/api/mt4account/#{self.id}/agents",
        params: data
      .success resolve
      .catch reject


  Resource::demoDeposit = (value) ->
    self = @
    $http.post "/api/mt4account/#{@id}/demo_deposit",
      value: value
    .then (res) ->
      angular.extend self, res.data.object
  Resource::demoDepositFormData = ->
    getFormData "/api/mt4account/#{@id}/demo_deposit"


  Resource::init = ->

  Resource
