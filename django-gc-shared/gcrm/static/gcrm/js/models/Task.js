import {StateSavingModel} from '../utils/Model'
import {PaginatedCollection} from '../utils/Collection'
import {Note} from './Note'
import moment from 'moment-timezone'


export class Task extends StateSavingModel {
  static collection = PaginatedCollection;
  collection = PaginatedCollection;
  static url = '/api/gcrm/task';
  url = '/api/gcrm/task';

  static TYPES_ICON = {
    'CALL': '\uf095',
    'MEETING': '\uf017',
    'MONITORING': '\uf1e5',
    'LETTER': '\uf003',
    'LECTURE': '\uf005',
    'PRACTICE': '\uf007'
  };

  getIcon() {
    return this.constructor.TYPES_ICON[this.data.task_type] || '\uf017'
  }

  processData(data) {
    // create date object to be able to use this
    //   as value for datetime-local field
    if(data.deadline)
      data.deadline = moment(data.deadline).toDate()
    super.processData(data)
  }

  complete(note) {
    return q((resolve, reject) => {
      this.action('POST', 'complete', {
        data: {
          note: note
        }
      }).catch(reject).then((data) => {
        this.processData(data.object)
        resolve()
      })
    })
  }

  postpone(note, deadline) {
    return q((resolve, reject) => {
      this.action('POST', 'postpone', {
        data: {
          note: note,
          deadline: deadline
        }
      }).catch(reject).then((data) => {
        this.processData(data.object)

        resolve({
          'note': new Note(data.note),
          'new_task': new Task(data.new_task),
        })
      })
    })
  }
}
