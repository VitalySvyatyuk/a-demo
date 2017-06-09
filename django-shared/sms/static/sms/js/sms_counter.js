django.jQuery(function () {
    var dj = django.jQuery;
    var msg_count = 1;
    var msg_params = {
        'ascii': {
            'first': 160,
            'other': 153
        },
        'non-ascii': {
            'first': 70,
            'other': 67
        }
    };
    dj('#id_text').keyup(function(){
        var msg = dj(this).val();
        if(/^[\x00-\x7F]*$/.test(msg)){
            var encoding = 'ascii';
        }
        else{
            var encoding = 'non-ascii';
        }
        if(msg.length >= msg_params[encoding]['first']){
            msg_count = parseInt((msg.length/msg_params[encoding]['other'] + 0.5).toFixed());
        }else{
            msg_count = 1;
        }
        if(msg_count == 1){
            dj(this).parent().children('.help').html('Максимум 8 сообщений. Сообщений: 1. Символов: ' +
                msg.length + ' из' + msg_params[encoding]['first']); 
        }else if(msg_count <= 8){
            dj(this).parent().children('.help').html('Максимум 8 сообщений. Сообщений: ' + msg_count +
                '. Cимволов: ' + (msg.length - msg_params[encoding]['other']*(msg_count-1) ) + ' из '+msg_params[encoding]['other'])
        }else{
           dj(this).parent().children('.help').html('Максимум 8 сообщений. Превышен максимальный порог'); 
        }
    })
});