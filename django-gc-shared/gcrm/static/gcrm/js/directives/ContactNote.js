angular.module('GCRM').component('contactNote', {
  bindings: {
    object: '=',
    onDelete: '&',
    onSave: '&',
  },
  transclude: false,
  templateUrl: '/gcrm/templates/component.contactNote.html',
  controllerAs: "contactNote",
  controller: function (Users) {
    this.Users = Users
    this.mode = this.object.data.text? null : 'edit'

    this.remove = () => {
      if(!this.object.data.id)
        return this.onDelete()
      return this.object.delete().then(() => {
        this.onDelete()
      })
    }

    this.save = () => {
      this.object.save(this.object.data.id? null : {contact: this.object.data.contact.id}).then(() => {
        this.mode = null
        this.onSave()
      })
    }
  },
})
