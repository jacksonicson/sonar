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
        $('#sensorParamTable td a.btn').live('click', function() {
            $(this).parent().parent().remove();
        });
    });

    $('div.btn-group[data-toggle-name=*]').each(function(){
        var group   = $(this);
        var form    = group.parents('form').eq(0);
        var name    = group.attr('data-toggle-name');
        var hidden  = $('input[name="' + name + '"]', form);
        $('button', group).each(function(){
            var button = $(this);
            button.live('click', function(){
                hidden.val($(this).val());
            });
            if(button.val() == hidden.val()) {
                button.addClass('active');
            }
        });
    });
    
    $("#hostExtends").change(function() {
        var value = $(this).val();
        if(value == "-1"){
            // show the sensor selection div
            updateSensorField();
        } else {
            // hide the sensor selection div
            $('#sensorField').empty();
        }
    });

    // Load list data
    updateSensorList();
    updateHostsList();
});

function addRowToParamTable(parameter, disabledRow){

    if(null == parameter){
        parameter = {
            key:"",
            value:""
        }
    }

    var paramTable = $('#sensorParamTableBody');
    if(!disabledRow){
        paramTable.append(
            $('<tr>').append(
                $('<td>').append(
                        $('<input>').attr("type", "text").attr("placeholder","Key..").attr("name","sensorParamKey").val(parameter.key)
                ),
                $('<td>').append(
                    $('<textarea>').attr("name", "sensorParamValue").attr("placeholder","Value..").val(parameter.value)
                ),
                $('<td>').append(
                    $('<a>').addClass("btn").addClass("btn-primary").attr("href", "javascript:void(0)").append($('<i>').addClass('icon-trash').addClass('icon-white'))
                )
            )
        );
    } else {
        paramTable.append(
            $('<tr>').append(
                $('<td>').append(
                    $('<input>').attr("type", "text").attr("placeholder","Key..").attr("name","sensorParamKey").attr("disabled", "disabled").val(parameter.key)
                ),
                $('<td>').append(
                    $('<textarea>').attr("name", "sensorParamValue").attr("placeholder","Value..").attr("disabled", "disabled").val(parameter.value)
                ),
                $('<td>').append(
                    $('<input>').attr("type", "checkbox").change(function(){toggleData(this, parameter.key, parameter.value);})
                )
            )
        );
    }
}

function toggleData(object, key, value){
    var row = $(object).parent().parent();
    var keyObj = $(row).find('input[name$="sensorParamKey"]');
    var valObj = $(row).find('textarea[name$="sensorParamValue"]');
    if(!object.checked){
        keyObj.val(key);
        valObj.val(value);
        keyObj.attr('readonly', false);
        keyObj.attr("disabled", "disabled");
        valObj.attr("disabled", "disabled");
    } else {
        keyObj.removeAttr('disabled');
        keyObj.attr('readonly', true);
        valObj.removeAttr('disabled');
    }
}

function newSensor(event){
    $('#sensorName').attr("value", "");
    $('#sensorLabels').attr("value", "");
    $('#sensorInterval').attr("value", "");
    $('#sensorType').attr("value","0");
    $('#metricButton').button('toggle');
    $('#newSensorDlg').modal('show');

    var paramTable = $('#sensorParamTableBody');
    paramTable.children('tr').remove();

    clearFormElements($('#newSensorForm'));
    populateExtendSensorList(null, null);
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

function saveSensor(){
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

function submitSensor(event) {
    var test = $("#sensorName").val();
    deleteSensorActual(test, saveSensor);

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

function deleteSensor(event){
    deleteSensorActual(event.target.id, function(){
        updateSensorList();
    });
}

function deleteSensorActual(sensor, target) {
    $.ajax({
        type:"GET",
        url:'{{ROOT_SENSORDEL}}?sensorName=' + sensor,
        dataType:'text',
        success:target
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
            getHostListExcludingCurrentHost(null,null);
            $('#hostName').attr("value", "");
            $('#hostLabels').attr("value", "");
            $('#newHost').modal('show');
        }
    });
}

function updateSensorField(){
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
                    
                    getHostListExcludingCurrentHost(host.hostname, host.extendsHost);
                    
                    if(null == host.extendsHost){
                        // need not populate the sensor list when the host extends another host
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
                    }

                    $('#newHost').modal('show');

                    // hostname found - form filled - exit
                    break;
                }
            }
        }
    });
}

