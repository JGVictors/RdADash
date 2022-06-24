$(document).ready(function () {

    $('#loading-content').fadeOut(600, function () { $('#loading-content').addClass('invisible') })

    updateTime($('#timenowDiv'))

});

function updateTime(timeDiv){

    timeRfrsh = timeDiv.children().first()
    timeRfrsh.click(false)
    timeRfrsh.removeAttr("role")
    

    $.ajax({
        url: "/getTimenow",
        method: "POST",
        datatype: "JSON",
        success: function(r){
            $("#timenow").text(r['timenow']) 
        }  
    })

    setTimeout(() => {
        timeRfrsh.click(() => { updateTime(timeDiv) })
        timeRfrsh.attr('role', 'button')
    }, 5000);

}