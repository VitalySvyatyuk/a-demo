import {Model} from '../utils/Model'
import {Collection} from '../utils/Collection'
import {Task} from './Task'
import _ from 'lodash'


export class Manager extends Model {
  static collection = Collection;
  collection = Collection;
  static url = '/api/gcrm/manager';
  url = '/api/gcrm/manager';

  static getStats(params) {
    return this.action('GET', 'get_stats', {params: params})
  }

  static getInfo(){
    return q((resolve, reject) => {
      this.action('GET', 'get_info', {ignoreLoadingBar: true}).catch(reject).then((data) => {
        resolve({
          'tasks': {
            'overdue': data.tasks.overdue.map((t) => new Task(t)),
            'next': data.tasks.next.map((t) => new Task(t)),
          },
          'clients': {
            'free': data.clients.free
          },
          'counts': {
            'reassign': data.counts.reassign,
            'next': data.counts.next,
            'overdue': data.counts.overdue
          }
        })
      })
    })
  }

  setPassword(value){
    return this.action('POST', 'set_password', {data: {value: value}})
  }

  revoke(){
    return this.action('POST', 'revoke')
  }

  setName(last, first, middle){
    return this.action('POST', 'set_name', {data: {last: last, first: first, middle: middle}}).then((data) => {
      this.data = data.object
      return data
    })
  }

  static findManagers(value) {
    return this.action('GET', 'find_managers', {params: {value: value}})
  }

  static setAsManager(user, office) {
    return this.action('POST', 'set_as_manager', {data: {user: user, office: office}})
  }

  canSetAgentCodes() {
    return this.action('GET', 'can_set_agent_codes')
  }
}

