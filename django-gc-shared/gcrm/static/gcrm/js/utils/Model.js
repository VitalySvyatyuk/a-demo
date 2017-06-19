import _ from 'lodash'

class BaseModel {
  constructor(data, extra) {
    if(data)
      this.processData(data)
  }

  static get(id, ...args) {
    return new this({id: id}, ...args).reload()
  }
  static getList(...args) {
    return new this.collection(this, ...args).reload()
  }
  static createCollection(data, ...args) {
    let collection = new this.collection(this, ...args)
    collection.processData(data)
    return collection
  }

  reload() {
    return q((resolve, reject) => {
      this.isLoading = true
      http.get(`${this.url}/${this.data.id}`)
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

  processData(data) {
    this.data = data
  }
}


class SavableModel extends BaseModel {
  postData(method, url, params, fields) {
    return q((resolve, reject) => {
      this.isLoading = true
      this.errors = null
      http({
        method: method,
        url: url,
        params: params,
        data: fields? _(this.data).pick(fields) : this.data
      })
      .finally(() => {
        this.isLoading = false
      })
      .then((res) => {
        this.processData(res.data)
        resolve(this)
      })
      .catch((res) => {
        this.errors = res.data
        reject(this)
      })
    })
  }

  create(params) {
    return this.postData('POST', this.url, params)
  }
  update(params) {
    return this.postData('PUT', `${this.url}/${this.data.id}`, params)
  }
  patch(fields) {
    return this.postData('PATCH', `${this.url}/${this.data.id}`, null, fields)
  }
  save(...args) {
    if(this.data.id)
      return this.update(...args)
    else
      return this.create(...args)
  }
  delete(params) {
    return q((resolve, reject) => {
      http({
        method: 'DELETE',
        url: `${this.url}/${this.data.id}`,
        params: params,
      })
      .then((res) => {
        resolve(res.data)
      })
      .catch(reject)
    })
  }
  static options(params) {
    return q((resolve, reject) => {
      http({
        method: 'OPTIONS',
        url: this.url,
        params: params,
      })
      .then((res) => {
        resolve(res.data)
      })
      .catch(reject)
    })
  }
}


class ActionableModel extends SavableModel {
  action(method, name, params) {
    return q((resolve, reject) => {
      http(_.extend({
        method: method,
        url: `${this.url}/${this.data.id}/${name}`,
      }, params))
      .then((res) => {
        resolve(res.data)
      })
      .catch(reject)
    })
  }

  static action(method, name, params) {
    return q((resolve, reject) => {
      http(_.extend({
        method: method,
        url: `${this.url}/${name}`,
      }, params))
      .then((res) => {
        resolve(res.data)
      })
      .catch(reject)
    })
  }
}


class EditableModel extends ActionableModel {
  startEdit() {
    this.originalData = _.cloneDeep(this.data)
    this.isEditing = true
  }
  cancelEdit() {
    this.data = this.originalData
    this.originalData = null
    this.isEditing = false
  }
  applyEdit(fields) {
    if(fields && self.data.id)
      return self.patch()
    else
      return self.save()
  }
}



export class Model extends EditableModel {

}

export class StateSavingModel extends Model {
  processData(data) {
    if(this.trackFields && this.trackFields.length)
      this.refreshState(data)
    super.processData(data)
    if(this.trackFields && this.trackFields.length)
      this.refreshStateStatus()
  }
  refreshState(data) {
    this.state = _(data || this.data).chain().pick(this.trackFields).cloneDeep().value()
  }
  refreshStateStatus() {
    if(this.trackFields && this.trackFields.length) {
      this.isChanged = !_.eq(
        angular.copy(_.pick(this.data, this.trackFields)),
        angular.copy(_.pick(this.state, this.trackFields))
      )
    }
  }
  revertData(fields) {
    _.extend(this.data, _(this.state).chain().pick(fields || this.trackFields).cloneDeep().value())
    this.errors = null
    this.refreshStateStatus()
  }
  saveChanges() {
    if(!(this.data.id && this.trackFields && this.trackFields.length))
      return this.save()
    else
      return this.patch(this.trackFields)
  }
}
