(function($){
$(document).ready(function(){
    $('.member_state_filter').change(function(e){
        $('#member_list tr').each(function(i){
            if ($('#member_state_' + $(this).data('state'))[0].checked) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
    $('.fee_registered_filter').change(function(e){
        $('#fees_list tr').each(function(i){
            if (Number($(this).data('registered').split('-')[0]) === new Date().getFullYear()) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
    $('.payment_registered_filter').change(function(e){
        $('#payments_list tr').each(function(i){
            if (Number($(this).data('registered').split('-')[0]) === new Date().getFullYear()) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });

    var balanceSortAsc = true;

    $('#balance_header').click(function(){
        var $rows = $('#member_list tr').get();

        if ($rows.length <= 1 && $($rows[0]).find('td[colspan]').length) {
            return;
        }

        $rows.sort(function(a, b){
            var balA = parseFloat($(a).data('balance')) || 0;
            var balB = parseFloat($(b).data('balance')) || 0;
            return balanceSortAsc ? (balA - balB) : (balB - balA);
        });

        var $tbody = $('#member_list');
        $.each($rows, function(i, row){
            $tbody.append(row);
        });

        balanceSortAsc = !balanceSortAsc;
        $('#balance_sort_icon').text(balanceSortAsc ? '▲' : '▼');
    });

})
})(jQuery);
