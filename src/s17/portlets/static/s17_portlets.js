(function($) {

    $(document).ready(function() {

        var trigger = $('dl.portletWhitePagesPortlet a.overlay-trigger');
        if (trigger.length > 0) {
            trigger.prepOverlay({
                subtype: 'ajax',
                config: {
                    onBeforeLoad: function(event) {
                        var input = $('#searchpersonform input[name=fullname]').attr('value');
                        $.ajax({
                            type: 'POST',
                            url: portal_url + '/@@whitepages?fullname=' + input,
                             success: function(data) {
                                if($('.searchResults').length>0){
                                    $('.searchResults').html(data);
                                } else{
                                    $('.pb-ajax > div > div').html(data);
                                }
                            }
                        });
                        return true;
                        }
                }
            });
        }

        var sel = $('#searchpersonform .searchButton');
        if (sel.length > 0) {
            sel.click(function(event) {
                if ($('#searchpersonform input[name=fullname]').attr('value').length === 0) {
                    return false;
                }
                trigger.click();
                event.preventDefault();
                return false;
            });
        }

        var sel = $('#searchpersonform input[name=fullname]');
        if (sel.length > 0) {
            sel.keydown(function(event) {
                if (event.keyCode == 13){
                    if ($(this).attr('value').length === 0) {
                        return false;
                    }
                    trigger.click();
                    event.preventDefault();
                }
            });
        }
    });

})(jQuery);
