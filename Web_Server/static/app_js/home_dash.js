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
    var nick_re = /^[A-Za-z0-9_]{6,15}$/;
    var ws = new WebSocket("ws://" + window.location.host + "/socket_agent/devicediscoveryagent");

     ws.onopen = function () {
         ws.send("WS opened from html page");
     };

     ws.onmessage = function (event) {
         var _data = event.data;
         _data = $.parseJSON(_data);
         var topic = _data['topic'];
         // ["", "ui", "web", "misc", "auto_discovery", "status"]
         var message = _data['message'];
         if (topic) {
             topic = topic.split('/');
             //console.log(topic);
             //to/ui/from/devicediscoveryagent/auto_discovery_status
             if (topic[3] == 'devicediscoveryagent' && topic[4] == 'auto_discovery_status') {
                 update_discovery_status(message);
             }
         }
     };


    function update_discovery_status(message){
        if (role == 'admin' || zone == uzone){
            if (message == 'ON'){
                 $("#pnp_on").css('display','block');
                 $("#pnp_off").css('display','none');
             } else {
                 $("#pnp_on").css('display','none');
                 $("#pnp_off").css('display','block');
             }
        }
    }

    //var nick_re = /^[A-Za-z0-9_ ]*[A-Za-z0-9 ][A-Za-z0-9_ ]{5,10}$/;
 //   var nick_re = /^[A-Za-z0-9_]{6,15}$/;

    $('body').on('click',"button[id^='hplus-']", function (e) {
        // Stop acting like a button
        e.preventDefault();
        // Get its current value
        var zone_id = this.id;
        zone_id = zone_id.split("-");
        zone_id = zone_id[1];
        var currentVal = parseFloat($("#heat_sp-"+zone_id).text());
        // If is not undefined
        if (!isNaN(currentVal) && currentVal < 95) {
            // Increment
            $("#heat_sp-"+zone_id).text(currentVal + 1);
        } else {
            // Otherwise put a 0 there
            $("#heat_sp-"+zone_id).text(95);
        }
    });

// This button will decrement the heat value till 0
    $('body').on('click',"button[id^='hminus-']", function (e) {
        // Stop acting like a button
        e.preventDefault();
        // Get its current value
        var zone_id = this.id;
        zone_id = zone_id.split("-");
        zone_id = zone_id[1];
        var currentVal = parseFloat($("#heat_sp-"+zone_id).text());
        // If it isn't undefined or its greater than 0
        if (!isNaN(currentVal) && currentVal > 35) {
            // Decrement one
            $("#heat_sp-"+zone_id).text(currentVal - 1);
        } else {
            // Otherwise put a 0 there
            $("#heat_sp-"+zone_id).text(35);
        }
    });

    $('body').on('click',"button[id^='cplus-']", function (e) {
        // Stop acting like a button
        e.preventDefault();
        // Get its current value
        var zone_id = this.id;
        zone_id = zone_id.split("-");
        zone_id = zone_id[1];
        var currentVal = parseFloat($("#cool_sp-"+zone_id).text());
        // If is not undefined
        if (!isNaN(currentVal) && currentVal < 95) {
            // Increment
            $("#cool_sp-"+zone_id).text(currentVal + 1);
        } else {
            // Otherwise put a 0 there
            $("#cool_sp-"+zone_id).text(95);
        }
    });

// This button will decrement the heat value till 0
    $('body').on('click',"button[id^='cminus-']", function (e) {
        // Stop acting like a button
        e.preventDefault();
        // Get its current value
        var zone_id = this.id;
        zone_id = zone_id.split("-");
        zone_id = zone_id[1];
        var currentVal = parseFloat($("#cool_sp-"+zone_id).text());
        // If it isn't undefined or its greater than 0
        if (!isNaN(currentVal) && currentVal > 35) {
            // Decrement one
           $("#cool_sp-"+zone_id).text(currentVal - 1);
        } else {
            // Otherwise put a 0 there
           $("#cool_sp-"+zone_id).text(35);
        }
    });

    $("#add_new_zone_submit").click(function (evt) {
            evt.preventDefault();
            values = $("#add_new_zone").val();
            if (!nick_re.test(values)) {
                document.getElementById("newzoneerror").innerHTML = "Nickname can only contain letters and numbers and a space. Please try again.";
                document.getElementById(values).value = "";
            } else {
                $.ajax({
                    url: '/add_new_zone/',
                    type: 'POST',
                    data: values,
                    success: function (data) {
                        if (data == "invalid") {
                            document.getElementById("newzoneerror").innerHTML = "Your nickname was not accepted by BEMOSS. Please try again.";
                        } else {
                            location.reload();
                            $('.bottom-right').notify({
                                message: { text: 'A new zone was added.' },
                                type: 'blackgloss',
                                fadeOut: { enabled: true, delay: 5000 }
                            }).show();
                        }
                    },
                    error: function (data) {
                        $('.bottom-right').notify({
                            message: { text: 'Oh snap! Try submitting again. ' },
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();
                    }
                });
            }
        });

    $( ".save_changes_zn" ).click(function(evt) {
        evt.preventDefault();
        values = this.id.split('-');
        node_id = values[1];
        values = "node_name_inputtxt_"+values[1];
        var value_er = values;
        nickname = $("#"+values).val();
        var error_id = "nodename_" + node_id;
        if (!nick_re.test(nickname)) {
            document.getElementById(error_id).innerHTML = "Nickname error. Please try again.";
            document.getElementById(values).value = "";
        } else {
        values = {
                "id": node_id,
                "nickname": nickname
                };
        document.getElementById(error_id).innerHTML = "";
        var jsonText = JSON.stringify(values);
        $.ajax({
              url : url_save_node_nickname,
              type: 'POST',
              data: jsonText,
              contentType: "application/json; charset=utf-8",
              dataType: 'json',
              success : function(data) {
                if (data == "invalid") {
                    document.getElementById(error_id).innerHTML = "Nickname error. Please try again.";
                    document.getElementById(value_er).value = "";
                } else {
                req_value_modal = "node_name_txt_"+data.node_id;
                var newtest = document.getElementById(req_value_modal);
                newtest.innerHTML = nickname.charAt(0).toUpperCase()+nickname.slice(1);
                $('.bottom-right').notify({
                    message: { text: 'Heads up! The node nickname change was successful.' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                  }).show();
                }
              },
              error: function(data) {
                  $('.bottom-right').notify({
                        message: { text: 'Error! Use close button to exit / Click on edit button to change nickname. ' },
                        type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
                    }).show();
              }
             });
        }
    });



    $('body').on('click',"button[id^='gs-']", function (e) {
        e.preventDefault();
        var zone_id = this.id;
        zone_id = zone_id.split("-");
        zone_id = zone_id[1];
        var heat_setpoint = "heat_sp-" + zone_id;
        var cool_setpoint = "cool_sp-" + zone_id;
        var illumination = "illumination-" +  zone_id;
        heat_setpoint = $("#"+heat_setpoint).text();
        cool_setpoint = $("#"+cool_setpoint).text();
        illumination = $("#"+illumination).text();

        var values = {
            "zone_id": zone_id,
            "heat_setpoint": heat_setpoint,
            "cool_setpoint": cool_setpoint,
            "illumination": illumination
        };
        var jsonText = JSON.stringify(values);
        console.log(jsonText);
        $.ajax({
			  url : '/change_global_settings/',
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
				//window.location.reload(true);
			  	$('.bottom-right').notify({
			  	    message: { text: 'Your changes were updated in the system.' },
			  	    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
			  	  }).show();
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The changes could not be updated at the moment. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });

    });

});
