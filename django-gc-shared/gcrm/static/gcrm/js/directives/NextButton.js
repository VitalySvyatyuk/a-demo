import {Contact} from '../models/Contact'

angular.module('GCRM').directive('nextButton', function() {
  return {
    restrict: 'AE',
    scope: {
      objects: '=',
    },
    templateUrl: '/gcrm/templates/component.nextButton.html',
    controllerAs: 'nextButton',
    controller: function ($state, Info) {
      this.info = Info
      this.getNextClient = () => {
        Contact.getNextClient().catch((res) => {
          alert(res.data.detail)
          if(res.data.last_id)
          $state.go('contact.feed', {id: res.data.last_id})
        }).then((data) => {
          $state.go('contact.feed', {id: data.id})
        })
      }
    }
  }
})
