import {Model} from '../utils/Model'
import {PaginatedCollection} from '../utils/Collection'


export class Call extends Model {
  static collection = PaginatedCollection;
  collection = PaginatedCollection;
  static url = '/api/gcrm/call';
  url = '/api/gcrm/call';

}