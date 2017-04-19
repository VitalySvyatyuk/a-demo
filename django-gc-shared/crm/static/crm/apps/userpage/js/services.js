CallService = function($http) {
    var self = this;
    self.query = function() {
        return $http.get(URL_CALLS_INDEX);
    };
};

app.service('Call', CallService);


VMCallService = function($http) {
    var self = this;
    self.query = function() {
        return $http.get(URL_VMCALLS_INDEX);
    };
};

app.service('VMCall', VMCallService);


LogService = function($http) {
    var self = this;
    self.query = function() {
        return $http.get(URL_LOGS_INDEX);
    };
};

app.service('Log', LogService);


DepositRequestService = function($http) {
    var self = this;
    self.query = function() {
        return $http.get(URL_DEPOSIT_REQUEST_INDEX);
    };
};

app.service('DepositRequest', DepositRequestService);

WithdrawRequestsService = function($http) {
    var self = this;
    self.query = function() {
        return $http.get(URL_WITHDRAW_REQUEST_INDEX);
    };
};

app.service('WithdrawRequests', WithdrawRequestsService);