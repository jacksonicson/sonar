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
        navigation:{
            buttonOptions:{
                enabled:true
            }
        },
        export: {
          enabled: true
        },
        chart:{
            renderTo:'container',
            animation:false
        },
        rangeSelector:{
            selected:0,
            enabled:true,
            inputEnabled:false
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

function addQueryHandler(event) {
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
        }
    })
}