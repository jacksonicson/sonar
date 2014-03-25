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
            hosts.push(item);
        });

        console.log("Hostnames loaded: " + hosts.length);

        $('#hostname').typeahead({
            source: hosts
        });
    });

    getSensorData(function(output){
        var sensors = output;
        console.log("Sensor names loaded: " + sensors.length);

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
           console.log("Sensornames loaded: " + results.length);
           return results;
        },
        error: function(error){
            console.log('oops');
        }
    });
    return sensors;
}

function setupDatePickers() {

    var myDate = new Date();
    myDate.setHours(myDate.getHours() - 5)
    var prettyDate = (myDate.getMonth() + 1) + '/' + myDate.getDate() + '/' + myDate.getFullYear();
    $("#startdate").val(prettyDate);
    $('#startdate').datepicker();

    var prettyTime = myDate.getHours() + ':' + myDate.getMinutes();
    $("#starttime").timepicker({
        showMeridian:false,
        defaultTime:prettyTime
    });


    var myDate = new Date();
    myDate.setHours(myDate.getHours()+24)
    var prettyDate = (myDate.getMonth() + 1) + '/' + myDate.getDate() + '/' + myDate.getFullYear();
    $("#stopdate").val(prettyDate);
    $('#stopdate').datepicker();

    var prettyTime = myDate.getHours() + ':' + myDate.getMinutes();
    $("#stoptime").timepicker({
        showMeridian:false,
        defaultTime:prettyTime
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
                name:'NULL',
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

    doAlert("Loading...");

    // Ajax call to get the time series
    $.ajax({
        type:"POST",
        url:'/tsdb',
        dataType:'json',
        data:serializedForm,

        success:function (list) {
            stopAlert();

            console.log(list);

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