updateTime()

function updateTime(){

    $.ajax({
        url: "/getTimenow",
        method: "POST",
        datatype: "JSON",
        success: function(r){
            $("#timenow").text(r.timenow) 
        }  
    })

    setTimeout(updateTime, 45000)
}