(function($) {

    $.fn.gauge = function(options) {

        PLUGIN_NAME = "gauge";

        // Options
        var defaults = {
            url:            "/domains/domain/statistics/",
            id:             null,
            name:           "Unknown",
            type:           null,
            update:         3000,
            gaugeOptions:   {
                width:      150,
                height:     150,
                redFrom:    90,
                redTo:      100,
                yellowFrom: 70,
                yellowTo:   90,
                minorTicks: 5
            }
        }

        var settings = $.extend(defaults, options);

        var dataTable = null;
        var chart = null;
        var element = null;
        var timeout = null;

        var responseSuccess = function(data, textStatus) {
            if (data['status'] == 200) {
                dataTable.setValue(0, 1, parseFloat(data['data']));
                chart.draw(dataTable, settings['gaugeOptions']);

                timeout = setTimeout(updateRequest, settings['update']);
            }

        };

        var updateRequest = function() {
            $.ajax({
                type:           "POST",
                url:            settings['url'],
                data:           { "domainId": settings['id'], "visualization": "gauge" },
                dataType:       "json",
                success:        responseSuccess
            });
        };

        return this.each(function() {
            element = this;

            dataTable = new google.visualization.DataTable();
            dataTable.addColumn("string", gettext("Label"));
            dataTable.addColumn("number", gettext("Value"));
            dataTable.addRows(1);
            dataTable.setValue(0, 0, settings['name']);
            dataTable.setValue(0, 1, 0);

            chart = new google.visualization.Gauge(this);
            chart.draw(dataTable, settings['gaugeOptions']);

            updateRequest();
        });
    }

    $.fn.areaChart = function(options) {

        PLUGIN_NAME = "areaChart";

        // Options
        var defaults = {
            url:                "/domains/domain/statistics/",
            id:                 null,
            type:               null,
            update:             3000,
            limit:              20,
            areaChartOptions:   {
                width:              600,
                height:             120,
                title:              "",
                backgroundColor:    "#eeeeee"
            }
        }

        var settings = $.extend(defaults, options);

        var dataTable = null;
        var chart = null;
        var element = null;
        var lastId = 0;
        var timeout = null;

        var responseSuccess = function(data, textStatus) {
            if (data['status'] == 200) {
                for (var i = 0; i < data['data'].length; i++) {
                    var item = data['data'][i];
                    var value = parseFloat(item['value']);
                    dataTable.addRow(["", value]);
                    if (dataTable.getNumberOfRows() >= settings['limit'])
                        dataTable.removeRow(0);
                }
                if (data['data'].length != 0)
                    lastId = data['data'][0]['id'];
                chart.draw(dataTable, settings['areaChartOptions']);

                timeout = setTimeout(updateRequest, settings['update']);
            }
        };

        var updateRequest = function() {
            $.ajax({
                type:           "POST",
                url:            settings['url'],
                data:           { "domainId": settings['id'], "visualization": "areaChart", "lastId": lastId },
                dataType:       "json",
                success:        responseSuccess
            });
        };

        return this.each(function() {
            element = this;

            dataTable = new google.visualization.DataTable();
            dataTable.addColumn("string", gettext("Time"));
            dataTable.addColumn("number", gettext("Usage"));

            chart = new google.visualization.AreaChart(this);
            chart.draw(dataTable, settings['areaChartOptions']);

            updateRequest();
        });
    }

})(jQuery);
