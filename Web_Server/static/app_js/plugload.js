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


var _values_on_submit_plugload = {};
// var device_type_id  = agent_id.slice(0,4);

$( "#sp_on" ).click(function() {
	if ($("#sp_on").css('background-color') == "green") {
	} else {
		$(this).css('background-color','green');
		$("#sp_off").css('background-color','rgba(222, 222, 222, 0.55)');
		status = 'ON';
	}
});

$( "#sp_off" ).click(function() {
	if ($("#sp_off").css('background-color') == "green") {
	} else {
		$(this).css('background-color','green');
		$("#sp_on").css('background-color','rgba(222, 222, 222, 0.55)');
		status = 'OFF';
	}
});


$( document ).ready(function() {
	$.csrftoken();


    if (device_data.power != null ) {
        var gauge_target = document.getElementById("chart_9");
        var gauge = new Gauge(gauge_target);
    }

    var ws = new WebSocket("ws://" + window.location.host + "/socket_agent/"+device_data.agent_id);

     ws.onopen = function () {
         ws.send("WS opened from html page");
     };

     ws.onmessage = function (event) {
         var _data = event.data;
         _data = $.parseJSON(_data);
         var topic = _data['topic'];
         // to/ui/from/agent_id/device_status_response
         // to/ui/from/agent_id/device_update_response
         if (topic) {
             topic = topic.split('/');
             console.log(topic);
             if (topic[3] == device_data.agent_id && topic[4] == 'device_status_response') {
                 if ($.type( _data['message'] ) === "string"){
                     var _message = $.parseJSON(_data['message']);
                     if ($.type(_message) != "object"){
                         _message = $.parseJSON(_message)
                     }
                     change_plugload_values(_message);
                 } else if ($.type( _data['message'] ) === "object"){
                     change_plugload_values(_data['message']);
                 }

             }
             // from/agent_id/device_status_response
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
                     change_plugload_values_on_success(_values_on_submit_plugload);
                     $('.bottom-right').notify({
                        message: { text: 'The changes made at '+update_time+" are now updated in the device!"},
                        type: 'blackgloss',

                         fadeOut: { enabled: true, delay: 5000 }
                      }).show();
                 }
             }
         }
     };


    var popts = {
        lines: 12, // The number of lines to draw
        angle: 0.0, // The length of each line
        lineWidth: 0.2, // The line thickness2
        pointer: {
            length: 0.8, // The radius of the inner circle
            strokeWidth: 0.03, // The rotation offset
            color: '#00000' // Fill color
        },
        limitMax: 'true',   // If true, the pointer will not go past the end of the gauge
        colorStart: '#6FADCF',   // Colors
        colorStop: '#8FC0DA',    // just experiment with them
        strokeColor: '#E0E0E0',   // to see which ones work best for you
        generateGradient: true,
        percentColors: [
            [0, "#a9d70b" ],
            [500, "#f9c802"],
            [1000, "#ff0000"]
        ],
        //animationSpeed: 30,
        fontSize: 20
    };


    if (device_data.power != null) {
        if (device_data.power != "") {
            //var power_val = [power];
            //var power_meter = $.jqplot('chart9', [power_val], options);
            $("#power_val").text(device_data.power);
            var power_val = parseInt(device_data.power);
            gauge.setTextField(document.getElementById("9-textfield"));
            gauge.setOptions(popts);
            gauge.maxValue = 1000;
            gauge.set(1);
            gauge.set(power_val);


        } else {

        }
    }

    function change_plugload_values_on_success(data) {
		if (data.status == 'ON') {
			$("#sp_on").css('background-color','green');
			$("#sp_off").css('background-color','rgba(222, 222, 222, 0.55)');
		} else {
			$("#sp_off").css('background-color','green');
			$("#sp_on").css('background-color','rgba(222, 222, 222, 0.55)');
		}
	}

	function change_plugload_values(data) {
		if (data.status == 'ON') {
			$("#sp_on").css('background-color','green');
			$("#sp_off").css('background-color','rgba(222, 222, 222, 0.55)');
		} else {
			$("#sp_off").css('background-color','green');
			$("#sp_on").css('background-color','rgba(222, 222, 222, 0.55)');			
		}
        if (data.power || data.power == 0) {
            $("#power_val").text(data.power);

            gauge.set(parseInt(data.power));
        }

	}

	$( "#confirm_change" ).click(function(evt) {
		evt.preventDefault();
		update_time = new Date();
		update_time = update_time.toLocaleTimeString();
		var status;
		if ($("#sp_off").css('background-color') == "green" || $("#sp_off").css('background-color') == "rgb(0, 128, 0)")
			status = 'OFF';
		else if ($("#sp_on").css('background-color') == "green" || $("#sp_on").css('background-color') == "rgb(0, 128, 0)")
			status = 'ON';
		
			values = {
					"status":status,
					"agent_id":agent_id,
					"user": user
			};
		_values_on_submit_plugload = values;
        submit_plugload_data(values)
	});

    function submit_plugload_data(values) {
        var jsonText = JSON.stringify(values);
	    console.log(jsonText);
		$.ajax({
			  url : '/device/_update/',
			  type: 'POST',
			  data: jsonText,
			  dataType: 'json',
			  success : function(data) {
			  	/*$('.bottom-right').notify({
			  	    message: { text: 'Your changes will be updated shortly' },
			  	    type: 'blackgloss'
			  	  }).show();*/
			  },
			  error: function(data) {
                  //submit_plugload_data(values);
				  $('.bottom-right').notify({
				  	    message: { text: 'Something went wrong when submitting the plugload data. Please try again.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });
    }

});
