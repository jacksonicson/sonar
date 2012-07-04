// Document ready handler
$(function () {
	setupDatePickers();
    setupHandlers();
});

function setupDatePickers() {
    var myDate = new Date();
    var month = myDate.getMonth() + 1;
    var prettyDate = month + '/' + myDate.getDate() + '/' + myDate.getFullYear();
	$("#startdate").val(prettyDate);
	$("#stopdate").val(prettyDate);

    $('#startdate').datepicker();
    $('#stopdate').datepicker();

    $('.dropdown-timepicker').timepicker({
        defaultTime: 'current',
        minuteStep: 15,
        disableFocus: false,
        template: 'dropdown'
    });

    getHostData(function(output){
        var hosts;
        hosts = new Array;
        $.each(output, function(index, item){
            hosts.push(item.hostname);
        });

        $('#hostname').typeahead({
            source: hosts
        });
    });

    getSensorData(function(output){
        var sensors;
        sensors = new Array;
        $.each(output, function(index, item){
            sensors.push(item.name);
        });
        $('#sensor').typeahead({
            source: sensors
        });
    });
}

function setupHandlers() {
    $('#addQuery').on("click", addQueryHandler);
}

function addQueryHandler(event) {
    doAlert("Loading...");
    event.preventDefault();

    // Serialize the form
    var serializedForm = $('#queryForm').serialize();

    // Ajax call to get the time series
    $.ajax({
        type:"POST",
        url:'/logdb',
        dataType:'json',
        data:serializedForm,

        success:function (list) {
            // update the div
            renderLogs(list);
            stopAlert();
        },
        error:function () {
            console.log("ajax call failed");
            stopAlert();
        }
    })
}

function renderLogs(list){
    var logTable = $('#logResultsTableBody');
    logTable.children('tr').remove();

    for(var i = 0; i < list.length ; i++)
    {
        var msg = list[i];
        logTable.append(
            $('<tr>').append(
                $('<td>').append(
                    $('<img>').attr("src", getLogLevelImage(msg.logLevel)).attr("alt", getLogLevelNames(msg.logLevel))
                ),
                $('<td>').text(getLogLevelNames(msg.logLevel)),
                $('<td>').text(timeConverter(msg.timestamp)),
                $('<td>').text(msg.programName),
                $('<td>').text(msg.logMessage)
            )
        );
    }
}

function getLogLevelNames(logLevel){
    var level = parseInt(logLevel);
    switch(level){
        case 0:
            return "Emergency";
        case 1:
            return "Alert";
        case 2:
            return "Critical";
        case 3:
            return "Error";
        case 4:
            return "Warning";
        case 5:
            return "Notice";
        case 6:
            return "Info";
        case 7:
            return "Debug";
    }
}

function getLogLevelImage(logLevel){
    var level = parseInt(logLevel);
    switch(level){
        case 0:
        case 1:
        case 2:
        case 3:
            return "images/error_level.png";
        case 4:
        case 5:
            return "images/warn_level.png";
        case 6:
            return "images/info_level.png";
        case 7:
            return "images/debug_level.png";
    }
}

function timeConverter(UNIX_timestamp){
	var a = new Date(UNIX_timestamp*1000);
	var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
	var year = a.getFullYear();
    var month = months[a.getMonth()];
    var date = a.getDate();
    var hour = a.getHours();
    var min = a.getMinutes();
    var sec = a.getSeconds();
    var time = date+','+month+' '+year+' '+hour+':'+min+':'+sec ;
    return time;
}
