import _ from 'lodash'


if (window.JSON && !window.JSON.dateParser) {
  var reISO = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2}(?:\.\d*))(?:Z|(\+|-)([\d|:]*))?$/;
  var reMsAjax = /^\/Date\((d|-|.*)\)[\/|\\]$/;
  JSON.dateParser = (key, value) => {
    if (typeof value !== 'string')
      return value
    if (reISO.exec(value))
      return new Date(value)
    if (reMsAjax.exec(value)) {
      var b = a[1].split(/[-+,.]/);
      return new Date(b[0] ? +b[0] : 0 - +b[1]);
    }
    return value
  }
}


class BaseCollection {
  constructor(model, defaultParams, locationParams) {
    this.model = model
    if(defaultParams)
      this.restoreParams(defaultParams)

    this.syncLocation = locationParams != undefined
    if (this.syncLocation) {
      this.currentLocationParams = {}
      if(locationParams.p) {
        this.currentLocationParams = JSON.parse(locationParams.p, JSON.dateParser)
        if (!_.isEmpty(this.currentLocationParams))
          this.restoreParams(this.currentLocationParams)
      }
    }
  }

  reload() {
    if (this.syncLocation && this.onceLoaded) {
      if (!_.isEqual(this.currentLocationParams, this.locationParams()))
        return $state.go($state.current.name, {p: JSON.stringify(this.locationParams())}, {reload: true})
    } else
      this.onceLoaded = true

    return new Promise((resolve, reject) => {
      this.isLoading = true
      http.get(this.model.url, {
        params: this.requestParams()
      })
      .finally(() => {
        this.isLoading = false
      })
      .then((res) => {
        this.processData(res.data)
        resolve(this)
      })
      .catch(reject)
    })
  }

  requestParams() {
    return _.extend({}, this.params)
  }

  processData(items) {
    this.items = items.map((item) => {
      return item.constructor === this.model? item : new this.model(item)
    })
  }

  restoreParams(params) {
  }
  locationParams(params) {
    return {}
  }
}


class SelectableCollection extends BaseCollection {
  collectSelected() {
    this.selectedIds = []
    this.items.forEach((item) => {
      if(item.selected)
        this.selectedIds.push(item.data.id)
    })
  }

  setAllSelected(value) {
    this.items.forEach((item) => {
      item.selected = value
    })
  }

  countSelected() {
    this.collectSelected()
    return this.selectedIds.length
  }

  // WUT?
  // allSelected(value) {
  //   if !arguments.length
  //     @countSelected() == @items.length
  //   else @setAllSelected(value)
  // }
}


class ActionableCollection extends SelectableCollection {
  action(method, url, data) {
    let actionParams = _.extend({}, this.requestParams())
    this.collectSelected()
    actionParams.id = this.selectedIds
    return this.model.action(method, url, {
      params: actionParams,
      data: data
    })
  }
}


class FilterableCollection extends ActionableCollection {
  inlineFilter(params) {
    this.inlineFilterParams = params
    return this.reload()
  }

  restoreParams(params){
    this.inlineFilterParams = params
    super.restoreParams({})
  }

  requestParams() {
    return _.extend(super.requestParams(), this.inlineFilterParams || {})
  }

  locationParams() {
    return Object.assign(this.inlineFilterParams || {}, super.locationParams())
  }
}


class SortableCollection extends FilterableCollection {
  requestParams() {
    if(!this.sortField)
      return super.requestParams()
    return _.extend(super.requestParams(), {
      ordering: (this.sortReversed? '-' : '') + this.sortField
    })
  }

  locationParams() {
    return Object.assign({
      sort_reversed: this.sortReversed,
      sort_field: this.sortField
    }, super.locationParams())
  }

  restoreParams(params) {
    this.sortReversed = params.sort_reversed
    this.sortField = params.sort_field
    super.restoreParams(_.omit(params, ['sort_reversed', 'sort_field']))
  }

  orderBy(sortField) {
    if(this.sortField == sortField)
      this.sortReversed = !this.sortReversed
    else {
      this.sortField = sortField
      this.sortReversed = false
    }
    this.reload()
  }
}


export class Collection extends SortableCollection {
}


let getPages = (page, numPages) => {
  return _.range(
    Math.max(page - 2, 1),
    Math.min(page + 2, numPages) + 1
  )
}


export class PaginatedCollection extends SortableCollection {
  processData(data) {
    this.summary = data.summary
    this.totalPages = data.num_pages
    this.count = data.count
    this.page = data.page
    this.pages = getPages(this.page, this.totalPages)

    return super.processData(
      this.processingMode == 'append'?
        this.items.concat(data.results) : data.results)
  }

  restoreParams(params){
    this.page = params.page || this.page || 1
    this.perPage = params.per_page || this.perPage
    this._prevParams = null
    super.restoreParams(_.omit(params, ['page', 'per_page']))
  }

  locationParams() {
    return Object.assign({
      page: this.page,
      per_page: this.perPage
    }, super.locationParams())
  }

  requestParams() {
    let params = super.requestParams()
    _.extend(params, {
      per_page: this.perPage
    })
    if (this._prevParams && !_.isEqual(this._prevParams, params))
      this.page = 1
    this._prevParams = _.cloneDeep(params)

    //finalize
    params.page = this.page
    return params
  }
  goto(page) {
    this.page = page
    this.reload()
  }

  gotoNext() {
    return this.goto(Math.min(this.totalPages, this.page + 1))
  }
  gotoPrev() {
    return this.goto(Math.max(1, this.page - 1))
  }
  setPerPage(num) {
    this.perPage = num
    this.page = 1
    this.reload()
  }
  reload(processingMode) {
    this.processingMode = processingMode
    return super.reload().catch((res) => {
      if(res.status == 404)
        this.goto(1)
    })
  }

  loadMore() {
    this.page += 1
    this.reload('append')
  }
}
