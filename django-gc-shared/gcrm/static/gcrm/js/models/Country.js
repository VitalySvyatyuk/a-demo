import {StateSavingModel} from '../utils/Model'
import {PaginatedCollection} from '../utils/Collection'


export class Country extends StateSavingModel {
  static collection = PaginatedCollection;
  collection = PaginatedCollection;
  static url = '/api/gcrm/country';
  url = '/api/gcrm/country';

  static getLanguages() {
    return this.action('GET', 'get_languages')
  }
  
}
