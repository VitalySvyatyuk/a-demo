import {StateSavingModel} from '../utils/Model'
import {PaginatedCollection} from '../utils/Collection'


export class Note extends StateSavingModel {
  static collection = PaginatedCollection;
  collection = PaginatedCollection;
  static url = '/api/gcrm/note';
  url = '/api/gcrm/note';
}
