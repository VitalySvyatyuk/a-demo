angular.module('GCRM').component('contactInfo', {
  bindings: {
    object: '=',
  },
  templateUrl: '/gcrm/templates/component.contactInfo.html',
  controllerAs: 'contactInfo',
  controller: function () {
    this.addContactInfo = () => {
      this.object.data.info.push({type: 'phone'})
    }

    this.save = () => {
      this.object.patch(['info'])
    }

    this.revert = () => {
      this.object.revertData(['info'])
      this.info = _.cloneDeep(this.object.data.info)
      this.update()
    }

    this.update = () => {
      this.info = _.filter(this.info, (info) => info.value)
      this.object.data.info = _.cloneDeep(this.info)
      this.info.push({type: 'phone'})
      this.info.push({type: 'email'})
      this.info.push({type: 'address'})
    }

    this.info = _.cloneDeep(this.object.data.info)
    this.update()
  }
})
