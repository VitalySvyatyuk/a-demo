angular.module('FrontPage', [])
.controller('MarketDepthController', function($scope, $timeout) {
    $scope.bid = $scope.previousBid = 1.12446
    $scope.ask = $scope.previousAsk = 1.12452
    
    function randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    var quoteDiff = 0.00001
    function getQuoteDiff() {
        var diffSign = (-1 * randomInt(0, 2)) + 1
        return quoteDiff * diffSign
    }

    function randomInterval(func, minT, maxT) {
        $timeout(function() {
            func.call()
            randomInterval(func, minT, maxT)
        }, randomInt(minT, maxT))
    }
    
    function simulateChange(quote) {
        quote = parseFloat(quote) + getQuoteDiff()
        return quote.toFixed(5)
    }

    function simulateChangeDeal(deal, prev, next) {
        deal = parseFloat(deal)
        dealN = deal + getQuoteDiff()
        if (dealN < parseFloat(next) && dealN > parseFloat(prev)) {
            return dealN.toFixed(5)
        }
        return deal.toFixed(5)
    }

    function closestDivisibleBy(number, n) {
        return Math.round(number / n) * n
    }

    function getLowestDealPoint() {
        var tail = closestDivisibleBy(randomInt(0, 100), 5) / 100
        return randomInt(32, 45) + tail
    }

    function changeLowestDealTail(deal) {
        deal = parseFloat(deal)
        var sign = (-1 * randomInt(0, 2)) + 1
        var tail = closestDivisibleBy(randomInt(0, 100), 5) / 100
        return (deal + (tail * sign)).toFixed(2)
    }
    
    function reduceDeals(initialPrice, sign) {
        return function(arr, deal, i) {
            var price = arr[i-1] ? arr[i-1].price : initialPrice
            price = parseFloat(price)
            price = price + (i * quoteDiff * randomInt(1, 3)) * sign
            obj = {
                price: price.toFixed(5),
                deal: deal
            }
            if (i > 0 && i < 5) {
                obj.hide = !randomInt(0,1)
            }
            arr.push(obj)
            return arr
        }
    }

    function getDealPoints() {
        return [0.2, 0.4, 0.5, 0.9, 4, 5, 20, getLowestDealPoint()]
    }

    $scope.bidDeals = getDealPoints().reduce(reduceDeals($scope.bid, -1), [])
    $scope.askDeals = getDealPoints().reduce(reduceDeals($scope.ask, 1), [])
    
    randomInterval(function() {
        $scope.previousBid = $scope.bid
        $scope.bid = simulateChange($scope.bid)
        $scope.bidDeals[0].price = $scope.bid
    }, 100, 1000)

    randomInterval(function() {
        $scope.previousAsk = $scope.ask
        $scope.ask = simulateChange($scope.ask)
        $scope.askDeals[0].price = $scope.ask
    }, 100, 1000)

    randomInterval(function() {
        $scope.bidDeals[randomInt(1,5)].hide = !randomInt(0,1)
    }, 800, 4000)

    randomInterval(function() {
        $scope.askDeals[randomInt(1,4)].hide = !randomInt(0,1)
    }, 500, 3000)

    randomInterval(function() {
        var toChange = randomInt(1,6)
        $scope.bidDeals[toChange].price = simulateChangeDeal(
            $scope.bidDeals[toChange].price,
            $scope.bidDeals[toChange+1].price,
            $scope.bidDeals[toChange-1].price
        )
    }, 50, 1000)

    randomInterval(function() {
        var toChange = randomInt(1,6)
        $scope.askDeals[toChange].price = simulateChangeDeal(
            $scope.askDeals[toChange].price,
            $scope.askDeals[toChange-1].price,
            $scope.askDeals[toChange+1].price
        )
    }, 50, 1000)

    randomInterval(function() {
        $scope.askDeals[$scope.askDeals.length-1].deal = changeLowestDealTail(
            $scope.askDeals[$scope.askDeals.length-1].deal)
    }, 400, 2000)

    randomInterval(function() {
        $scope.bidDeals[$scope.bidDeals.length-1].deal = changeLowestDealTail(
            $scope.bidDeals[$scope.bidDeals.length-1].deal)
    }, 400, 2000)

});