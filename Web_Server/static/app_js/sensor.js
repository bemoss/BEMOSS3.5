/**

 *  Authors: BEMOSS Team
 *  Version: 3.5
 *  Email: aribemoss@gmail.com
 *  Created: "2014-10-13 18:45:40"
 *  Updated: "2015-02-13 15:06:41"


 * Copyright © 2014 by Virginia Polytechnic Institute and State University
 * All rights reserved

 * Virginia Polytechnic Institute and State University (Virginia Tech) owns the copyright for the BEMOSS software and its
 * associated documentation ("Software") and retains rights to grant research rights under patents related to
 * the BEMOSS software to other academic institutions or non-profit research institutions.
 * You should carefully read the following terms and conditions before using this software.
 * Your use of this Software indicates your acceptance of this license agreement and all terms and conditions.

 * You are hereby licensed to use the Software for Non-Commercial Purpose only.  Non-Commercial Purpose means the
 * use of the Software solely for research.  Non-Commercial Purpose excludes, without limitation, any use of
 * the Software, as part of, or in any way in connection with a product or service which is sold, offered for sale,
 * licensed, leased, loaned, or rented.  Permission to use, copy, modify, and distribute this compilation
 * for Non-Commercial Purpose to other academic institutions or non-profit research institutions is hereby granted
 * without fee, subject to the following terms of this license.

 * Commercial Use: If you desire to use the software for profit-making or commercial purposes,
 * you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
 * Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
 * licenses to others. You may contact the following by email to discuss commercial use:: vtippatents@vtip.org

 * Limitation of Liability: IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
 * THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
 * CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
 * LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
 * OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGES.

 * For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.

 * Address all correspondence regarding this license to Virginia Tech's electronic mail address:: vtippatents@vtip.org

**/


$( document ).ready(function() {
    $.csrftoken();

    var ws = new WebSocket("ws://" + window.location.host +  "/socket_agent/"+agent_id);

     ws.onopen = function () {
         ws.send("WS opened from html page");
     };

     ws.onmessage = function (event) {
         var _data = event.data;
         console.log(_data)
         //_data = $.parseJSON(_data);
         var topic = _data['topic'];
          // to/ui/from/agent_id/device_status_response
         // to/ui/from/agent_id/device_update_response
         if (topic) {
             topic = topic.split('/');
             console.log(topic);

             if (topic[3] == agent_id && topic[4] == 'device_status_response') {
                 if ($.type( _data['message'] ) === "string"){
                     var _message = $.parseJSON(_data['message']);
                     if ($.type(_message) != "object"){
                         _message = $.parseJSON(_message)
                     }
                     change_status(_message);
                 } else if ($.type( _data['message'] ) === "object"){
                     change_status(_data['message']);
                 }

             }
         }
     };

     function change_status(device_data) {
		if (device_data.occupied == 'OCCUPIED') {
			$("#occupied").show();
			$("#unoccupied").hide();
		} else {
			$("#occupied").hide();
			$("#unoccupied").show();
		}
		if (device_data.status == 'ON') {
			$("#on").show();
			$("#off").hide();
		} else {
			$("#on").hide();
			$("#off").show();
		}
		if (device_data.door == 'OPEN') {
            $("#door_open").css('background-color', 'green');
            $("#door_close").css('background-color', 'rgba(222, 222, 222, 0.55)');
		}else {
			$("#door_close").css('background-color','green');
			$("#door_open").css('background-color','rgba(222, 222, 222, 0.55)');
           }
		$("#illumination").text(device_data.Illumination);
		$("#temperature").text(device_data.temperature);
		$("#humidity").text(device_data.humidity);
	}

});
