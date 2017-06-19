angular.module('GCRM').component('contactCall', {
  bindings: {
    object: '=',
  },
  transclude: false,
  templateUrl: '/gcrm/templates/component.contactCall.html',
  controllerAs: 'contactCall',
  controller: function ($scope, $timeout) {
    this.showPlayer = () => {
      this.playerShown = true
      $scope.$root.$broadcast('shutup', this)
    }
    $scope.$on('shutup', (e, sender) => {
      if(sender !== this)
      this.playerShown = false
    })
  }
})
