function getHostData(handleData) {
    console.log("Loading host names...");
    $.ajax({
        type:"GET",
        url:'/hostsacmpl',
        dataType:'json',
        success: function (results) {
            console.log("Host names loaded.");
            handleData(results);
        },
        error: function(error){
            console.log('oops');
        }
    });
}


function getSensorData(handleData){
    console.log("Loading sensor names...");
    $.ajax({
        type:"GET",
        url:'/sensornames',
        dataType:'json',
        success: function (results) {
            console.log("Sensor names loaded.");
            handleData(results);
        },
        error: function(error){
            console.log('oops');
        }
    });
}