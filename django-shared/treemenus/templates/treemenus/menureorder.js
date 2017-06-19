$(function () {
    $('ul.menu').sortable({
        update: function () {
            var menu = $(this);
            var parent_menu_id = /\d+/.exec(menu.attr('id')).pop();
            var order = [];
            menu.children().each(function () {
                var child_id = /\d+/.exec($(this).attr('id')).pop();
                order.push(child_id);
            });
            $('<div>Вы уверены что хотите отсортировать меню?</div>').dialog({
                resizable: false,
                height:140,
                modal: true,
                buttons: {
                    "Да": function() {
                        $.ajax({
                            url: TREEMENUS_REORDER_URL + '?parent='+parent_menu_id+'&order='+order.join(','),
                            error: function () {
                                alert('Ошибка при сортировке менюшек.');
                            }
                        });
                        $( this ).dialog( "close" );
                    },
                    Cancel: function() {
                        $( this ).dialog( "close" );
                    }
                }
            });
        }
    })
})