
payForm = {
    
    validators: {
        
        name: function(v, char) {
            var maxlength = 31;
            if(char) {
                if(v.length>maxlength) return false;
                return /^[a-zA-Z ]{0,}$/.test(v);
            }
            return /^[a-zA-Z ]{3,31}$/.test(v);
        },
        cvc: function(v, char) {
            var maxlength = 3;
            if(char) {
                if(v.length>maxlength) return false;
                return /^[0-9]{0,}$/.test(v); 
            }
            return /^[0-9]{3}$/.test(v);
        }
    },

    cardType: function(t) {
        $('.icon').removeClass('active');
        $('.'+t).addClass('active');
    },

    buildFullCCNumber: function() {
        return $("#cc1").val() + $("#cc2").val() + $("#cc3").val() + $("#cc4").val();
    },

    submit: function(e) {
        e.preventDefault();
        var inp,
            params = {};
        var validated = true;
        $('input, select').each(function() {
            if(this.id != null) {
                params[this.id] = $(this).val();

                if(params[this.id] == '') {
                    alert(get_string('required'));
                    $(this).focus();
                    validated = false;
                    return false;
                }

                if(payForm.validators[this.id] != null && !payForm.validators[this.id](params[this.id])) {
                    alert(get_string('incorrect_value'));
                    $(this).focus();
                    validated = false;
                    return false;
                }

            }
        });

        if (!validated) {
            return false;
        }

        $("body").css("cursor", "wait");
        
        if (!window.location.origin) 
        {
        	 window.location.origin = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
        }
        //KR: set cc data 
        var host = window.location.origin;  //"http://localhost:8080";

        //var host = "https://devtest.wirecapital.com";
        
        var txID = paymentExecuteRequest.txId;
        var returnUrl = merchantReturnUrl;
        if(returnUrl ==null || returnUrl.trim()=="")
        {
        	returnUrl = host+"/FE/Error.jsp";
        }
        
        var token = paymentExecuteRequest.authToken;
        var cc = {};
        //cc.ccNumber =  $("#ccnum").find("span").html();
        cc.cardHolderName = $("#name").val();
        cc.ccNumber = payForm.buildFullCCNumber();
        cc.cvv = $("#cvc").val();
        cc.expirationMonth = $("#month").val();
        cc.expirationYear = $("#year").val();
        //var expDate=new Date();
        //expDate.setFullYear(parseInt(yyyy),parseInt(mm)-1,1);
        paymentExecuteRequest.cc = cc;
        
        function redirect(url)
        {
        	$("body").css("cursor", "auto");
        	window.location = url;
        }

        
        var resultCheckCounter = 60; 
        function result(txID)
		{
        	var resultRequest = {};
        	resultRequest.txId = txID;
        	resultRequest.authToken = token;
        	var resultRequestJson = JSON.stringify(resultRequest);
        	//console.log("Payment status check request:"+resultRequestJson);
 			$.ajax({
			    url: host+"/FE/rest/tx/status",
			    type: "POST",
			    data: resultRequestJson,
			    dataType: "json",
			    contentType:"application/json",
			    beforeSend: function(x) {
			      if (x && x.overrideMimeType) {
			        x.overrideMimeType("application/json;charset=UTF-8");
			      }
			    },
			    success: function(data, textStatus, jqXHR) {
			    	//console.log("Payment status check response:"+JSON.stringify(data));
			    	resultCheckCounter--;
			        if(data.result.code=='1' || data.result.code=='2')
			      	{
			        	//1:complete 2:pending
			        	var msg = "Transaction Id:"+txID+"\nResult Code:"+data.result.code+" \nMessage:"+data.result.message;
						//console.log(msg);
						//alert(msg);
						redirect(data.returnUrl);
			      	}
			      	else if( data.result.code=='0' || data.result.code=='5')
			  		{
			      		//failed.
			      		msg = "Transaction Id:"+txID+"\nResult Code:"+data.result.code+"\nMessage:"+data.result.message+"\nErrorId:"+data.result.errorId;
						//console.log(msg);
						//alert(msg);
						if(data.returnUrl==null || data.returnUrl.trim()=="")
						{
							data.returnUrl = returnUrl+"txId="+txID+"&resultCode="+data.result.code+"&message="+encodeURI(data.result.message)
							+"&errorId="+data.result.errorId;
						}
						redirect(data.returnUrl);
			  		}
			      	else if( data.result.code =='-2' )
		      		{
			      		//Card is 3D enrolled. Redirect to url for 3D authentication.
			      		msg = "Transaction Id:"+txID+"\nResult Code:"+data.result.code+" \nMessage:"+data.result.message;
						//console.log(msg);
						//alert(msg);
						//txFail(txID,orderId,data.cancelUrl);
						redirect(data.auth3DUrl);
		      		}
			      	else if( data.result.code =='4' )
		      		{
			      		//cancelled by user.
			      		msg = "Transaction Id:"+txID+"\nResult Code:"+data.result.code+" \nMessage:"+data.result.message;
						//console.log(msg);
						//alert(msg);
						redirect(data.cancelUrl);
		      		}
			  		else 
					{
			  			if(resultCheckCounter==0)
		  				{
			  				msg = "Transaction Result Check Timeout.\n Transaction Id:"+txID;
							//console.log();
							//alert(msg);
 						    returnUrl += "txId="+txID+"&resultCode=2"+"&message="+encodeURI("Transaction is Pending.Transaction result check timeout.")+"&advice="+encodeURI("Call query service to get result.");
							redirect(returnUrl);	
							return;
		  				}
			  			//console.log("Transaction is in process. Status:"+data.txStatusId);
			  			setTimeout(function() {
			  				result(txID);
			  			},1000);
					}

			    },
			    error: function(jqXHR, textStatus, errorThrown)
			    {
		        	  //console.log("Transaction Error["+textStatus+"]. Result Check Request["+resultRequestJson+"]");
		        	  //alert("Transaction failed.");
					  returnUrl += "txId="+txID+"&resultCode=0"+"&message="+encodeURI("Transaction failed.Failed to check status.");
					  redirect(returnUrl);
			    }
			});
		}

 		var payExecTxRequestJson = JSON.stringify(paymentExecuteRequest);
      	//console.log("Payment execute request:"+payExecTxRequestJson);
		$.ajax({
	          url: host+"/FE/rest/tx/payment/execute",
	          type: "POST",
	          data: payExecTxRequestJson,
	          dataType: "json",
		      contentType:"application/json",
	          beforeSend: function(x) {
	            if (x && x.overrideMimeType) {
	              x.overrideMimeType("application/json;charset=UTF-8");
	            }
	          },
	          success: function(data, textStatus, jqXHR) {
	           		//console.log("Payment execute response:"+JSON.stringify(data));

		      	    requestId = data.requestId;
		    	  	orderId = data.orderId;
		    	  	amount = data.amount;
		    	  	currencyCode = data.currencyCode;
		    	  	
			        if( data.result.code=='0' || data.result.code=='5')
			  		{
			      		//Failed.
			      		msg = "Transaction Id:"+txID+"\nResult Code:"+data.result.code+"\nMessage:"+data.result.message+"\nErrorId:"+data.result.errorId;
						//console.log(msg);
						//alert(msg);
						if(data.returnUrl ==null || data.returnUrl.trim()=="")
						{
							data.returnUrl = returnUrl + "txId="+txID+"&resultCode="+data.result.code+"&message="+encodeURI(data.result.message)
							+"&errorId="+data.result.errorId;
						}
						redirect(data.returnUrl);
			  		}
			  		else
					{
			  			//console.log("Transaction is in process...");
			  			setTimeout(function() {
			  				result(data.txId);
			  			},1000);
					}

	          },
	          error: function(jqXHR, textStatus, errorThrown)
	          {
	        	 //console.log("Transaction Error["+textStatus+"]. Execute Request["+payExecTxRequestJson+"]");
	        	 //alert("Transaction failed.");
				 returnUrl += "txId="+txID+"&resultCode=0"+"&message="+encodeURI("Transaction failed.Failed to execute payment request.");
				 redirect(returnUrl);
	          }
		});

        return false;
    },
    
    validate: function(el, validator) {
        if(el.goodval == null) el.goodval='';
        if(validator(el.value, true)) 
        	el.goodval=el.value;
        else el.value=el.goodval;
        
        if(validator(el.value, false)) 
        	{
        	if(el.parentNode!=null)
        	el.parentNode.className = '';
        	}
        else 
        	{
        	if(el.parentNode!=null)
        	el.parentNode.className = 'valid-err';
        	}
    }
};


$(document).ready(function() {
    
    $('form').submit(payForm.submit);

});