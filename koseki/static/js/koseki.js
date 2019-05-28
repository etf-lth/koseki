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
})
})(jQuery);
