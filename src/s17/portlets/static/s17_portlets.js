(function ($) {

    $(document).ready(function() {
        $('a#wp_overlaytrigger').prepOverlay({
                subtype: 'ajax',
                config: {
                    onBeforeLoad : function (e) {
                        var input = $('#searchpersonform input[name=fullname]').attr('value');
                        $.ajax({
                            type: 'POST',
                            url: portal_url + '/@@whitepages?fullname=' + input,
                             success: function(data) {
                                $('.people-results').html(data);
                            }
                        });
                        return true;
                        }
                }
            });
        $('#searchpersonform .searchButton').click(function(event){
            if ($('#searchpersonform input[name=fullname]').attr('value').length === 0) {
                return false;
            }
            $('a#wp_overlaytrigger').click();
        });
        $('#searchpersonform input[name=fullname]').keydown(function(event){
            if(event.keyCode==13){
                if ($(this).attr('value').length === 0) {
                    return false;
                }
                $('a#wp_overlaytrigger').click();
                event.preventDefault();
            }
        });
    });

})(jQuery);
