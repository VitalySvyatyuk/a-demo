import {StateSavingModel} from '../utils/Model'
import {PaginatedCollection} from '../utils/Collection'
import {Task} from './Task'
import {Note} from './Note'


class ContactPaginatedCollection extends PaginatedCollection {
  processData(data) {
    let managersSummary = data.summary.managers
    data.summary.managers = {}
    for (let managerData of managersSummary)
      data.summary.managers[managerData.manager] = managerData.count
    return super.processData(data)
  }

  batchReassign(new_manager, comment, withTask, taskComment, setAgentCode, agentCode) {
    if(!withTask)
      withTask = false
    if(!setAgentCode)
      setAgentCode = false
    return this.action('POST', 'batch_reassign', {
      new_manager: new_manager, comment: comment, with_task: withTask, task_comment: taskComment, set_agent_code: setAgentCode, agent_code: agentCode
    })
  }

  batchAgentCode(code) {
    return this.action('POST', 'batch_agent_code', {code: code})
  }
}

export class Contact extends StateSavingModel {
  static collection = ContactPaginatedCollection;
  collection = ContactPaginatedCollection;
  static url = '/api/gcrm/contact';
  url = '/api/gcrm/contact';

  trackFields = ['name', 'info', 'tags', 'manager'];

  userResetOTP() {
    return this.action('POST', 'user_reset_otp').then(() => {
      this.data.user.otp.device = null
      this.data.user.otp.is_lost = true
    })
  }

  reassign(comment) {
    this.isLoading = true
    let q = this.action('POST', 'reassign', {
      data: {
        manager: this.data.manager,
        comment: comment
      }
    })
    q.then((data) => {
      this.isLoading = false
      switch (data.status) {
        case 'changed':
          this.state.manager = this.data.manager
          break;
        case 'request_created':
          this.revertData(['manager'])
          this.data.reassign_requests.push(data.object)
          break;
        case 'request_exists':
          this.revertData(['manager'])
          break;
      }
      return data
    }, (res) => {
      this.isLoading = false
      return res
    })
    return q
  }

  getFeed(type, offset=0, limit=100) {
    return q((resolve, reject) => {
      this.action('GET', 'feed', {params: {type: type, limit: limit, offset: offset}}).catch(reject).then((data) => {
        _.extend(data, {
          offset: offset,
          limit: limit,
          left: Math.max(0, data.total - (offset + limit)),
          items: data.items.map((record) => {
            if(record.feed_type == 'note')
              return new Note(record)
            else if (record.feed_type == 'task')
              return new Task(record)
            else  // compat
              return {data: record}
          }),
          loadMore: () => {
            let q = this.getFeed(type, data.offset + data.limit, data.limit)
            q.then((moreData) => {
              _.extend(data, {
                items: data.items.concat(moreData.items),
                offset: moreData.offset,
                left: moreData.left,
              })
            })
            return q
          }
        })
        resolve(data)
      })
    })
  }

  static getNextClient() {
    return this.action('GET', 'get_next_client')
  }
}
