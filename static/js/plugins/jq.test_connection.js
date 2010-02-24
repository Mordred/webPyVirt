(function($) {

    $.fn.testConnection = function(options) {

        var defaults = {
            url:                "/nodes/node/testConnection/",
            formTag:            "#frmAddNode",
            canvas:             "#testConnection",
            loadImage:          MEDIA_URL + "/img/icons/load-roller.gif"
        };

        var settings = $.extend(defaults, options);

        var loadImage   = null;
        var canvas      = null;
        var status      = null;

        var createURI = function(data) {

            var uri = "";

            // driver
            uri += data['driver'];
            
            // transport
            uri += data['transport'].length ? "+" + data['transport'] : "";

            // username
            uri += "://" + (data['username'].length ? data['username'] + "@" : "");
            
            // hostname
            uri += data['address'];

            // port
            uri += data['port'].length ?  ":" + data['port'] : "";

            // path
            uri += "/" + data['path']

            // extra parameters
            uri += data['extra_parameters'].length ? "?" + data['extra_parameters'] : "";

            return uri;
        };

        var responseSuccess = function(data, textStatus) {
            if (data['status'] == 400) {
                // Show that form is not valid!
                // Somehow JS validation failed
            } else if (data['status'] == 200) {
                if (data['success']) {

                    var show = function() {
                        status.html(gettext("OK")).css("color", "#00ee00");

                        $("<table />")
                            .append("<tr><td>" + gettext("CPU Model") 
                                + ":</td><td>" + data['info']['model'] + "</td></tr>")
                            .append("<tr><td>" + gettext("Memory Size") 
                                + ":</td><td>" + data['info']['memory'] + " MB</td></tr>")
                            .append("<tr><td>" + gettext("Active CPUs") 
                                + ":</td><td>" + data['info']['cpus'] + "</td></tr>")
                            .append("<tr><td>" + gettext("CPU frequency") 
                                + ":</td><td>" + data['info']['mhz'] + " MHz</td></tr>")
                            .append("<tr><td>" + gettext("NUMA Cells") 
                                + ":</td><td>" + data['info']['nodes'] + "</td></tr>")
                            .append("<tr><td>" + gettext("CPU socket per node") 
                                + ":</td><td>" + data['info']['sockets'] + "</td></tr>")
                            .append("<tr><td>" + gettext("Core per socket") 
                                + ":</td><td>" + data['info']['cores'] + "</td></tr>")
                            .append("<tr><td>" + gettext("Threads per core") 
                                + ":</td><td>" + data['info']['threads'] + "</td></tr>")
                            .hide()
                            .appendTo(canvas)
                            .slideDown(500);
                    };

                    loadImage.fadeOut(500, show);
                } else {

                    var show = function() {
                        status.html(gettext("Failed")).css("color", "#ee0000");

                        var errorMsg = $("<span />")
                            .append(gettext("Error message: "))
                            .append("\"" + data['error'] + "\"");

                        $("<div />")
                            .append(errorMsg)
                            .addClass("error")
                            .appendTo(canvas)
                            .slideDown(500);
                    };

                    loadImage.fadeOut(500, show);
                }
            }
        };

        var formToDict = function(form) {
            var form = form.serializeArray();

            var data = {};
            $.each(form, function(i, field) {
                data[field.name] = field.value;
            });

            return data;
        };

        var btnClick = function(event) {

            var data = formToDict($(settings.formTag));

            if (!validate(data)) return false;

            canvas.html("").hide().dialog("destroy");

            $("<span />")
                .html(interpolate(gettext("Connecting to '<i>%s</i>'..."), [createURI(data)]))
                .appendTo(canvas);

            loadImage = $("<img />").attr("src", settings.loadImage);
            status = $("<span />")

            $("<span />")
                .append("[&nbsp;")
                .append(loadImage)
                .append(status)
                .append("&nbsp;]")
                .addClass("status")
                .appendTo(canvas);


            buttons = {}
            buttons[gettext("Close")] = function() { $(this).dialog("close") };

            canvas.dialog({
                modal:          true,
                width:          500,
                autoOpen:       false,
                title:          gettext("Connection Test"),
                position:       ["center", 80],
                buttons:        buttons
                
            });
            canvas.dialog("open");

            $.ajax({
                type:       "POST",
                url:        settings.url,
                data:       $(settings.formTag).serialize(),
                dataType:   "json",
                success:    responseSuccess,
            });

            return false;
        };

        var validate = function(data) {
            var valid = true;

            if (data['name'].length != 0) {
                var field = $(settings.formTag).find(":input[name='name']").parent();
                field.removeClass("field-error");

                field.find(".errorlist").remove();
            }

            if (data['driver'].length == 0) {
                var field = $(settings.formTag).find(":input[name='driver']").parent();
                field.addClass("field-error");

                valid = false;
            } else {
                var field = $(settings.formTag).find(":input[name='driver']").parent();
                field.removeClass("field-error");

                field.find(".errorlist").remove();
            }

            if (data['port'].length != 0) {
                var isNumber = true;
                for (var i = 0; i < data['port'].length; i++) {
                    if (data['port'].charAt(i) < "0" || data['port'].charAt(i) > "9") {
                        isNumber = false;
                        break;
                    }
                }

                if (!isNumber) {
                    var field = $(settings.formTag).find(":input[name='port']").parent();
                    field.addClass("field-error");

                    valid = false;
                } else {
                    var field = $(settings.formTag).find(":input[name='port']").parent();
                    field.removeClass("field-error");

                    field.find(".errorlist").remove();
                }
            } else {
                var field = $(settings.formTag).find(":input[name='port']").parent();
                field.removeClass("field-error");

                field.find(".errorlist").remove();
            }

            if (valid)
                $(settings.formTag).find("div.errornote").slideUp(500);

            return valid;
        };


        return this.each(function() {
            canvas = $(settings.canvas);

            $(this).click(btnClick);
        });
    };

})(jQuery);

