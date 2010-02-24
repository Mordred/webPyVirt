(function($) {

    $.fn.checkStatus = function(options) {

        var defaults = {
            url:                "/nodes/node/checkStatus/",
            canvasPrefix:       "node_status_",
            buttonPrefix:       "node_"
        };

        var settings = $.extend(defaults, options);

        var responseSuccess = function(data, textStatus, nodeId) {
            if (data['status'] == 200) {
                var messageText = null;
                var canvas = $("#" + settings['canvasPrefix'] + nodeId);
                var span = canvas.find("span.message");

                if (data['node']['status']) {
                    span.html(gettext("running")).css("color", "#008800");
                } else {
                    span.html(gettext("cannot connect")).css("color", "#880000");
                }

                canvas.find("img.loader").fadeOut(500, function() { span.fadeIn(500); } );
            }
        }

        var btnClick = function(event) {
            var thisId = $(this).attr("id");
            var nodeId = thisId.replace(settings['buttonPrefix'], "");

            var canvas = $("#" + settings['canvasPrefix'] + nodeId);
            canvas.find("span.message").fadeOut(500, function() {
                canvas.find("img.loader").fadeIn(500, function() {
                    $.ajax({
                        type:       "GET",
                        url:        settings['url'] + nodeId + "/",
                        dataType:   "json",
                        success:    function(data, textStatus) { responseSuccess(data, textStatus, nodeId); }
                    });
                })
            });

        }

        return this.each(function() {

            // Click event
            $(this).click(btnClick);
            $(this).click();
        });
    };

})(jQuery);

