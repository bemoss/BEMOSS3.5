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

    var ws = new WebSocket("ws://" + window.location.host + "/socket_agent/devicediscoveryagent");

     ws.onopen = function () {
         ws.send("WS opened from html page");
     };

     ws.onmessage = function (event) {
         var _data = event.data;
         if (_data == 'Open_Success'){
             return
         }
            _data = $.parseJSON(_data);
         var topic = _data['topic'];
         var message = _data['message'];

         if (topic) {
             topic = topic.split('/');
             // /agent/ui/misc/bemoss/discovery_request_response
              // from/agent_id/device_status_response
             // from/agent_id/device_update_response
             if (topic[3]=='devicediscoveryagent' && topic[4] == 'discovery_request_response') {
                 if (message == 'ON') {
                     update_discovery_status_on(message);
                     $('.bottom-right').notify({
                         message: {text: 'New Devices/Controllers are now being discovered.'},
                         type: 'blackgloss',
                         fadeOut: {enabled: true, delay: 5000}
                     }).show();
                 } else if (message == 'OFF') {
                     update_discovery_status_off(message);
                     $('.bottom-right').notify({
                         message: {text: 'New Devices/Controllers discovery now complete. Navigate to Discover/Manage --> Devices page to view new devices.'},
                         type: 'blackgloss',
                         fadeOut: {enabled: true, delay: 5000}
                    }).show();
                 }
             }

         }
     };

    function update_discovery_status_off(message){
        if (role == 'admin' || zone == uzone){

            $("#pnp_on").css('display','none');
            $("#pnp_off").css('display','block');
            $("#disc_selected").prop('disabled', false);

        }

    }

    function update_discovery_status_on(message){
        if (role == 'admin' || zone == uzone){
             $("#pnp_on").css('display','block');
             $("#pnp_off").css('display','none');
             $("#disc_selected").prop('disabled', false);
        }

    }

    ht = $(".eq_height_hvac").height();
    $(".eq_height_lt").height(ht);
    $(".eq_height_pl").height(ht);
    $(".eq_height_ss").height(ht);
    $(".eq_height_pm").height(ht);
    $(".eq_height_DER").height(ht);
    $(".eq_height_cam").height(ht);
    $("#hvac_all").change(function() {
        if($(this).is(":checked")) {
            $("input[id^=hvac_]").prop('checked', true);
        } else {
            $("input[id^=hvac_]").prop('checked', false);
        }
    });

    $("#lt_all").change(function() {
        if($(this).is(":checked")) {
            $("input[id^=lt_]").prop('checked', true);
        } else {
            $("input[id^=lt_]").prop('checked', false);
        }
    });

    $("#pl_all").change(function() {
        if($(this).is(":checked")) {
            $("input[id^=pl_]").prop('checked', true);
        } else {
            $("input[id^=pl_]").prop('checked', false);
        }
    });

    $("#ss_all").change(function() {
        if($(this).is(":checked")) {
            $("input[id^=ss_]").prop('checked', true);
        } else {
            $("input[id^=ss_]").prop('checked', false);
        }
    });

    $("#pm_all").change(function() {
        if($(this).is(":checked")) {
            $("input[id^=pm_]").prop('checked', true);
        } else {
            $("input[id^=pm_]").prop('checked', false);
        }
    });
    $("#DER_all").change(function() {
        if($(this).is(":checked")) {
            $("input[id^=DER_]").prop('checked', true);
        } else {
            $("input[id^=DER_]").prop('checked', false);
        }
    });
    $("#cam_all").change(function() {
        if($(this).is(":checked")) {
            $("input[id^=cam_]").prop('checked', true);
        } else {
            $("input[id^=cam_]").prop('checked', false);
        }
    });
    $('#disc_selected').click( function(evt){
          evt.preventDefault();
          var tobe_discovered = [];
	      $.each($('input:checked'), function(index, value) {
              var current_id = this.id;
                  if (!(current_id == "hvac_all") && !(current_id == "lt_all") && !(current_id == "pl_all") && !(current_id == "ss_all") && !(current_id == "pm_all") && !(current_id == "DER_all")&& !(current_id == "cam_all")) {
                    tobe_discovered.push(this.value);
                   }
          });
           var jsonText = JSON.stringify(tobe_discovered);
            //alert(jsonText);
            console.log(jsonText);

        if (tobe_discovered.length > 0) {
            if (role == 'admin') {
                $.ajax({
                    url: '/discovery/new/',
                    type: 'POST',
                    data: jsonText,
                    dataType: 'json',
                    success: function (data) {
                        console.log("testing");
                        console.log(data);
                        $("#disc_selected").prop('disabled', true);
                        $('.bottom-right').notify({
                            message: {text: 'Discovery of Selected Devices/Controllers will begin shortly.'},
                            type: 'blackgloss',
                            fadeOut: {enabled: true, delay: 5000}
                        }).show();
                         setTimeout(function(){
                         window.location.reload();
                }, 5000);
                    },
                    error: function (data) {
                        $('.bottom-right').notify({
                            message: {text: 'Communication Error. Try again later!'},
                            type: 'blackgloss',
                            fadeOut: {enabled: true, delay: 5000}
                        }).show();
                    }
                });
            } else {
                $('.bottom-right').notify({
                    message: {text: 'Unauthorized access to system functions; Aborted.'},
                    type: 'blackgloss',
                    fadeOut: {enabled: true, delay: 5000}
                }).show();
            }
        } else {
            $('.bottom-right').notify({
                            message: {text: 'No devices/controllers selected.'},
                            type: 'blackgloss',
                            fadeOut: {enabled: true, delay: 5000}
                        }).show();
        }
	   });
});
