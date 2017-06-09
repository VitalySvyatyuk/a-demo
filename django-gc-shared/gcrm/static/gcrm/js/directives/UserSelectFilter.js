import {Users} from '../services/Users'

angular.module('GCRM').component('userSelectFilter', {
  bindings: {
    model: '=',
    onChange: '&',
    hideNullManager: '=',
    usersInfo: '='
  },
  templateUrl: '/gcrm/templates/component.userSelectFilter.html',
  controllerAs: 'userSelectFilter',
  controller: function (Users) {
    this.Users = Users
    this.offices = _(Users.objects.items)
    if (!this.Users.mapping[MY_USER_ID].data.can_see_all_users)
      this.offices = this.offices.filter({data: {is_managable: true}})
    this.offices = Users.offices
    this.addUser = (manager) => {
      if(!manager) {
        this.model.push('null')
        return this.onChange()
      }

      this.model.push(manager.data.id)

      let userOffice = this.Users.mappingOffices[manager.data.office.id]
      if(_.difference(userOffice.managers.map((u) => u.data.id), this.model).length == 0)
        this.addOffice(userOffice)
      this.onChange()
    }

    this.addOffice = (office) => {
      for(let manager of office.managers)
        if(~this.model.indexOf(manager.data.id))
          this.model.splice(this.model.indexOf(manager.data.id), 1)
      this.model.push(`office${office.id}`)
      this.onChange()
    }

    this.removeId = (id) => {
      this.model.splice(this.model.indexOf(id), 1)
      this.onChange()
    }
  }
})
