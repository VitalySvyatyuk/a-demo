import {Manager} from '../models/Manager'

angular.module('GCRM').service('Users', function() {
  this.reload = () => {
    return Manager.getList().then((objects) => {
      this.objects = objects
      this.mapping = {}

      let moreThanOne = false
      for(let user of this.objects.items) {
        this.mapping[user.data.id] = user
        if(user.data.id != MY_USER_ID && user.data.is_managable ||
           user.data.id == MY_USER_ID && user.data.can_see_all_users)
          moreThanOne = true
      }
      this.me = this.mapping[MY_USER_ID]
      this.me.moreThanOne = moreThanOne

      this.offices = _(this.objects.items).groupBy((item) =>
        item.data.office.id
      ).map((value) => {
        return {
          id: value[0].data.office.id,
          name: value[0].data.office.name,
          managers: value,
          is_managable: !!_(value).find((m) => m.data.is_managable)
        }
      }).orderBy([
        (o) => o.id != this.me.data.office.id,
        'name'
      ]).value()

      this.mappingOffices = {}
      for (let office of this.offices){
        this.mappingOffices[office.id] = office
      }
    })

  }
})
