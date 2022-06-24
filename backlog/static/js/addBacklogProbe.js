
$('#backlogTable :input').change(function () {
    let statusIcon = $(this).parent().parent().children().eq(-2).children().first()

    statusIcon.first().removeClass('bi-bookmark').addClass('bi-bookmark-plus text-warning')
    statusIcon.attr("role", "button")


    statusIcon.click(uploadBacklogProbe)

})


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
            console.log('Sucesso no Probe do TA')
        },
        error: function(xhr, status) {
            statusIcon.removeClass('text-primary').addClass("text-warning");
            setTimeout( function () { statusIcon.click(uploadBacklogProbe) }, 1000)
        }
    })

}
