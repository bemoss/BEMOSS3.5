/**

Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"

**/


$( document ).ready(function() {
    $.csrftoken();

    var _values_on_submit = {};
    var update_time;

    var ws = new WebSocket("ws://" + window.location.host +  "/socket_agent/"+device_data.agent_id);
     ws.onopen = function () {
         ws.send("WS opened from html page");
     };
     ws.onmessage = function (event) {
         var _data = event.data;
         _data = $.parseJSON(_data);
         var topic = _data['topic'];
          // from/agent_id/device_status_response
         // from/agent_id/device_update_response
         if (topic) {
             topic = topic.split('/');
             console.log(topic);
             if (topic[3] == device_data.agent_id && topic[4] == 'device_status_response') {
                 if ($.type( _data['message'] ) === "string"){
                     var _message = $.parseJSON(_data['message']);
                     if ($.type(_message) != "object"){
                         _message = $.parseJSON(_message)
                     }
                     change_rtu_values(_message);
                 } else if ($.type( _data['message'] ) === "object"){
                     change_rtu_values(_data['message']);
                 }

             }
             if (topic[3] == device_data.agent_id && topic[4] == 'update_response') {
                 var message_upd = _data['message'];
                 var popup = false
                 if ($.type( _data['message'] ) === "string"){
                    if (message_upd.indexOf('success') > -1) {
                        popup = true
                        }
                 } else if ($.type( _data['message'] ) === "object") {
                    if (message_upd['message'].indexOf('success') > -1){
                        popup = true
                        }
                 }

                 if (popup) {
                     change_rtu_values_on_submit_success(_values_on_submit);
                     $('.bottom-right').notify({
                        message: { text: 'The changes made at '+update_time+" are now updated in the device!"},
                        type: 'blackgloss',

                         fadeOut: { enabled: true, delay: 5000 }
                      }).show();
                 }
             }
         }
     };

    function change_rtu_values_on_submit_success(_data) {
        if (_data.fan_status == 'ON') {
            if ($("#on_fan").hasClass('btn-default')) {
                $("#on_fan").removeClass('btn-default').addClass('btn-success');
                $("#off_fan").removeClass('btn-success').addClass('btn-default');
            }
        }

        if (_data.cooling_status == 'ON') {
            if ($("#on_cool").hasClass('btn-default')) {
                $("#on_cool").removeClass('btn-default').addClass('btn-success');
                $("#off_cool").removeClass('btn-success').addClass('btn-default');
            }
        }

        $('#heating').slider({ value: _data.heating });
        $("#heating_level").text(_data.heating);

        $('#outside_damper').slider({ value: _data.outside_damper_position });
        $("#outside_damper_val").text(_data.outside_damper_position);

        $('#bypass_damper').slider({ value: _data.bypass_damper_position });
        $("#bypass_damper_val").text(_data.bypass_damper_position);

        $("#heat_setpoint").text(_data.heat_setpoint);
        $("#cool_setpoint").text(_data.cool_setpoint);

        if (_data.cooling_mode == 'None') {
            $("#coolmode").text("None");
        } else if (_data.cooling_mode == 'STG1') {
            $("#coolmode").text("Stage 1 Cooling");
        } else if (_data.cooling_mode == 'STG2') {
            $("#coolmode").text("Stage 2 Cooling");
        } else if (_data.cooling_mode == 'STG3') {
            $("#coolmode").text("Stage 3 Cooling");
        } else if (_data.cooling_mode == 'STG4') {
            $("#coolmode").text("Stage 4 Cooling");
        }

    }

    function change_rtu_values(_data) {
        if (_data.fan_status == 'ON') {
            if ($("#on_fan").hasClass('btn-default')) {
                $("#on_fan").removeClass('btn-default').addClass('btn-success');
                $("#off_fan").removeClass('btn-success').addClass('btn-default');
            }
        }

        if (_data.cooling_status == 'ON') {
            if ($("#on_cool").hasClass('btn-default')) {
                $("#on_cool").removeClass('btn-default').addClass('btn-success');
                $("#off_cool").removeClass('btn-success').addClass('btn-default');
            }
        }

        $('#heating').slider({ value: _data.heating });
        $("#heating_level").text(_data.heating);

        $('#outside_damper').slider({ value: _data.outside_damper_position });
        $("#outside_damper_val").text(_data.outside_damper_position);

        $('#bypass_damper').slider({ value: _data.bypass_damper_position });
        $("#bypass_damper_val").text(_data.bypass_damper_position);

        $("#heat_setpoint").text(_data.heat_setpoint);
        $("#cool_setpoint").text(_data.cool_setpoint);

        $("#outside_temp").text(_data.outdoor_temperature);

        $("#return_temp").text("--");
        $("#supply_temp").text("--");
        $("#pressure").text("--");

        if (_data.cooling_mode == 'None') {
            $("#coolmode").text("None");
        } else if (_data.cooling_mode == 'STG1') {
            $("#coolmode").text("Stage 1 Cooling");
        } else if (_data.cooling_mode == 'STG2') {
            $("#coolmode").text("Stage 2 Cooling");
        } else if (_data.cooling_mode == 'STG3') {
            $("#coolmode").text("Stage 3 Cooling");
        } else if (_data.cooling_mode == 'STG4') {
            $("#coolmode").text("Stage 4 Cooling");
        }

    }

    //Dropdown value append
    $('.dropdown-menu li').click(function(event) {
      var $target = $( event.currentTarget );
      $target.closest( '.btn-group' )
         .find( '[data-bind="label"]' ).text( $target.text() )
            .end()
         .children( '.dropdown-toggle' ).dropdown( 'toggle' );

      return false;
    });

    var setHeight = $("#actt").height();
    $("#dispp").height(setHeight+'px');

    $("button[id^='off_']").click(function(e) {
        e.preventDefault();
        var off = this.id.split("_");
        var on = "on_" + off[1];
        if ($(this).hasClass('btn-success')) {
            $(this).removeClass('btn-success').addClass('btn-default');
            $('#' + on).removeClass('btn-default').addClass('btn-success');
        } else {
            $(this).removeClass('btn-default').addClass('btn-success');
            $('#' + on).removeClass('btn-success').addClass('btn-default');
        }
    });

    $("button[id^='on_']").click(function(e) {
        e.preventDefault();
        var on = this.id.split("_");
        var off = "off_" + on[1];
        if ($(this).hasClass('btn-success')) {
            $(this).removeClass('btn-success').addClass('btn-default');
            $('#' + off).removeClass('btn-default').addClass('btn-success');
        } else {
            $(this).removeClass('btn-default').addClass('btn-success');
            $('#' + off).removeClass('btn-success').addClass('btn-default');
        }
    });

    $("#heating").slider({
        value: heating,
        orientation: "horizontal",
        range: "min",
        animate: true,
        min: 0,
        max: 100,
        step: 1,
        slide: function (event, ui) {
            $("#heating_level").html(ui.value);
        }
    });

    $("#outside_damper").slider({
        value: outside_damper,
        orientation: "horizontal",
        range: "min",
        animate: true,
        min: 0,
        max: 100,
        step: 1,
        slide: function (event, ui) {
            $("#outside_damper_val").html(ui.value);
        }
    });

    $("#bypass_damper").slider({
        value: bypass_damper,
        orientation: "horizontal",
        range: "min",
        animate: true,
        min: 0,
        max: 100,
        step: 1,
        slide: function (event, ui) {
            $("#bypass_damper_val").html(ui.value);
        }
    });
    $(".slider").slider("float");

    if (role == 'tenant') {
         $('#heating').slider("disable");
        $('#outside_damper').slider("disable");
        $('#bypass_damper').slider("disable");
    }

    $('#heatplus').click(function(e){
        e.preventDefault();
        var currentVal = parseInt($("#heat_setpoint").text());
        if (!isNaN(currentVal) && currentVal < 95) {
            $('#heat_setpoint').text(currentVal + 1);
        } else {
            $('#heat_setpoint').text(95);
        }
    });

    $("#heatminus").click(function(e) {
            e.preventDefault();
            var currentVal = parseInt($("#heat_setpoint").text());
            if (!isNaN(currentVal) && currentVal > 35) {
                $('#heat_setpoint').text(currentVal - 1);
            } else {
                $('#heat_setpoint').text(35);
            }
        });

    $('#coolplus').click(function(e){
            e.preventDefault();
            var currentVal = parseInt($("#cool_setpoint").text());
            if (!isNaN(currentVal) && currentVal < 95) {
                $('#cool_setpoint').text(currentVal + 1);
            } else {
                $('#cool_setpoint').text(95);
            }
        });

    $("#coolminus").click(function(e) {
            e.preventDefault();
            var currentVal = parseInt($("#cool_setpoint").text());
            if (!isNaN(currentVal) && currentVal > 35) {
                $('#cool_setpoint').text(currentVal - 1);
            } else {
                $('#cool_setpoint').text(35);
            }
        });


    $("#submit_rtu_data").click(function(e){
        e.preventDefault();
        update_time = new Date();
	    update_time = update_time.toLocaleTimeString();
        var heat_setpoint = $("#heat_setpoint").text();
        var cool_setpoint = $("#cool_setpoint").text();
        var fan_state = 'OFF';
        if ($("#on_fan").hasClass("btn-success")){
            fan_state = 'ON';
        }
        var cooling_status = 'OFF';
        if ($("#on_cool").hasClass("btn-success")){
            cooling_status = 'ON';
        }
        var cooling_mode = $("#coolmode").text();

        if (cooling_mode == 'None') {
            cooling_mode = 'NONE';
        } else if (cooling_mode == 'Stage 1 Cooling') {
            cooling_mode = 'STG1';
        } else if (cooling_mode == 'Stage 2 Cooling') {
            cooling_mode = 'STG2';
        } else if (cooling_mode == 'Stage 3 Cooling') {
            cooling_mode = 'STG3';
        } else if (cooling_mode == 'Stage 4 Cooling') {
            cooling_mode = 'STG4';
        }

        var heating = $("#heating_level").text();
        var outside_damper = $("#outside_damper_val").text();
        var bypass_damper = $("#bypass_damper_val").text();

        var values = {
            "heat_setpoint": parseFloat(heat_setpoint),
            "cool_setpoint": parseFloat(cool_setpoint),
            "fan_state": fan_state,
            "cooling_status": cooling_status,
            "cooling_mode": cooling_mode,
            "heating": parseInt(heating),
            "outside_damper_position": parseInt(outside_damper),
            "bypass_damper_position": parseInt(bypass_damper),
            "agent_id": agent_id
        };
        _values_on_submit = values;
        var jsonText = JSON.stringify(values);
        console.log(jsonText);
        $.ajax({
              url : '/device/_update/',
              type: 'POST',
              data: jsonText,
              dataType: 'json',
              success : function(data) {
                console.log("Data submitted");

              },
              error: function(data) {
                  //submit_thermostat_data(values);
                  $('.bottom-right').notify({
                        message: { text: 'Something went wrong when submitting RTU data. Please try again.' },
                        type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
                    }).show();
              }
		 });

    });

});