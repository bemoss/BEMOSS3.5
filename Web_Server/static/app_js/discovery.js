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
    $.ajaxSetup({
         beforeSend: function(xhr, settings){
             function getCookie(n) {
                 var cookieValue = null;
                 if(document.cookie&&document.cookie != ''){
                     var cookies = document.cookie.split(';');
                     for(var i = 0; i < cookies.length; i++){
                         var cookie = jQuery.trim(cookies[i]);
                         if(cookie.substring(0, n.length + 1) == (n + '=')){
                             cookieValue = decodeURIComponent(cookie.substring(n.length + 1));
                             break;
                         }
                     }
                 }
                 return cookieValue;
             }
             if(!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))){
                 xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
             }
         }
    });

    var ws = new WebSocket("ws://" + window.location.host + "/socket_agent/approvalhelperagent");
     ws.onopen = function () {
         ws.send("WS opened from html page");
     };
     ws.onmessage = function (event) {
         var _data1 = event.data;
         if (_data1 == "Open_Success"){
             return;
         }
         _data = $.parseJSON(_data1);
         if (! ('topic' in _data) ){
             return
         }
         var topic = _data['topic'];
         // '/ui/web/misc/get_device_username/response'
         if (topic) {
             topic = topic.split('/');
             console.log(topic);
             // from/misc/approvalhelper_get_device_username_response
             // from/misc/device_update_response
             if (topic[3] == "approvalhelperagent" && topic[4] == "get_device_username_response") {
                 var message_upd = _data['message'];
                 message_upd = JSON.parse(message_upd);
                 if (message_upd['flag']==1) {
                     // change_values_on_success_submit(_values_on_submit);
                     // $("#lighting_tbl").find('tr').each(function (rowIndex, r) {
                     //     row_cells = $(this)[0];
                     //     model = row_cells.cells[2].innerHTML;
                     //     mac_addr = row_cells.cells[3].innerHTML.toLowerCase();
                     //     if (model.toLowerCase().indexOf('philips hue bridge') >= 0){
                     //         if (mac_addr == message_upd['mac']){
                     //             $(this).find(".app_stat_lt").text("Approved")
                     //            }
                     //        }
                     //    });
                     var agent_id = message_upd['agent_id'];
                     var t = document.createTextNode("Approved");
                     var newhref = document.createElement('a');
                     newhref.href = '#';
                     newhref.id = 'select_APR_'+agent_id;
                     var newli = document.createElement('Li');
                     var dropdownButton = document.getElementById('dm-pending-'+agent_id);
                     newhref.appendChild(t);
                     newli.appendChild(newhref);
                     dropdownButton.appendChild(newli);
                     $('.dropdown-menu li').click(function(event) {
                         event.preventDefault();
                         var $target = $( event.currentTarget );
                         $target.closest( '.btn-group' )
                         .find( '[data-bind="label"]' ).text( $target.text() )
                            .end()
                         .children( '.dropdown-toggle' ).dropdown( 'toggle' );
                         return false;
                     });

                     var buttonID = 'authorize-' + message_upd['agent_id'];
                     var AuthButton = document.getElementById(buttonID);
                     AuthButton.parentNode.removeChild(AuthButton);
                     $('.bottom-right').notify({
                        message: { text: 'You can approve the selected Device Now !'},
                        type: 'blackgloss',

                         fadeOut: { enabled: true, delay: 10000 }
                      }).show();
                 } else {
                     $('.bottom-right').notify({
                        message: { text: 'Selected device get username failed, please try again !'},
                        type: 'blackgloss',

                         fadeOut: { enabled: true, delay: 5000 }
                      }).show();
                 }
             }
         }
     };

    $('.dropdown-menu li').click(function(event) {
        event.preventDefault();
      var $target = $( event.currentTarget );
      $target.closest( '.btn-group' )
         .find( '[data-bind="label"]' ).text( $target.text() )
            .end()
         .children( '.dropdown-toggle' ).dropdown( 'toggle' );

      return false;
    });



    $(".authorize").click(function(evt) {
        evt.preventDefault();
        var identifier = (this).id;
        identify_id = identifier.split("-");
        identify_id = identify_id[1];
        values = {
            'agent_id': identify_id
        };
        var jsonText = JSON.stringify(values);
        $.ajax({
            url: url_authenticate,
            type: 'POST',
            data: jsonText,
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {
                if (data.indexOf("success") > -1) {
                    $('#' + identify_id + "-spin").addClass('fa fa-spinner fa-spin').removeClass('icon-search');
                    $("#authorize-" + identify_id).removeClass('btn-warning').addClass('btn-success disabled');
                    $('.bottom-left').notify({
                        message: { text: 'Authenticating, please press the button on your device to be authorized...' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                }
            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: { text: 'Authenticate failed! Please try again. ' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();

            }
        })

    });



    function submit_changes_for_table(table){
        var data =[];

        $(table).find('tr').each(function (rowIndex, r) {
            var cols = [];
            var agent_id = '';
            $(this).find("span[id^='zone-']").each(function () {
                agent_id = this.id;
                agent_id = agent_id.split("-");
                cols.push(agent_id[1]);
                cols.push($(this).text().trim());
            });
            $(this).find("input[id^='nick-']").each(function () {
                if (!agent_id){ //If zone information not available
                    agent_id = this.id;
                    agent_id = agent_id.split("-");
                    cols.push(agent_id[1]);
                    cols.push(''); //Blacnk zone
                }
                cols.push($(this).val());
            });

            $(this).find("span[id^='app_stat-']").each(function () {
                cols.push($(this).text().trim());

            });
            if (cols.length!=0) {
                data.push(cols);
            }
            console.log(data);

        });

            var status = ['Approved', 'Pending', 'Non-BEMOSS'];
            var abbr_status = ['APR', 'PND', 'NBD'];
            for (i=0; i<data.length;i++) {
                var submit_status = abbr_status[status.indexOf(data[i][3])];
                data[i][3] = submit_status;
            }
            values = {
                "data":data
            };
            var jsonText = JSON.stringify(values);
            console.log(jsonText);
            $.ajax({
			  url : url_change_zones,
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
                 setTimeout(function(){
                         window.location.reload();
                }, 3000);
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The changes could not be updated at the moment. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });

    }

    $("#set_approve_HVAC").click(function(e) {
        e.preventDefault();
        $(".app_stat_HVAC").text("Approved");

    });

    $("#set_approve_Lighting").click(function(e) {
        e.preventDefault();
        //$(".app_stat_lt").text("Approved");
        var data;
        $("#tbl_PND_Lighting").find('tr').each(function (rowIndex, r) {
            row_cells = $(this)[0];
            model = row_cells.cells[2].innerHTML;
            if (model.toLowerCase().indexOf('philips hue bridge') < 0){
                $(this).find(".app_stat_Lighting").text("Approved")
            }else{
                if (row_cells.cells[5].innerHTML.toLowerCase().indexOf('authorize') == -1){
                    $(this).find(".app_stat_Lighting").text("Approved")
                }else{
                    $('.bottom-right').notify({
                        message: { text: 'At least one Philips Hue cannot be approved now. Please press Authorize Device button(s)'},
                        type: 'blackgloss',

                         fadeOut: { enabled: true, delay: 10000 }
                      }).show();
                }
            }

        });


    });
    $(".btn-submit-devices").click(function (evt) {
        evt.preventDefault();
        table = evt.target.value;
        submit_changes_for_table(document.getElementById(table))
    });
    document.getElementsByName('btn_submit_devices')


    $("#set_approve_Plugload").click(function(e) {
        e.preventDefault();
        $(".app_stat_Plugload").text("Approved");

    });

    $("#set_approve_Sensor").click(function(e) {
        e.preventDefault();
        $(".app_stat_Sensor").text("Approved");

    });


});