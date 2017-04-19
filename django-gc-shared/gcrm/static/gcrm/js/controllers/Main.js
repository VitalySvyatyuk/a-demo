angular.module('GCRM').controller('Main', ($rootScope, $state, Users) => {
  $rootScope.log = console.log.bind(console)
  $rootScope.Users = Users

  $rootScope.contactSearch = (search) => {
    $state.go('contacts', {p: JSON.stringify({search: search})})
  }
})
