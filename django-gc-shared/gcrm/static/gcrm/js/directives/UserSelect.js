import {Users} from '../services/Users'

angular.module('GCRM').component('userSelect', {
  bindings: {
    model: '=',
    onChange: '&',
    hideNullManager: '=',
    classes: '=',
  },
  templateUrl: '/gcrm/templates/component.userSelect.html',
  controllerAs: 'userSelect',
  controller: function (Users, $timeout) {
    this.Users = Users
    this.offices = Users.offices
    this.setModel = (user) => {
      this.model = user? user.data.id : user
      $timeout(this.onChange.bind(this), 1);
    }
  }
})
