(function($) {

    $.fn.checkNodeStatus = function(options) {

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

    $.fn.checkDomainStatus = function(options) {

        var PLUGIN_NAME = "checkDomainStatus";

        var defaults = {
            url:                "/domains/domain/checkStatus/",
            updateTime:         30000
        };

        var settings = $.extend(defaults, options);

        var responseSuccess = function(data, domain) {
            var loader = domain.data(PLUGIN_NAME + ".loader");
            var canvas = domain.data(PLUGIN_NAME + ".canvas");

            if (data['status'] == 200) {

                var oldStatus = canvas.html();

                loader.fadeOut(500, function() {
                    if (oldStatus != data['domain']['status']) {
                        canvas.fadeOut(500, function() {
                            canvas.html(data['domain']['status']);
                            canvas.fadeIn(500);
                        });
                    }
                });

            } else if (data['status'] == 503) {

                var oldStatus = canvas.html();
                var newStatus = "<span class=\"error\">" + data['statusMessage'] + "</span>";

                loader.fadeOut(500, function() {
                    if (oldStatus != newStatus) {
                        canvas.fadeOut(500, function() {
                            canvas.html(newStatus);
                            canvas.fadeIn(500);
                        });
                    }
                });
            }
            var timeout = setTimeout(function() { 
                    sendRequest(domain, loader, canvas); 
                }, settings['updateTime']);
            $(domain).data(PLUGIN_NAME + ".timeout", timeout);
        }

        var sendRequest = function(domain) {
            var loader = domain.data(PLUGIN_NAME + ".loader");
            var canvas = domain.data(PLUGIN_NAME + ".canvas");

            var domId = domain.val();

            $.ajax({
                type:       "GET",
                url:        settings['url'] + domId + "/",
                dataType:   "json",
                success:    function(data, textStatus) { responseSuccess(data, domain); }
            });
        }

        var fireEvent = function(element, event) {
            switch (event) {
                case "stop":
                    clearTimeout(element.data(PLUGIN_NAME + ".timeout"));
                    element.removeData(PLUGIN_NAME + ".timeout");
                    break;
                case "restart":
                    fireEvent(element, "stop");
                    sendRequest(element);
                    break;
            }
        };

        var create = function(element) {
            var loader = element.siblings(".loader");
            var canvas = $("<span />");
            element.parent().append(canvas);

            element.data(PLUGIN_NAME + ".loader", loader);
            element.data(PLUGIN_NAME + ".canvas", canvas);

            canvas.fadeOut(500, function() {
                loader.fadeIn(500, function() {
                    sendRequest(element);
                })
            });

        };

        return this.each(function() {

            if (typeof options === "string") {
                fireEvent($(this), options);
            } else {
                create($(this));
            }
        });
    };

})(jQuery);

