getPages = (page, numPages) ->
  _.range Math.max(page - 2, 1),
    Math.min(page + 2, numPages) + 1

app.factory "Paginator", ->
  class Paginator
    page: 1
    isLoading: false
    perPage: 10
    perPageChoices: [10, 20, 50, 100]
    items: []
    constructor: (@obj, @params={}) ->

    processData: (data) ->
      _.extend @, _.omit(
        data, 'num_pages', 'results')
      @numPages = data.num_pages
      @items = @items.concat data.results
      @page = data.page
      @hasMore = @page < @numPages
      @pages = getPages @page, @numPages
      @onLoad() if @onLoad
      @ # so in resolve we will get paginator object

    refresh: ->
      return if @isLoading
      @load @page

    load: (page) ->
      return if @isLoading
      page ?= 1

      @isLoading = true
      @obj.query _.extend({
        page: page
        per_page: @perPage
      }, @params)
      .$promise
      .finally => @isLoading = false
      .then (data) =>
        @items = []
        @processData data

    goto: (page) ->
      return if @isLoading
      @load page

    gotoNext: ->
      return if @isLoading or not @hasMore
      @load Math.min(@numPages, @page + 1)

    gotoPrev: ->
      return if @isLoading
      @load Math.max(1, @page - 1)

    setPerPage: (num) ->
      return if @isLoading
      @perPage = num
      @load 1

    more: ->
      return if @isLoading or not @hasMore
      @isLoading = true
      @obj.query _.extend({
        page: @page + 1
        per_page: @perPage
      }, @params)
      .$promise
      .finally => @isLoading = false
      .then (data) =>
        @processData data