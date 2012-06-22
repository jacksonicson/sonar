// Document ready handler
$(function () {
	setupDatePickers();
    setupHandlers();
});

function setupDatePickers() {
    $('#startdate').datepicker();
    $('#stopdate').datepicker();
	
	var myDate = new Date();
    var month = myDate.getMonth() + 1;
    var prettyDate = month + '/' + myDate.getDate() + '/' + myDate.getFullYear();
	$("#startdate").val(prettyDate);
	$("#stopdate").val(prettyDate);

    $('.dropdown-timepicker').timepicker({
        defaultTime: 'current',
        minuteStep: 15,
        disableFocus: false,
        template: 'dropdown'
    });
}

function setupHandlers() {
    $('#addQuery').on("click", addQueryHandler);
}

function addQueryHandler(event) {
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
        }
    })
}

function renderLogs(list){
	if(list.length == 0){
		$('#container').text('No Logs Found');
	}
	else {
		$('#container').text('');
		for(var i = 0; i < list.length ; i++)
		{
			$('#container').append(formatLogMessage(list[i]));
		}
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

function formatLogMessage(logMessage){
	var result = "<p>";
	result += "[" + timeConverter(logMessage.timestamp) + "] ";
	result += "[Sev: " + logMessage.logLevel + "] ";
	result += "[" + logMessage.programName + "] ";
	result += logMessage.logMessage;
	result += "</p>";
	return result;
}

