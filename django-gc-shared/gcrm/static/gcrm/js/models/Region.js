import {StateSavingModel} from '../utils/Model'
import {PaginatedCollection} from '../utils/Collection'


export class Region extends StateSavingModel {
  static collection = PaginatedCollection;
  collection = PaginatedCollection;
  static url = '/api/gcrm/region';
  url = '/api/gcrm/region';
}
