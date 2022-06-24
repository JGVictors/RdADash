$('#uploadBacklog').submit(function (e) {
    e.preventDefault();

    let formData = new FormData()
    formData.append('file', $('#fileBacklog')[0].files[0])

    $.ajax({
        url: "/backlog/upload",
        method: "POST",
        data: formData,
        contentType: false,
        processData: false,
        beforeSend: function() {
            $('#uploadBacklog').children().children().prop('disabled', true);
            $("#uploadBacklogProgress").text("");
            $("#uploadBacklogProgress").removeClass("bg-success");
            $("#uploadBacklogProgress").removeClass("bg-warning");
        },
        xhr: function() {
            let xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener("progress", function(evt) {
                let pct = Math.floor((evt.loaded / evt.total) * 100);
                $("#uploadBacklogProgress").width(pct + "%");
                if (evt.loaded = evt.total) $("#uploadBacklogProgress").text("Processando...");
            }, false);
           return xhr;
        },
        success: function(r) {
            $("#uploadBacklogProgress").addClass("bg-success");
            setTimeout( function () {
                $("#uploadBacklogProgress").text("Backlog importado com sucesso! Atualizando pagina em 5 segundos...");
                setTimeout( function() { location.reload() }, 4000);
            }, 1000)
        },
        error: function(xhr, status) {
            $("#uploadBacklogProgress").addClass("bg-warning");
            setTimeout( function () {
                $("#uploadBacklogProgress").text("Tente Novamente (Error " + xhr.status + ")...");
                $('#uploadBacklog').children().children().prop('disabled', false);
            }, 1000)
        }
    })

})