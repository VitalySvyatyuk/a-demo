angular.module('GCRM').component('contactMt4Account', {
  bindings: {
    object: '='
  },
  transclude: false,
  templateUrl: '/gcrm/templates/component.contactMt4Account.html',
  controllerAs: 'contactMt4Account',
  controller: function(){
    this.contactSearch = (search) => {
      $state.go('contacts', {p: JSON.stringify({search: search})})
    }
  }
});
