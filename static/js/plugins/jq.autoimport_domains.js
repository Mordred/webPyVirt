(function($) {

    $.fn.autoimportDomains = function(options) {

        var defaults = {
            listUrl:            "/nodes/node/autoimport/list/",
            importUrl:          "/domains/domain/autoimport/",
            loadImg:            MEDIA_URL + "/img/icons/load-roller.gif",
            loader:             ".loader",
            secret:             "#secret"
        };

        var settings = $.extend(defaults, options);

        // Variables
        var canvas = null;
        var loader = null;
        var toImportCount = 0, toRemoveCount = 0;
        var globalActions = null;
        var dialog = null;
        var domains = {};

        var getDialog = function() {
            if (dialog == null) {
                var buttons = {};
                buttons[gettext("Close")] = function() { $(this).dialog("close"); };

                dialog = $("<div />").addClass("dialog").addClass("smaller").dialog({
                    modal:          true,
                    width:          500,
                    autoopen:       false,
                    buttons:        buttons
                });
            }
            return dialog;
        };

        var importDomainResponse = function(data) {
            if (data['status'] == 200) {
                var uuid = data['uuid'];
                var button = $(canvas).find("#import-" + uuid);
                var action = $(button).closest("td");
                button.fadeOut(500, function() {
                    button.remove();
                    action.css("color", "green").html(gettext("Imported"));
                });

                var show = function() {
                    getDialog().find(".import-status-" + uuid).html(gettext("OK")).css("color", "#00ee00");
                };

                getDialog().find(".import-load-" + uuid).fadeOut(500, show);

                delete domains[uuid];
                toImportCount--;

                if (toImportCount == 0) $("#import-all").fadeOut(500);
            } else if (data['status'] == 404) {
                var uuid = data['uuid'];
                var show = function() {
                    getDialog().find(".import-status-" + uuid).html(gettext("Failed")).css("color", "#ee0000");
                };
                getDialog().find(".import-load-" + uuid).fadeOut(500, show);
            }
        };

        var importDomainClick = function(domain) {
            getDialog()
                .dialog("option", "title", gettext("Import") + ": " + domain['name'])
                .dialog("option", "position", ["center", 80])
                .dialog("open")
                .html("");

            sendImportRequest(domain['uuid'])
        };

        var importAllDomainsClick = function() {
            getDialog()
                .dialog("option", "title", gettext("Import All Domains"))
                .dialog("option", "position", ["center", 80])
                .dialog("open")
                .html("");

            for (uuid in domains) {
                sendImportRequest(uuid);
            }
        };

        var sendImportRequest = function(uuid) {
            var domain = domains[uuid];
            $("<span />")
                .html(interpolate(gettext("Trying to import domain '<i>%s</i>'..."), [domain['name']]))
                .appendTo(getDialog());

            var loadImage = $("<img />").attr("src", settings['loadImg']).addClass("import-load-" + uuid);
            var status = $("<span />").addClass("import-status-" + uuid);

            $("<span />")
                .append("[&nbsp;")
                .append(loadImage)
                .append(status)
                .append("&nbsp;]")
                .addClass("status")
                .appendTo(getDialog());

            $("<br />").appendTo(getDialog());

            $.ajax({
                type:       "POST",
                url:        settings['importUrl'],
                data:       { "uuid": uuid },
                dataType:   "json",
                success:    function(data, textStatus) { importDomainResponse(data); }
            });
        };

        var createActions = function(uuid) {
            var actions = $("<div />");
            var domain = domains[uuid]
            var status = domain['status'];

            if (status == 0) {          // Domain not exist but it is in database
                toRemoveCount++;

                actions
                    .append(
                        $("<button />").html(gettext("Recreate")).attr("id", "recreate-" + uuid)
                        // TODO: Recreate domain
                    ).append(
                        $("<button />").html(gettext("Remove")).attr("id", "remove-" + uuid)
                        // TODO: Remove domain
                    );
            } else if (status == 1) {   // Domain not in database
                toImportCount++;

                actions
                    .append(
                        $("<button />").html(gettext("Import")).attr("id", "import-" + uuid)
                            .click(function(event) { importDomainClick(domain); })
                    );
            }

            return actions
        };

        var createAllActions = function() {
            if (globalActions == null)
                globalActions = $("<div />").addClass("right").css("padding", "10px 10px 0 0");

            if (toImportCount > 1)
                globalActions
                    .append(
                        $("<button />").html(gettext("Import All")).attr("id", "import-all")
                            .click(function(event) { importAllDomainsClick(); })
                        // TODO: Import all
                    )

            if (toRemoveCount > 1)
                globalActions
                    .append(
                        $("<button />").html(gettext("Recreate All")).attr("id", "recreate-all")
                        // TODO: Recreate all
                    ).append(
                        $("<button />").html(gettext("Remove All")).attr("id", "remove-all")
                        // TODO: Remove all
                    );

            canvas.append(globalActions);
        };

        var createDomainList = function(data, textStatus) {
             if (data['status'] == 200) {
                var table = $("<table />").addClass("white-stripe").addClass("w100p").addClass("smaller")
                    .append(
                        $("<tr />")
                            .append("<th>" + gettext("Domain Name") + "</th>")
                            .append("<th class=\"center\">" + gettext("UUID") + "</th>")
                            .append("<th class=\"center\">" + gettext("vCPU") + "</th>")
                            .append("<th class=\"center\">" + gettext("Memory") + "</th>")
                            .append("<th class=\"center\">" + gettext("Action") + "</th>")
                    ).css("display", "none");

                if (data['domains'].length == 0) {
                    table.append(
                        $("<tr />")
                            .append("<td class=\"center\" colspan=\"5\">"
                                + gettext("Nothing to import or remove!")
                                + "</td>")
                    );
                } else {
                    for (domain in data['domains']) {
                        var dom = data['domains'][domain];
                        domains[dom.uuid] = dom;
                        table.append(
                            $("<tr />").css("line-height", "2em")
                                .append("<td>" + dom['name'] + "</td>")
                                .append("<td class=\"center small\">" + dom['uuid'] + "</td>")
                                .append("<td class=\"center\">" + dom['vcpu'] + "</td>")
                                .append("<td class=\"center nowrap\">" + dom['memory'] + "</td>")
                                .append(
                                    $("<td />").addClass("center").addClass("w25p").append(createActions(dom.uuid))
                                )
                        );
                    }
                }

                canvas.append(table);
                table.fadeIn(500, createAllActions);
            } else if (data['status'] == 503) {
                var error = $("<div />").addClass("error").html(
                    "<h3>" + gettext("Error") + "</h3><br />" + data['statusMessage']
                );
                canvas.append(error);
                error.fadeIn(500);
            } else if (data['status'] == 501) {
                var error = $("<div />").addClass("message").html(
                    "<h3>" + gettext("Status") + "</h3><br />" + data['statusMessage']
                );
                canvas.append(error);
                error.fadeIn(500);
            }
        };

        var loadDomainList = function() {
            $.ajax({
                type:       "GET",
                url:        settings['listUrl'] + $(settings['secret']).val() + "/",
                dataType:   "json",
                success:    function(data, textStatus) {
                    loader.fadeOut(500, function() {
                        createDomainList(data, textStatus);
                    });
                }
            });
        };

        return this.each(function() {
            canvas = $(this);
            loader = $(this).find(settings['loader']);

            loadDomainList();
        });
    };

})(jQuery);

