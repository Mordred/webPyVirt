function googleGauge() {
    // CPU
    $("#gauge_cpu").gauge({
        url:            "/domains/domain/statistics/cpu/",
        id:             $("#domainId").val(),
        name:           gettext("CPU")
    });
    $("#area_chart_cpu").areaChart({
        url:                "/domains/domain/statistics/cpu/",
        id:                 $("#domainId").val(),
        areaChartOptions:   {
            width:                  550,
            height:                 200,
            title:                  gettext("CPU"),
            titleY:                 gettext("%"),
            titleFontSize:          12,
            backgroundColor:        "#eeeeee",
            legendBackgroundColor:  "#eeeeee",
            max:                    100,
            min:                    0
        }
    });

    // Memory
    $("#gauge_memory").gauge({
        url:            "/domains/domain/statistics/memory/",
        id:             $("#domainId").val(),
        name:           gettext("Memory")
    });
    $("#area_chart_memory").areaChart({
        url:            "/domains/domain/statistics/memory/",
        id:             $("#domainId").val(),
        areaChartOptions:   {
            width:                  550,
            height:                 200,
            title:                  gettext("Memory"),
            titleY:                 gettext("%"),
            titleFontSize:          12,
            backgroundColor:        "#eeeeee",
            legendBackgroundColor:  "#eeeeee",
            max:                    100,
            min:                    0
        }
    });
}

google.load("visualization", "1", { packages: ['gauge', 'areachart' ]});
google.setOnLoadCallback(googleGauge);

// On DOM Ready
$(function() {
    $("#screenshot .button").tooltip().domainButton();
    $(".domain-status").checkDomainStatus({
        fireStatus: function(status) { $("#screenshot .button").domainButton("status", status); }
    });
});
