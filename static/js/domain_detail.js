$(function() {
    $("#screenshot .button").tooltip().domainButton();
    $(".domain-status").checkDomainStatus({
        fireStatus: function(status) { $("#screenshot .button").domainButton("status", status); }
    });
});
