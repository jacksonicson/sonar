// Document ready handler
$(function () {
    setupDatePickers();
    setupHandlers();
});

function setupDatePickers() {


}

function setupDatePickers() {

    /*var myDate = new Date();
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
     });*/

    var myDate = new Date();
    var month = myDate.getMonth() + 1;
    var prettyDate = month + '/' + myDate.getDate() + '/' + myDate.getFullYear();
    $("#startdate").val(prettyDate);
    $("#stopdate").val(prettyDate);

    $('#startdate').datepicker();
    $('#stopdate').datepicker();

    $(document).ready(function () {
        $('.timepicker-default').timepicker({
            showMeridian:false
        });
    });

    getHostData(function (output) {
        var hosts;
        hosts = new Array;
        $.each(output, function (index, item) {
            hosts.push(item.hostname);
        });

        $('#hostname').typeahead({
            source:hosts
        });
    });

    getSensorData(function (output) {
        var sensors;
        sensors = new Array;
        $.each(output, function (index, item) {
            sensors.push(item.name);
        });
        $('#sensor').typeahead({
            source:sensors
        });
    });

    $(".top").live('click', function () {
        if ($(this).children(".mid").is(':visible')) {
            $(this).children(".mid").slideUp();
        } else {
            $(this).children(".mid").slideDown();
        }
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

function renderLogs(list) {
    var logTable = $('#logResultsTableBody');
    logTable.children('tr').remove();
    $("#logsFoundtext").text(list.length);

    for (var i = 0; i < list.length; i++) {
        var msg = list[i];
        var heading = null;
        heading = msg.logMessage.replace(/(\r\n|\n|\r)/gm, "");
        if (msg.logMessage.length > 60) {
            heading = heading.substr(0, 60) + "...";
        }
        logTable.append(
            $('<tr>').append(
                $('<td>').text(msg.programName),
                $('<td>').append(
                    $('<img>').attr({ src:getLogLevelImage(msg.logLevel), title:getLogLevelNames(msg.logLevel)})
                ),
                $('<td>').append(
                    $('<div>').attr({class:"top"}).html(heading).append(
                        $('<div>').css({"display":"none", "word-wrap":"break-word", "padding-left":"10px", "padding-right":"10px", "background-color":"#E6E6E6", "border-radius":"2px", "moz-border-radius":"2px"})
                            .width(500).attr({class:"mid"}).html(msg.logMessage + "<br/>Date: " + timeConverter(msg.timestamp))
                    )
                )
            )
        );
    }
}

function getLogLevelNames(logLevel) {
    var level = parseInt(logLevel);
    switch (level) {
        case 50010:
            return "Sync";
        case 50000:
            return "Fatal";
        case 40000:
            return "Error";
        case 30000:
            return "Warning";
        case 20000:
            return "Info";
        case 10000:
            return "Debug";
        case 5000:
            return "Trace";
    }
}

function getLogLevelImage(logLevel) {
    var level = parseInt(logLevel);
    switch (level) {
        case 50000:
        case 40000:
            return "images/error_level.png";
        case 30000:
            return "images/warn_level.png";
        case 20000:
            return "images/info_level.png";
        case 10000:
        case 5000:
            return "images/debug_level.png";
        case 50010:
            return "images/sync.png";
    }
}

function timeConverter(UNIX_timestamp) {
    var a = new Date(UNIX_timestamp * 1000);
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var year = a.getFullYear();
    var month = months[a.getMonth()];
    var date = a.getDate();
    var hour = a.getHours();
    var min = a.getMinutes();
    var sec = a.getSeconds();
    var time = date + ',' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec;
    return time;
}
