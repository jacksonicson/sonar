jQuery(document).ready(function ($) {
    // Init tabs
    $('#tabs').tab();

    // Register event handlers
    $('#submitHost').click(submitHost);
    $('#btnNewHost').click(newHost);
    $('#btnNewSensor').click(newSensor);
    $('#submitSensor').click(submitSensor);

    jQuery(document).ready(function ($) {
        $('#addButton').click(addRowToParamTable);
        $('#sensorParamTable td img.delete').live('click', function() {
            $(this).parent().parent().remove();
        });
    });

    // Load list data
    updateSensorList();
    updateHostsList();
});

function addRowToParamTable(){
    $('#sensorParamTable tr:last').after('<tr><td><input type="text" placeholder="Key.." name="sensorParamKey"/></td><td><textarea rows="" cols="" name="sensorParamValue"  placeholder="Value.."></textarea></td><td><img src="images/delete.png" class="delete" border="0">');
}
function newSensor(event){
    $('#sensorName').attr("value", "");
    $('#sensorLabels').attr("value", "");
    $('#sensorInterval').attr("value", "");
    $('#newSensorDlg').modal('show');
    $('#sensorParamTable tr:gt(0)').remove();
    clearFormElements($('#newSensorForm'));
}

function clearFormElements(ele) {

    $(ele).find(':input').each(function() {
        switch(this.type) {
            case 'password':
            case 'select-multiple':
            case 'select-one':
            case 'text':
            case 'textarea':
                $(this).val('');
                break;
            case 'checkbox':
            case 'radio':
                this.checked = false;
        }
    });

}

function submitSensor(event) {
    var test = $("#newSensorForm").serialize();
    console.log("FORM: " + test);

    $.ajax({
        type:"POST",
        url:'{{ROOT_SENSORADD}}',
        dataType:'text',
        data:test,

        success:function (data) {
            if (data == 'ok') {
                updateSensorList();
            } else {
                $('#errors').show();
                $('#errors').text("Error: Could not save sensor...");
            }

            $('#newSensorDlg').modal('hide');
        }
    });
}

function deleteHost(event) {
    var host = event.target.id;

    $.ajax({
        type:"GET",
        url:'{{ROOT_DELHOST}}?hostname=' + host,
        dataType:'text',
        success:function (data) {
            updateHostsList();
        }
    });
}

function deleteSensor(event) {
    var sensor = event.target.id;

    $.ajax({
        type:"GET",
        url:'{{ROOT_SENSORDEL}}?sensorName=' + sensor,
        dataType:'text',
        success:function (data) {

            updateSensorList();
        }
    });
}


function submitHost(event) {
    var editHost = event.target.id;

    var form = $('#newHostForm').serialize();
    console.log(form);

    $.ajax({
        type:"POST",
        url:'{{ROOT_ADDHOST}}',
        dataType:'text',
        data:form,

        success:function (data) {
            if (data == 'ok') {
                updateHostsList();
                $('#newHost').modal('hide');
            } else {
                $('#errors').show();
                $('#errors').text("Error: Could not save host...");
            }

            $('#newHost').modal('hide');
        }
    });
}

function newHost(event) {
    $('#sensorField').empty();

    $.ajax({
        type:"GET",
        url:'{{ROOT_SENSORS}}',
        dataType:'json',

        success:function (sensors) {

            var sensorField = $('#sensorField');

            for (var s in sensors) {
                var sensor = sensors[s]
                var checked = "no";

                sensorField.append(
                    $('<div>').addClass("controls").attr("id", sensor.name).append(
                        $('<label>').addClass("checkbox").text(sensor.name).append(
                            $('<input>').attr("type", "checkbox").attr("id", "chbx_" + sensor.name).attr("name", "sensor_" + sensor.name)
                        )
                    )
                )
            }

            $('#hostName').attr("value", "");
            $('#hostLabels').attr("value", "");
            $('#newHost').modal('show');
        }
    });
}

function editHost(event) {
    var editHost = event.target.id;
    editHostIntern(event, editHost);
}

function editHostIntern(event, editHost) {

    console.log("editing host");

    var sensorField = $('#sensorField').empty();

    $.ajax({
        type:"GET",
        url:'{{ROOT_HOSTS}}',
        dataType:'json',

        success:function (hosts) {

            for (var i in hosts) {
                var host = hosts[i];

                console.log("checking hostname: " + host.hostname + " against " + editHost);
                if (host.hostname == editHost) {
                    console.log("Hostname LISTING SENSORS NOW: " + host.hostname);

                    var sensorField = $('#sensorField');

                    $('#hostName').attr("value", host.hostname);

                    console.log("labels: " + host.labels);
                    var labelsString = "";
                    for (var i = 0; i < host.labels.length; i++) {
                        if(host.labels[i] == '')
                            continue;

                        labelsString += host.labels[i];
                        if ((i + 1) >= host.labels.length)
                            labelsString += ","
                    }

                    $('#hostLabels').attr("value", labelsString);


                    for (var s in host.sensor) {

                        var sensor = host.sensor[s]

                        sensorField.append(
                            $('<div>').addClass("controls").attr("id", sensor.name).append(
                                $('<label>').addClass("checkbox").text(sensor.name).append(
                                    $('<input>').attr("type", "checkbox").attr("id", "chbx_" + sensor.name).attr("name", "sensor_" + sensor.name)
                                )
                            )
                        )

                        console.log("sensor active: " + sensor.active + " sensor " + sensor.name);

                        if (sensor.active) {
                            $("#chbx_" + sensor.name).attr("checked", "yes")
                        }
                    }

                    $('#newHost').modal('show');

                    // hostname found - form filled - exit
                    break;
                }
            }
        }
    });


}

