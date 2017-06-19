import {StateSavingModel} from '../utils/Model'
import {PaginatedCollection} from '../utils/Collection'


export class ReassignRequest extends StateSavingModel {
  static collection = PaginatedCollection;
  collection = PaginatedCollection;
  static url = '/api/gcrm/reassign_request';
  url = '/api/gcrm/reassign_request';

  static RESULTS = ['Необработанные', 'Одобренные', 'Отклоненные'];

  accept() {
    return this.action('POST', 'accept')
  }

  reject(close_comment) {
    return this.action('POST', 'reject', {data: {close_comment: close_comment}})
  }
}