function getHostListExcludingCurrentHost(currentHostName, virtualHostSelected){
    $.ajax({
        type:"GET",
        url:'{{ROOT_HOSTS}}',
        dataType:'json',

        success:function (data) {
            $('#hostExtends').empty();
            var noneOpt = new Option("None", "-1");
            $(noneOpt).html("None");
            $("#hostExtends").append(noneOpt);
            
            for (var i in data) {
                var host = data[i];
                if(currentHostName == null || host.hostname.toLowerCase() != currentHostName.toLowerCase()){
                    var o = new Option(host.hostname, host.hostname);
                    $(o).html(host.hostname);
                    $("#hostExtends").append(o);
                }
            }
            if(null != virtualHostSelected){
                $("#hostExtends").val(virtualHostSelected); 
            }
        }
    });
}

function updateCheckboxStates(event){
    var id = event.target.id;
    var $table = $('#listHosts');
    var $rows = $('tbody > tr',$table);
    var atLeastOneSelected = false;
    
    $.each($rows, function(index, row){
        var keyA = $('td:eq(1) > input[type="checkbox"]', row);
        var hostName = keyA.attr('id');
        var actualHostName = hostName.substring(4, hostName.length);
        if(keyA.is(':checked')){
            setOption(actualHostName, true);
        } else {
            setOption(actualHostName, false);
        }
        if(keyA.is(':checked') && !atLeastOneSelected){
            atLeastOneSelected = true;
        }
    });
    
    if(atLeastOneSelected){
        $("#extendsButton").removeClass("disabled");
    } else {
        $("#extendsButton").addClass("disabled");
    }
}

function setBulkHostExtends(event){
    var hostNameStr = event.target.id;
    var parentHostName = hostNameStr.substring(8, hostNameStr.length);
    
    // get the selected children to override
    var formData = "";
    var $table = $('#listHosts');
    var $rows = $('tbody > tr',$table);
    
    $.each($rows, function(index, row){
        var keyA = $('td:eq(1) > input[type="checkbox"]', row);
        var hostName = keyA.attr('id');
        var actualHostName = hostName.substring(4, hostName.length);
        if(keyA.is(':checked')){
            formData += "childHost=" + actualHostName + "&";
        }
    });
    formData += "parentHost=" + parentHostName;
    
    $.ajax({
        type:"POST",
        url:'{{ROOT_HOSTEXTEND}}',
        dataType:'text',
        data:formData,
        success:function (data) {
            if (data == 'ok') {
                updateHostsList();
            } else {
                $('#errors').show();
                $('#errors').text("Error: Could not extend the sensors...");
            }
        }
    });
    
    
}

function setOption(hostname, option){
    var $button = $('ul#hostExtendOptions li');
    $.each($button, function(index, row){
         var keyA = $('a', row);
         if(hostname == keyA.text()){
            if(option){
                $(this).hide();
            } else {
                $(this).show();
            }
            return;
         }
    });
}

function sortHostTable(){
    var $table = $('#listHosts');
    var $rows = $('tbody > tr',$table);
    $rows.sort(function(a, b){
        var keyA = $('td:eq(3)',a);
        var keyB = $('td:eq(3)',b);
        return $(keyA).text().toUpperCase().localeCompare($(keyB).text().toUpperCase());

    });
    $.each($rows, function(index, row){
        $table.append(row);
    });

    $.each($rows, function(index, row) {
        $this = $(this)
        $this.find("td:eq(0)").html(index+1);
    });

}

