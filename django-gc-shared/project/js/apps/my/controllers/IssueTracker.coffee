app.controller "IssueTrackerController", ($scope, $upload, IssueComment, userIssues, $modal, IssueCreateModal) ->
  initComment = ->
    $scope.errors = null
    $scope.files = []
    $scope.comment = issue: $scope.selected.id
    unless $scope.commentFormData?
      (new IssueComment issue: $scope.selected.id)
      .formData().then (data) ->
        $scope.commentFormData = data

  loadIssue = (issue) ->
    initComment()
    $scope.selected.refresh()
    $scope.comments = null
    $scope.setGlobalLoading true
    IssueComment.query issue: $scope.selected.id
    .$promise
    .finally -> $scope.setGlobalLoading false
    .then (data) ->
      $scope.comments = data if $scope.selected is issue

  $scope.select = (issue) ->
    if $scope.selected is issue
      $scope.selected = null
    else
      $scope.selected = issue
      loadIssue issue

  $scope.selectCommentFiles = (files) ->
    $scope.files ?= []
    #add files and remove dupes by name
    $scope.files = _($scope.files.concat files).uniq (f) -> f.name

  $scope.unselectCommentFile = (file) ->
    $scope.files = _($scope.files).without file

  $scope.postComment = ->
    $scope.setGlobalLoading true
    $scope.errors = null

    IssueComment.createWithFile $scope.comment, $scope.files
    .success (data) ->
      $scope.setGlobalLoading false
      if $scope.selected?.id is data.issue
        initComment()
        $scope.comments.push new IssueComment(data)
        $scope.selected.refresh()
    .error (data) ->
      $scope.setGlobalLoading false
      $scope.errors = data

  $scope.viewImage = (url) ->
    $scope.setGlobalLoading true
    ImageViewModal.open $modal, url

  $scope.createIssue = ->
    IssueCreateModal().result.then (issue) ->
      $scope.issues.unshift issue

  $scope.issues = userIssues
  if $scope.issues.length > 0
    (new IssueComment issue: userIssues[0].id)
    .formData().then (data) ->
      $scope.commentFormData = data
