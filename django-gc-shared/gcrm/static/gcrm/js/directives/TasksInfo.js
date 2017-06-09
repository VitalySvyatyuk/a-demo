angular.module('GCRM').directive('tasksInfo', function() {
  return {
    restrict: 'AE',
    scope: {
      objects: '=',
    },
    templateUrl: '/gcrm/templates/component.tasksInfo.html',
    controllerAs: 'tasksInfo',
    controller: function (Info) {
      this.info = Info
    }
  }
})