function updateHostsList() {
    doAlert("Loading...");
    
    // clear states of extension
    $("#extendsButton").addClass("disabled");
    $("#hostExtendOptions li:not(:first)").remove();

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
                            $('<input>').attr("type", "checkbox").attr("id", "ext_" + host.hostname).attr("name", "extHosts").click(updateCheckboxStates)
                        ),
                        $('<td>').append(
                            $('<a>').append($('<i>').addClass('icon-trash'), "Delete").addClass("btn").attr("id", host.hostname).click(deleteHost)
                        ),
                        $('<td>').append(
                            $('<a>').text(host.hostname).click(editHost).attr("href", "javascript:void(0)").attr("id", host.hostname)
                        ),
                        $('<td>').append(list)
                    )
                );
                
                // clear host extesion
                $("#hostExtendOptions").append(
                    $('<li>').append(
                        $('<a>').text(host.hostname).attr("id", "hostext_" + host.hostname).click(setBulkHostExtends)
                    )
                );
            }

            //alert(data); // shows whole dom
            // alert( $(data).find('#wrapper').html() ); // returns null
            sortHostTable();
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
                            $('<a>').append($('<i>').addClass('icon-trash'), "Delete").addClass("btn").attr("id", sensor.name).click(deleteSensor),
                            $('<a>').append($('<i>').addClass('icon-cog'), "Extend").addClass("btn").attr("id", "ext_" + sensor.name).click(editSensorExtend)
                        ),
						$('<td>').append(
                            $('<a>').text(sensor.name).click(editSensor).attr("href", "javascript:void(0)").attr("id", sensor.name)
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

function editSensorExtend(event){
    var editSensor = event.target.id;
    var sensorName = editSensor.substring(4, editSensor.length);
    
    clearFormElements($('#newSensorForm'));
    editSenrorIntern(event, sensorName, true);
}

function editSensor(event, extendFlag){
	var editSensor = event.target.id;
    clearFormElements($('#newSensorForm'));
    editSenrorIntern(event, editSensor, false);
}

function editSenrorIntern(event, editSensor, extendFlag){
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
                    $('#sensorLabels').attr("value", labelString);
                    populateSensorConfiguration(sensor.name, extendFlag);
				}    
			}
        }
    });
}

function populateSensorConfiguration(sensorName, extendFlag){
    var paramTable = $('#sensorParamTableBody');
    paramTable.children('tr').remove();

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
                    if(parameter.extendSensor == sensorName)
                        addRowToParamTable(parameter);
                    else 
                        addRowToParamTable(parameter, true);
                }
            }

            if(configData.sensorType == 0){
                $('#sensorType').attr("value","0");
                $('#metricButton').button('toggle');
            } else if(configData.sensorType == 1){
                $('#sensorType').attr("value","1");
                $('#logButton').button('toggle');
            }

            populateExtendSensorList(sensorName, configData.sensorExtends);

            $('#newSensorDlg').modal('show');
        }
    });
    
    if(!extendFlag){
        $("#sensorNameGroup").show();
        $("#sensorLabelGroup").show();
        $("#sensorIntervalGroup").show();
        $("#sensorExtendControl").hide();
        $("#sensorTypeGroup").show();
        $("#sensorParamGroup").show();
    } else {
        $("#sensorNameGroup").hide();
        $("#sensorLabelGroup").hide();
        $("#sensorIntervalGroup").hide();
        $("#sensorExtendControl").show();
        $("#sensorTypeGroup").hide();
        $("#sensorParamGroup").hide();
    }
}

function populateExtendSensorList(sensorName, virtualSensorName){
    $.ajax({
        type:"GET",
        url:'{{ROOT_SENSORS}}',
        dataType:'json',

        success:function (data) {
            $('#sensorExtends').empty();
            var noneOpt = new Option("None", "-1");
            $(noneOpt).html("None");
            $("#sensorExtends").append(noneOpt);

            for (var i in data) {
                var sensor = data[i];
                if(sensorName == null || sensor.name.toLowerCase() != sensorName.toLowerCase()){
                    var o = new Option(sensor.name, sensor.name);
                    $(o).html(sensor.name);
                    $("#sensorExtends").append(o);
                }
                if(null != virtualSensorName){
                    $("#sensorExtends").val(virtualSensorName); 
                }
            }
        }
    });			
}

