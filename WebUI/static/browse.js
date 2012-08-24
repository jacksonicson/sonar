// Global variables
var emptyData = [
    [0, 0],
    [100,0]
]

var chart;

// Document ready handler
$(function () {
    setupDatePickers();
    setupHandlers();
    setupCharts();
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
});

function getSensors(){
    var sensors = new Array;
    $.ajax({
        type:"GET",
        url:'/sensornames',
        dataType:'json',
        success: function (results) {
           for(var count = 0 ; count < results.length ; count++){
               sensors.push(results[count].name);
           }
        },
        error: function(error){
            console.log('oops');
        }
    });
    return sensors;
}

function setupDatePickers() {

   	var myDate = new Date();
    var month = myDate.getMonth() + 1;
    var prettyDate = month + '/' + myDate.getDate() + '/' + myDate.getFullYear();
	$("#startdate").val(prettyDate);
	$("#stopdate").val(prettyDate);

    $('#startdate').datepicker();
    $('#stopdate').datepicker();

    $(document).ready(function () {
        $('.timepicker-default').timepicker({
            showMeridian: false
        });
    });
}

function setupHandlers() {
    $('#addQuery').on("click", addQueryHandler);
}

function setupCharts() {
	
	// to set the timezone to the current timezone
	Highcharts.setOptions({
		global: {
			useUTC: false
		}
	});
	
	chart = {
		
        tooltip:{
            enabled:false
        },
        navigator:{
            buttonOptions:{
                enabled:true
            }
        },

        rangeSelector: {
            selected: 2,
            enabled:true,
            inputEnabled:false,
            buttons: [{
                type: 'minute',
                count: 5,
                text: '5m'
            }, {
                type: 'minute',
                count: 15,
                text: '15m'
            }, {
                type: 'hour',
                count: 1,
                text: '1h'
            }, {
                type: 'day',
                count: 1,
                text: '1d'
            }, {
                type: 'all',
                text: 'All'
            }]
        },

        export: {
          enabled: true
        },
        chart:{
            renderTo:'container',
            animation:false,
            zoomType: 'x'
        },
        plotOptions:{
            series:{
                animation:false
            }
        },
        title:{
        },
        series:[
            {
                name:'EMPTY',
                data:emptyData
            }
        ]
    }

    // Create the chart
    chart = new Highcharts.StockChart(chart);
}

function addQueryHandler(event, noLabel) {
    event.preventDefault();
 
    // Serialize the form
    var serializedForm = $('#queryForm').serialize();

    // Ajax call to get the time series
    $.ajax({
        type:"POST",
        url:'/tsdb',
        dataType:'json',
        data:serializedForm,

        success:function (list) {
            // Ensure that the list contains at least one element
            if (list.length == 0)
                list.push([0, 0])

            // Update the time series in the chart
            chart.series[0].setData(list);
            if(!noLabel)
                addQueryLabel();
        }
    })
}

function resubmitForm(event){
    var id = event.target.id;
    var data=id.split("$");
    $("#hostname").val(data[0]);
    $("#sensor").val(data[1]);
    $("#startdate").val(data[2]);
    $("#starttime").val(data[3]);
    $("#stopdate").val(data[4]);
    $("#stoptime").val(data[5]); 
    addQueryHandler(event, true);
}

function addQueryLabel() {
    var id = $("#hostname").val() + "$" + $("#sensor").val() + "$" + $("#startdate").val() + "$" + $("#starttime").val() 
        + "$" + $("#stopdate").val() + "$" + $("#stoptime").val();

    if($("#hostname").val() == '')
        return
    if($("#sensor").val() == '')
        return

    var labelName = $("#hostname").val() + " / " + $("#sensor").val();

    $("#labelContainer").append(
        $('<span>').addClass("label").addClass("label-inverse").append(
            $('<a>').attr("id", id).addClass("labelLink").text(labelName).click(resubmitForm)
        ),
        $('<span>').text('  ')
    );
}