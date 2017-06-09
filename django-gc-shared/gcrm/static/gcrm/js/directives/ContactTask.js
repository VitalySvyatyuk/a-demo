import moment from 'moment-timezone'
import {Task} from '../models/Task'

angular.module('GCRM').component('contactTask', {
  bindings: {
    object: '=',
    onDelete: '&',
    onSave: '&',
    onComplete: '&',
    isLink: '=',
  },
  transclude: false,
  templateUrl: '/gcrm/templates/component.contactTask.html',
  controllerAs: 'contactTask',
  controller: function (Users) {
    this.Users = Users
    this.TASK_TYPES = TASK_TYPES
    this.TYPES_ICON = Task.TYPES_ICON
    if(!this.object.data.text)
      this.mode = 'edit'
    else if (this.object.data.closed_at)
      this.mode = 'closed'
    else
      this.mode = null

    this.complete = (comment) => {
      this.object.complete(comment).then(() => {
        this.mode = 'closed'
        this.onComplete()
      })
    }

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

    this.setDeadlineToday = () => this.object.data.deadline = moment().hour(23).minute(59).second(0).millisecond(0).toDate()
    this.setDeadlineNextHour = () => this.object.data.deadline = moment().add(1, 'h').second(0).millisecond(0).toDate()
    this.setDeadlineTomorrow = () => this.object.data.deadline = moment().add(1, 'd').hour(23).minute(59).second(0).millisecond(0).toDate()
    this.setDeadlineNextWeek = () => this.object.data.deadline = moment().add(1, 'w').hour(23).minute(59).second(0).millisecond(0).toDate()
    this.setDeadlinePlus30Min = () => this.object.data.deadline = moment().add(30, 'm').second(0).millisecond(0).toDate()
  }
})
