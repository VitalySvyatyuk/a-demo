app.controller "PrivateMessageController", ($scope, $routeParams, messages, PrivateMessage) ->
  $scope.getHtmlBody = (message) ->
    if message.is_html
      message.body
    else
      message.body.replace /\n/g, '<br/>'

  $scope.select = (msg) ->
    if $scope.selected is msg
      $scope.selected = null
    else
      $scope.selected = msg

    #mark as read
    if $scope.selected and $scope.selected.new
      PrivateMessage.batchMark 'read', [$scope.selected.id]
      $scope.selected.new = false
      $scope.setInboxCount $scope.inboxCount - 1

  $scope.$watch 'allChecked', (val) ->
    _.each $scope.messages.items, (msg) -> msg.isChecked = val

  getChecked = ->
    _($scope.messages.items).where isChecked: true

  $scope.markDeleted = (message) ->
    msgs = if message is 'checked' then getChecked() else [message]
    $scope.select null if $scope.selected in msgs

    $scope.setGlobalLoading true
    PrivateMessage.batchMark 'deleted', _(msgs).pluck('id')
    .finally ->
      $scope.setGlobalLoading false
      $scope.updateInboxCount()
      $scope.messages.load()

  $scope.markRead = (message) ->
    msgs = if message is 'checked' then getChecked() else [message]

    $scope.setGlobalLoading true
    PrivateMessage.batchMark 'read', _(msgs).pluck('id')
    .finally ->
      $scope.updateInboxCount()
      $scope.setGlobalLoading false
      $scope.allChecked = false if message is 'checked'
      _(msgs).each (msg) ->
        msg.isChecked = false if message is 'checked'
        msg.new = false

  $scope.markUnread = (message) ->
    msgs = if message is 'checked' then getChecked() else [message]

    $scope.setGlobalLoading true
    PrivateMessage.batchMark 'unread', _(msgs).pluck('id')
    .finally ->
      $scope.setGlobalLoading false
      $scope.allChecked = false if message is 'checked'
      _(msgs).each (msg) ->
        msg.isChecked = false if message is 'checked'
        msg.new = true

  $scope.messages = messages
  $scope.messages.onLoad = ->
    $scope.allChecked = false
  $scope.$watch 'messages.isLoading', $scope.setGlobalLoading

  if $routeParams.openMessage
    message = _($scope.messages.items).find id: Number($routeParams.openMessage)
    $scope.select(message)