function updateHostsList() {
    doAlert("Loading...");

    // Load all hosts
    $.ajax({
        type:"GET",
        url:'{{ROOT_HOSTS}}',
        dataType:'json',

        success:function (data) {
            // Body for the hosts lists
            var $wrap = $('#listHostsBody');
            $wrap.children('tr').remove();

            // For each host
            for (var i in data) {
                var host = data[i];

                // Create a cell with the data about the sensor
                var activeSensors = []
                for (var s in host.sensor) {
                    var sensor = host.sensor[s];
                    if (sensor.active) {
                        activeSensors.push(sensor.name);
                    }
                }

                var list = $('<ul>');
                for (var j in activeSensors) {
                    list.append(
                        $('<li>').text(activeSensors[j])
                    )
                }

                $wrap.append(
                    $('<tr>')
                        .append(
                        $('<td>').text(i),
                        $('<td>').append(
                            $('<a>').append($('<i>').addClass('ico-trash'), "Delete").addClass("btn").attr("id", host.hostname).click(deleteHost)
                        ),
                        $('<td>').append(
                            $('<a>').text(host.hostname).click(editHost).attr("href", "#").attr("id", host.hostname)
                        ),
                        $('<td>').append(list)
                    )
                );
            }

            //alert(data); // shows whole dom
            // alert( $(data).find('#wrapper').html() ); // returns null
            stopAlert();

        },
        error:function () {
            console.log("ajax call failed");
        }
    });
}

function updateSensorList() {
    doAlert("Loading...");

    $.ajax({
        type:"GET",
        url:'{{ROOT_SENSORS}}',
        dataType:'json',

        success:function (data) {

            var wrap = $('#listSensorsBody');
            wrap.children('tr').remove();
            for (var i in data) {
                var sensor = data[i];

                var labelString = '';
                for (var j = 0; j < sensor.labels.length; j++) {
                    labelString += sensor.labels[j];
                    if (j < (sensor.labels.length - 1))
                        labelString += ","
                }

                wrap.append(
                    $('<tr>')
                        .append(
                        $('<td>').text(i),

                        $('<td>').append(
                            $('<a>').append($('<i>').addClass('ico-trash'), "Delete").addClass("btn").attr("id", sensor.name).click(deleteSensor)
                        ),
						$('<td>').append(
                            $('<a>').text(sensor.name).click(editSensor).attr("href", "#").attr("id", sensor.name)
                        ),
                        $('<td>').text(sensor.binary),
                        $('<td>').text(labelString)
                    )
                );
            }

            //alert(data); // shows whole dom
            // alert( $(data).find('#wrapper').html() ); // returns null

            stopAlert();
        },
        error:function () {
            console.log("ajax call failed");
        }
    });
}

function editSensor(event){
	var editSensor = event.target.id;
    clearFormElements($('#newSensorForm'));
    editSenrorIntern(event, editSensor);
}

function editSenrorIntern(event, editSensor){
	console.log("editing sensor" + editSensor);

    $.ajax({
        type:"GET",
        url:'{{ROOT_SENSORS}}',
        dataType:'json',

        success:function (data) {

            for (var i in data) {
                var sensor = data[i];
                console.log("checking sensor name: " + sensor.name + " against " + editSensor);
				if(sensor.name == editSensor){
					$('#sensorName').attr("value", sensor.name);
						var labelString = '';
					for (var j = 0; j < sensor.labels.length; j++) {
						labelString += sensor.labels[j];
						if (j < (sensor.labels.length - 1))
							labelString += ","
					}
                    populateSensorConfiguration(sensor.name);
					break;
				}
			}
        }
    });
}

function populateSensorConfiguration(sensorName){
    $('#sensorParamTable tr:gt(0)').remove();
    $.ajax({
        type:"POST",
        url:'{{ROOT_SENSORCONF}}',
        dataType:'json',
        data: "sensor=" + sensorName,
        success: function(configData){
            // get interval value
            $('#sensorInterval').attr("value", configData.interval);

            // get the parameters value
            if(null != configData.parameters && configData.parameters.length > 0){
            for(var count = 0; count < configData.parameters.length; count++){
                var parameter = configData.parameters[count];
                $('#sensorParamTable tr:last').after('<tr><td><input type="text" placeholder="Key.." value="' + parameter.key + '" name="sensorParamKey"/></td><td><textarea name="sensorParamValue"  placeholder="Value..">' + parameter.value +'</textarea></td><td><img src="images/delete.png" class="delete" border="0">');
            }
            }
            $('#newSensorDlg').modal('show');
        }
    });
}

