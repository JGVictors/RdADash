avaliableProbes = [
    "Raiz Aguardando Atuação (Fora do Prazo)",
    "Raiz Aguardando Atuação (Esperado)",
    "TA na Responsabilidade da Automação",
    "TA no Fluxo SONAR",
    "TA em Atuação",
    "Raiz em Atuação",
    "TA em Escalonamento",
    "Raiz em Escalonamento",
    "TA Tramitação Indevida",
    "Raiz Tramitação Indevida",
    "TA Encerrado por Normalização",
    "Raiz Encerrado por Normalização"
]

$('#backlogTable :input').autocomplete({ source: avaliableProbes })

$('#backlogTable :input').change(function() {
    let probeInput = $(this)
    let statusIcon = probeInput.parent().parent().children().eq(-2).children().first()

    probeInput.addClass('bg-warning')
    statusIcon.removeClass('bi-bookmark').addClass('bi-bookmark-plus text-warning')
    statusIcon.attr('role', 'button')

    statusIcon.click(uploadProbe)
})

$('.ticket-just-refresh').click(refreshProbe)

function uploadProbe() {
    let statusIcon = $(this)
    let row = statusIcon.parent().parent()
    let probeInput = row.children().eq(-3).children().first()
    let analistaTd = row.children().last()

    disableProbeActions(row)
    
    $.ajax({
        url: window.location.pathname + '/probe/' + row.children().first().text(),
        method: 'POST',
        data: { probe: probeInput.val() },
        datatype: 'JSON',
        beforeSend: () => {
            statusIcon.addClass('text-primary')
            probeInput.addClass('bg-primary')
        },
        success: (r) => { 
            statusIcon.removeClass('text-danger')
            analistaTd.text(r['prober_username'])
        },
        error: (xhr, status) => {
            statusIcon.addClass('text-danger');
            probeInput.addClass('bg-warning')
        },
        complete: () => { enableProbeActions(row) }
    })

}

function refreshProbe() {
    let refreshIcon = $(this) 
    let row = refreshIcon.parent().parent()
    let probeInput = row.children().eq(-3).children().first()
    let analistaTd = row.children().last()

    disableProbeActions(row)

    refreshIcon.addClass('text-warning')

    $.ajax({
        url: window.location.pathname + '/get_ticket_probe/' + row.children().first().text(),
        method: 'POST',
        data: { probe: probeInput.val() },
        datatype: 'JSON',
        beforeSend: () => { refreshIcon.removeClass('text-danger').addClass('text-primary') },
        success: (r) => {
            probeInput.val(r['probe'])
            analistaTd.text(r['prober_username'])
        },
        error: (xhr) => { if (xhr.status != 404) refreshIcon.addClass('text-danger') },
        complete: () => { enableProbeActions(row) }
    })

}

function disableProbeActions(row) {
    let icons = row.children().eq(-2).children()
    for (i=0; i < icons.length; i++) {
        icon = $(icons[i])
        icon.off('click')
        icon.removeAttr('role')
        icon.addClass('opacity-50 text-muted')
    }
    let probeInput = row.children().eq(-3).children().first()
    probeInput.addClass('bg-muted')
    probeInput.prop('disabled', 'true')
}

function enableProbeActions(row) {
    let icons = row.children().eq(-2).children()
    for (i=0; i < icons.length; i++) {
        icon = $(icons[i])
        icon.removeClass('opacity-50 text-muted text-primary text-warning')
        setTimeout(() => { icon.attr('role', 'button') }, 3000)
    }
    $(icons[0]).removeClass('bi-bookmark-plus').addClass('bi-bookmark')
    setTimeout(() => { $(icons[1]).click(refreshProbe) }, 3000)
    let probeInput = row.children().eq(-3).children().first()
    probeInput.removeClass('bg-muted bg-warning bg-primary')
    if ($('#userCanOnlyView').val() == '') probeInput.removeAttr('disabled')
}