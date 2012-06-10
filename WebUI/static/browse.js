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
});

function setupDatePickers() {
    $('#startdate').datepicker()
    $('#stopdate').datepicker()


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