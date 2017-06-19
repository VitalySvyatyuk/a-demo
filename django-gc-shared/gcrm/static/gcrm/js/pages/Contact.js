import {Task} from '../models/Task'
import {Note} from '../models/Note'

angular.module('GCRM').controller('ContactPage', ($scope, object) => {
  $scope.object = object
  $scope.feedLimit = 50
  $scope.setFeedLimit = (v) => $scope.feedLimit = v

  $scope.editTag = (tag) => {
    let newTag = prompt('', tag)
    if(newTag === null)
      return
    if(tag)
      $scope.object.data.tags = _.without($scope.object.data.tags, tag)
    if(newTag)
      $scope.object.data.tags.push(newTag)
    $scope.object.data.tags = _.uniq($scope.object.data.tags)
    $scope.object.patch(['tags'])
  }

  $scope.saveName = () => {
    if (!$scope.object.data.name)
      $scope.object.data.name = $scope.object.data.user.name
    $scope.object.data.name_sync_from_user = $scope.object.data.name == $scope.object.data.user.name
    $scope.object.patch(['name', 'name_sync_from_user']).then(() => {
      $scope.nameForm.$setPristine()
      $scope.nameForm.$setUntouched()
    })
  }

  $scope.revertName = () => {
    $scope.object.data.name = $scope.object.state.name
    $scope.nameForm.$setPristine()
    $scope.nameForm.$setUntouched()
  }

  $scope.reassign = (comment) => {
    $scope.object.reassign(comment).then((data) => {
      if(data.status == 'request_created' || data.status == 'request_exists')
        alert(data.detail)
      else if(data.status == 'changed')
        object.getFeed().then((data) => $scope.feed = data)
    }, (res) => {
      $scope.reassignErrors = res.data
    })
  }

  $scope.initNew = (type) => {
    if(type == 'task')
      $scope.newTask = new Task({
        contact: {
          id: $scope.object.data.id
        },
        task_type: 'CALL',
        assignee: $scope.object.data.manager || MY_USER_ID,
        deadline: moment().set('hour', 23).set('minute', 59).set('second', 0).set('millisecond', 0)
      })
    else if(type == 'note')
      $scope.newNote = new Note({
        contact: {
          id: object.data.id
        },
      })
  }

  $scope.cancelNew = (type) => {
    if(type == 'task')
      $scope.newTask = null
    else if(type == 'note')
      $scope.newNote = null
  }

  $scope.feedRecordAdded = (record) => {
    $scope.$broadcast('feedRecordAdded', record);
  }
})
