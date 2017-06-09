app.controller "ProfileInfoController", ($scope, $rootScope, OTPService, countries, regions, formData, $location) ->
  updateInitialUser = ->
    $scope.initialUser = angular.copy($rootScope.user)
    $rootScope.user.profile.nationality or= $rootScope.user.profile.country


    if JSON.stringify($scope.user.profile.investment_undertaking) != JSON.stringify({"Units of collective investment undertaking": "No"})
      $scope.user.profile.investment_undertaking = 'Open'
    else
      $scope.user.profile.investment_undertaking = 'None'

    if JSON.stringify($scope.user.profile.transferable_securities) != JSON.stringify({"Transferable securities": "No"})
      $scope.user.profile.transferable_securities = 'Open'
    else
      $scope.user.profile.transferable_securities = 'None'

    if JSON.stringify($scope.user.profile.forex_instruments) != JSON.stringify({"Trading experience FOREX/CFDs": "No"})
      $scope.user.profile.forex_instruments = 'Open'
    else
      $scope.user.profile.forex_instruments = 'None'

    if JSON.stringify($scope.user.profile.derivative_instruments) != JSON.stringify({"Derivative instruments (incl. options, futures, swaps, FRAs, etc.)": "No"})
      $scope.user.profile.derivative_instruments = 'Open'
    else
      $scope.user.profile.derivative_instruments = 'None'

    
    $scope.user.profile.derivative_instruments_exp = 'less-one-year'
    $scope.user.profile.derivative_instruments_train = 'seminar'
    $scope.user.profile.derivative_instruments_aver = 'Less than $10 000'
    $scope.user.profile.derivative_instruments_freq = 'daily'

    $scope.user.profile.forex_instruments_exp = 'less-one-year'
    $scope.user.profile.forex_instruments_train = 'seminar'
    $scope.user.profile.forex_instruments_aver = 'Less than $10 000'
    $scope.user.profile.forex_instruments_freq = 'daily'

    $scope.user.profile.transferable_securities_exp = 'less-one-year'
    $scope.user.profile.transferable_securities_train = 'seminar'
    $scope.user.profile.transferable_securities_aver = 'Less than $10 000'
    $scope.user.profile.transferable_securities_freq = 'daily'

    $scope.user.profile.investment_undertaking_exp = 'less-one-year'
    $scope.user.profile.investment_undertaking_train = 'seminar'
    $scope.user.profile.investment_undertaking_aver = 'Less than $10 000'
    $scope.user.profile.investment_undertaking_freq = 'daily'

  $scope.save = () ->
    if $scope.user.profile.derivative_instruments == 'Open'
      $scope.user.profile.derivative_instruments = {"Years of experience": $scope.user.profile.derivative_instruments_exp, "Average volume of transaction per year (USD)": $scope.user.profile.derivative_instruments_aver, "Training received": $scope.user.profile.derivative_instruments_train, 'Frequency of transactions': $scope.user.profile.derivative_instruments_freq}
    else
      $scope.user.profile.derivative_instruments = {"Derivative instruments (incl. options, futures, swaps, FRAs, etc.)": "No"}


    if $scope.user.profile.forex_instruments == 'Open'
      $scope.user.profile.forex_instruments = {"Years of experience": $scope.user.profile.forex_instruments_exp, "Average volume of transaction per year (USD)":  $scope.user.profile.forex_instruments_aver, "Training received": $scope.user.profile.forex_instruments_train, 'Frequency of transactions': $scope.user.profile.forex_instruments_freq}
    else
      $scope.user.profile.forex_instruments = {"Trading experience FOREX/CFDs": "No"}


    if $scope.user.profile.transferable_securities == 'Open'
      $scope.user.profile.transferable_securities = {"Years of experience": $scope.user.profile.transferable_securities_exp, "Average volume of transaction per year (USD)": $scope.user.profile.transferable_securities_aver, "Training received": $scope.user.profile.transferable_securities_train, 'Frequency of transactions': $scope.user.profile.transferable_securities_freq}
    else
      $scope.user.profile.transferable_securities = {"Transferable securities": "No"}


    if $scope.user.profile.investment_undertaking == 'Open'
      $scope.user.profile.investment_undertaking = {"Years of experience": $scope.user.profile.investment_undertaking_exp, "Average volume of transaction per year (USD)": $scope.user.profile.investment_undertaking_aver, "Training received": $scope.user.profile.investment_undertaking_train, 'Frequency of transactions': $scope.user.profile.investment_undertaking_freq}
    else 
      $scope.user.profile.investment_undertaking = {"Units of collective investment undertaking": "No"}

    if $scope.user.profile.education_level == 'Other'
      $scope.user.profile.education_level = $scope.user.profile.education_level_spec
    if $scope.user.profile.nature_of_biz == 'Other'
      $scope.user.profile.nature_of_biz = $scope.user.profile.nature_of_biz_spec
    if $scope.user.profile.source_of_funds == 'Other'
      $scope.user.profile.source_of_funds = $scope.user.profile.source_of_funds_spec

    delete $scope.errors
    $scope.setGlobalLoading true
    $rootScope.user.$patch()
    .finally -> $scope.setGlobalLoading false
    .then (data) -> updateInitialUser()
    .catch (res) ->
      if res.status is 511
        OTPService.processResource res.data.detail, $scope.user, $scope.user.$patch
        .then updateInitialUser
      else
        if JSON.stringify($scope.user.profile.investment_undertaking) != JSON.stringify({"Units of collective investment undertaking": "No"})
          $scope.user.profile.investment_undertaking = 'Open'
        else
          $scope.user.profile.investment_undertaking = 'None'

        if JSON.stringify($scope.user.profile.transferable_securities) != JSON.stringify({"Transferable securities": "No"})
          $scope.user.profile.transferable_securities = 'Open'
        else
          $scope.user.profile.transferable_securities = 'None'

        if JSON.stringify($scope.user.profile.forex_instruments) != JSON.stringify({"Trading experience FOREX/CFDs": "No"})
          $scope.user.profile.forex_instruments = 'Open'
        else
          $scope.user.profile.forex_instruments = 'None'

        if JSON.stringify($scope.user.profile.derivative_instruments) != JSON.stringify({"Derivative instruments (incl. options, futures, swaps, FRAs, etc.)": "No"})
          $scope.user.profile.derivative_instruments = 'Open'
        else
          $scope.user.profile.derivative_instruments = 'None'
        $scope.errors = res.data

  $scope.registrationSave = () ->
    $scope.save().then () ->
      if !$scope.errors
        $rootScope.reloadUser().$promise.then () ->
          $location.path($rootScope.registrationCompleteLink() or '/trading/')

  $scope.selectFirstRegion = () ->
    $scope.user.profile.state = _.findWhere($scope.regions,
      country: $scope.user.profile.country
    ).id

  $scope.stateFilter = (a) ->
    if $scope.user.profile
      return a.country == $scope.user.profile.country

  $scope.formatPhoneCodeLabel = (option) ->
    s = _.ljust option.phone_code, 7
    "+#{s} (#{option.name})".replace ///\ ///g, '&nbsp;'

  $scope.filterCountries = (a) ->
    return a.country == $scope.user.profile.country

  # Subscribe on event to restore values
  $scope.$on "$locationChangeStart", (event, next, current) ->
    $rootScope.user = $scope.initialUser

  updateInitialUser()
  $scope.countries = countries
  $scope.regions = regions
  $scope.formData = formData
