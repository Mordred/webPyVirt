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
            } else if (data['status'] == 503) {
                var tempTable = new google.visualization.DataTable();
                tempTable = new google.visualization.DataTable();
                tempTable.addColumn("string", gettext("Label"));
                tempTable.addColumn("number", gettext("Value"));
                tempTable.addRows(1);
                tempTable.setValue(0, 0, settings['name']);
                tempTable.setValue(0, 1, NaN);
                chart.draw(tempTable, settings['gaugeOptions']);

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

        var createTimeString = function(timestamp) {
            var time = new Date();
            time.setTime(timestamp * 1000);
            var h = time.getHours();
            var m = time.getMinutes();
            var s = time.getSeconds();
            var ret = "" + (h < 10 ? "0" + h : h)
                + ":" + (m < 10 ? "0" + m : m)
                + ":" + (s < 10 ? "0" + s : s);
            return ret;
        };

        var responseSuccess = function(data, textStatus) {
            if (data['status'] == 200) {
                if (data['data'].length != 0) {
                    lastId = data['data'][0]['id'];
                }

                for (var i = data['data'].length - 1; i >= 0; i--) {
                    var item = data['data'][i];
                    var value = parseFloat(item['value']);

                    var time = createTimeString(item['time']);
                    dataTable.addRow([time, value]);
                    if (dataTable.getNumberOfRows() >= settings['limit'])
                        dataTable.removeRow(0);
                }

                chart.draw(dataTable, settings['areaChartOptions']);

                timeout = setTimeout(updateRequest, settings['update']);
            } else if (data['status'] == 503) {
                var tempTable = new google.visualization.DataTable();
                tempTable.addColumn("string", gettext("Time"));
                tempTable.addColumn("number", gettext("Usage"));
                chart.draw(tempTable, settings['areaChartOptions']);

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
