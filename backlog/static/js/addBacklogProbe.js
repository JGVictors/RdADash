
$('#backlogTable :input').change(function () {
    let statusIcon = $(this).parent().parent().children().eq(-2).children().first()

    statusIcon.first().removeClass('bi-bookmark').addClass('bi-bookmark-plus text-warning')
    statusIcon.attr("role", "button")


    statusIcon.click(uploadBacklogProbe)

})

$('.ticket-just-refresh').click(refreshProbe)

function uploadBacklogProbe() {
    let statusIcon = $(this)

    statusIcon.click(false)
    statusIcon.removeAttr("role")

    let probeInput = statusIcon.parent().parent().children().eq(-3).children().first()
    let ticket = statusIcon.parent().parent().children().first().text()

    $.ajax({
        url: window.location.pathname + '/probe/' + ticket,
        method: "POST",
        data: { probe: probeInput.val() },
        datatype: "JSON",
        beforeSend: function() {
            statusIcon.removeClass('text-warning').addClass('text-primary')
        },
        success: function(r){
            statusIcon.removeClass('bi-bookmark-plus text-primary').addClass('bi-bookmark')
        },
        error: function(xhr, status) {
            statusIcon.removeClass('text-primary').addClass("text-warning");
            setTimeout( function () { statusIcon.click(uploadBacklogProbe) }, 1000)
        }
    })

}

function refreshProbe() {
    let refreshIcon = $(this) 

    refreshIcon.click(() => {})
    refreshIcon.removeAttr("role")

    refreshIcon.addClass('text-warning')

    let probeInput = refreshIcon.parent().parent().children().eq(-3).children().first()
    let analistaTd = refreshIcon.parent().parent().children().last()
    let ticket = refreshIcon.parent().parent().children().first().text()

    $.ajax({
        url: window.location.pathname + '/get_ticket_probe/' + ticket,
        method: "POST",
        data: { probe: probeInput.val() },
        datatype: "JSON",
        beforeSend: function() {
            refreshIcon.removeClass('text-warning text-danger').addClass('text-primary')
        },
        success: function(r){
            refreshIcon.removeClass('text-primary')
            probeInput.val(r['probe'])
            analistaTd.text(r['prober_username'])
        },
        error: function(xhr, status) {
            refreshIcon.removeClass('text-primary')
            if (xhr.status != 404) refreshIcon.addClass('text-danger');
            setTimeout( function () { refreshIcon.click(refreshProbe) }, 5000)
        }
    })


}