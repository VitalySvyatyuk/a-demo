import {Contact} from './models/Contact'
import {Manager} from './models/Manager'
import {Task} from './models/Task'
import {Account} from './models/Account'
import {ReassignRequest} from './models/ReassignRequest'
import {Call} from './models/Call'
import moment from 'moment-timezone'
import {Country} from "./models/Country";

angular.module('GCRM').config(($stateProvider, $locationProvider, $urlRouterProvider) => {
  $locationProvider.html5Mode(true)
  $urlRouterProvider.otherwise("/contact")

  $stateProvider
  .state('contacts', {
    url: "/contact?p",
    templateUrl: "/gcrm/templates/contacts.html",
    controller: 'ContactsPage',
    resolve: {
      users: (Users) => Users.reload(),
      objects: ($stateParams) => {
        return Contact.getList({
          sort_field: 'user__profile__last_activity_ts',
          sort_reversed: true,
          tags: [],
          manager: [],
        }, $stateParams)
      },
      languages: () => Country.getLanguages(),
    }
  })
  .state('contacts.create', {
    url: "/create",
    views: {
      "create": {
        templateUrl: "/gcrm/templates/contacts.create.html",
        controller: 'ContactCreatePage'
      }
    },
    resolve: {
      object: ($stateParams) => new Contact({manager: MY_USER_ID}),
    }
  })
  .state('contact', {
    abstract: true,
    url: "/contact/:id",
    templateUrl: "/gcrm/templates/page.contact.html",
    controller: 'ContactPage',
    resolve: {
      users: (Users) => Users.reload(),
      object: ($stateParams, $state) => Contact.get($stateParams.id).catch((res) => {
        alert(res.data.detail)
      }),
    }
  })
    .state('contact.feed', {
      url: "",
      controller: "ContactFeedPage",
      templateUrl: "/gcrm/templates/page.contact.feed.html",
      resolve: {
        objects: (object) => object.getFeed()
      }
    })
    .state('contact.mt4accounts', {
      url: "/mt4accounts",
      controller: "ContactFeedPage",
      templateUrl: "/gcrm/templates/page.contact.feed.html",
      resolve: {
        objects: (object) => object.getFeed('mt4account')
      }
    })
    .state('contact.logs', {
      url: "/logs",
      controller: "ContactFeedPage",
      templateUrl: "/gcrm/templates/page.contact.feed.html",
      resolve: {
        objects: (object) => object.getFeed('fulllog')
      }
    })
    .state('contact.calls', {
      url: "/calls",
      controller: "ContactFeedPage",
      templateUrl: "/gcrm/templates/page.contact.feed.html",
      resolve: {
        objects: (object) => object.getFeed('call')
      }
    })
    .state('contact.payments', {
      url: "/payments",
      controller: "ContactPaymentsPage",
      templateUrl: "/gcrm/templates/page.contact.payments.html",
      resolve: {
        objects: (object) => object.getFeed('payment', 0, 999999)
      }
    })
  .state('tasks', {
    url: "/tasks/my",
    templateUrl: "/gcrm/templates/tasks.html",
    controller: 'TasksPage',
    resolve: {
      users: (Users) => Users.reload(),
      overdue: () => Task.getList({
        deadline_1: moment().toDate(),
        is_completed: false,
        assignee: [MY_USER_ID]
      }),
      today: () => Task.getList({
        deadline_0: moment().toDate(),
        deadline_1: moment().set('hour', 23).set('minute', 59).set('second', 59).toDate(),
        is_completed: false,
        assignee: [MY_USER_ID]
      }),
      tomorrow: () => Task.getList({
        deadline_0: moment().add(1, 'days').set('hour', 0).set('minute', 0).set('second', 0).toDate(),
        deadline_1: moment().add(1, 'days').set('hour', 23).set('minute', 59).set('second', 59).toDate(),
        is_completed: false,
        assignee: [MY_USER_ID]
      }),
    }
  })
  .state('tasks_all', {
    url: "/tasks/all?p",
    templateUrl: "/gcrm/templates/tasks_all.html",
    controller: 'TasksAllPage',
    resolve: {
      users: (Users) => Users.reload(),
      objects: ($stateParams) => {
        return Task.getList({
          assignee: [MY_USER_ID],
        }, $stateParams)
      },
    }
  })
  .state('reassigns', {
    url: "/reassigns?p",
    templateUrl: "/gcrm/templates/reassign_requests.html",
    controller: 'ReassignsPage',
    resolve: {
      users: (Users) => Users.reload(),
      objects: ($stateParams) => ReassignRequest.getList({
        'result': 'all',
        'author': [],
        'new_manager': [],
        'previous_manager': [],
      }, $stateParams),
    }
  })
  .state('analytics', {
    url: "/analytics",
    templateUrl: "/gcrm/templates/analytics.html",
    controller: 'AnalyticsPage',
    resolve: {
      users: (Users) => Users.reload(),
      objects: () => Manager.getStats({
        stats_date_0: moment().startOf('day').toDate(),
        stats_date_1: moment().endOf('day').toDate()
      }),
    }
  })
  .state('accounts', {
    url: "/accounts?p",
    templateUrl: "/gcrm/templates/accounts.html",
    controller: 'AccountsPage',
    resolve: {
      users: (Users) => Users.reload(),
      objects: ($stateParams) => Account.getList({'type': []}, $stateParams),
      types: () => Account.getTypes()
    }
  })
  .state('calls', {
    url: "/calls?p",
    templateUrl: "/gcrm/templates/calls.html",
    controller: 'CallsPage',
    resolve: {
      users: (Users) => Users.reload(),
      objects: ($stateParams) => Call.getList({
        'manager': [],
        'disposition': 'all',
      }, $stateParams),
    }
  })
  .state('managers', {
    url: "/managers?p",
    templateUrl: "/gcrm/templates/managers.html",
    controller: 'ManagersPage',
    resolve: {
      users: (Users) => Users.reload().then((res) => {
        if (!Users.me.data.is_supermanager)
          $state.go('contacts')
        return res
      }),
    }
  })
});
