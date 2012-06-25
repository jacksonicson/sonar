// Global variables
var emptyData = [
    [0, 0],
    [100,0]
]

var chart;

function getHostData(handleData) {
    $.ajax({
        type:"GET",
        url:'/hosts',
        dataType:'json',
        success: function (results) {
            handleData(results);
        },
        error: function(error){
            console.log('oops');
        }
    });
};


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

    $('#sensor').typeahead({
        source: getSensors()
    })

});

function getSensors(){
    var sensors = new Array;
    return sensors;
}

function setupDatePickers() {
    $('#startdate').datepicker()
    $('#stopdate').datepicker()

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
                enabled:false
            }
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