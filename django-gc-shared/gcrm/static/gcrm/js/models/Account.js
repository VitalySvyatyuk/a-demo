import {Model} from '../utils/Model'
import {PaginatedCollection} from '../utils/Collection'


export class Account extends Model {
  static collection = PaginatedCollection;
  collection = PaginatedCollection;
  static url = '/api/gcrm/account';
  url = '/api/gcrm/account';

  static getTypes(params) {
    return this.action('GET', 'get_types', {params: params})
  }
}