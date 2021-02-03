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
})
})(jQuery);
