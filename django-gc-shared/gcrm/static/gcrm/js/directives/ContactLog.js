angular.module('GCRM').component('contactLog', {
  bindings: {
    object: '=',
  },
  transclude: false,
  templateUrl: '/gcrm/templates/component.contactLog.html',
  controllerAs: "contactLog",
  controller: function (Users) {
    this.Users = Users

    this.icon = 'fa-cogs'

    if (this.object.data.event.startsWith('gcrm manager changed')) {
      this.type = 'manager changed'
      this.icon = 'fa-exchange'
    }
  },
})
