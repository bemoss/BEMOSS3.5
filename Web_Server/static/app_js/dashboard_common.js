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
//The following function definations are from bootstrap-notify.p, copied here for quick fix for importing problem//
      var setTimeOut_identifier;
      var Notification = function (element, options) {
        // Element collection
        this.$element = $(element);
        this.$note    = $('<div class="alert"></div>');
        this.options  = $.extend(true, {}, $.fn.notify.defaults, options);

        // Setup from options
        if(this.options.transition)
          if(this.options.transition == 'fade')
            this.$note.addClass('in').addClass(this.options.transition);
          else this.$note.addClass(this.options.transition);
        else this.$note.addClass('fade').addClass('in');

        if(this.options.type)
          this.$note.addClass('alert-' + this.options.type);
        else this.$note.addClass('alert-success');

        if(!this.options.message && this.$element.data("message") !== '') // dom text
          this.$note.html(this.$element.data("message"));
        else
          if(typeof this.options.message === 'object')
            if(this.options.message.html)
              this.$note.html(this.options.message.html);
            else if(this.options.message.text)
              this.$note.text(this.options.message.text);
          else
            this.$note.html(this.options.message);

        if(this.options.closable)
          var link = $('<a class="close pull-right" href="#">&times;</a>');
          $(link).on('click', $.proxy(onClose, this));
          this.$note.prepend(link);

        return this;
      };

      var onClose = function() {
        this.options.onClose();
        $(this.$note).remove();
        this.options.onClosed();
        return false;
      };

      Notification.prototype.show = function () {
        if(this.options.fadeOut.enabled)
          this.$note.delay(this.options.fadeOut.delay || 3000).fadeOut('slow', $.proxy(onClose, this));

        this.$element.append(this.$note);
        //this.$note.alert();
      };

      Notification.prototype.hide = function () {
        if(this.options.fadeOut.enabled)
          this.$note.delay(this.options.fadeOut.delay || 3000).fadeOut('slow', $.proxy(onClose, this));
        else onClose.call(this);
      };

      $.fn.notify = function (options) {
        return new Notification(this, options);
      };

      $.fn.notify.defaults = {
        type: 'success',
        closable: true,
        transition: 'fade',
        fadeOut: {
          enabled: true,
          delay: 3000
        },
        message: null,
        onClose: function () {},
        onClosed: function () {}
      };

//end-of-bootstrap-notify.py copy//

    var ws = new WebSocket("ws://" + window.location.host + "/generic_socket/identify_response/from/");

     ws.onopen = function () {
         ws.send("WS opened from html page");
     };

     ws.onmessage = function (event) {
         //alert("get data from agent")
         var _data = event.data;
         try {
             _data = $.parseJSON(_data);
         }catch(err){

             return
         }
         var topic = _data['topic'];
         // ["", "agent", "ui", device_type, command, building_name, zone_id, agent_id]
         if (topic) {
             topic = topic.split('/');
             "to/ui/identify_response/from/agnet_id"
             console.log(topic);
             if (topic[2] == 'identify_response') {
                //stop Identification
                 //notify done
                 agent_id = topic[4];
                 identifier = "identify-"+agent_id;
                 $('#' + agent_id + "-spin").removeClass('fa fa-spinner fa-spin').addClass('icon-search');
                 $('#' + identifier).removeClass('btn-success disabled').addClass('btn-warning');
                 clearTimeout(setTimeOut_identifier);
                 $('.bottom-right').notify({
                        message: { text: 'Device Identification complete' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
             }

         }
     };


    var nick_re = /^[A-Za-z0-9_]{6,15}$/;

    $( ".save_changes" ).click(function(evt) {
		evt.preventDefault();
		values = this.id.split('-');
		agent_id = values[1];
        device_type = values[2];
		values = values[1]+"_nickname";
		var value_er = values;
		nickname = $("#"+values).val();
		var error_id = "viewediterror_" + agent_id;
		if (!nick_re.test(nickname)) {
			document.getElementById(error_id).innerHTML = "Nickname error. Please try again.";
			document.getElementById(values).value = "";
		} else {
		values = {
			    "id": agent_id,
			    "nickname": nickname,
                "device_type": device_type
			    };
		document.getElementById(error_id).innerHTML = "";
	    var jsonText = JSON.stringify(values);
		$.ajax({
			  url : save_view_edit_changes_dashboard,
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
				if (data == "invalid") {
					document.getElementById(error_id).innerHTML = "Nickname error. Please try again.";
					document.getElementById(value_er).value = "";
				} else {
				req_value_modal = data.agent_id+"_nick"
				req_val_stats = data.agent_id + "_nickname_header";
              	var newtest = document.getElementById(req_value_modal);
              	document.getElementById(req_val_stats).innerHTML = nickname.charAt(0).toUpperCase()+nickname.slice(1);
            	newtest.innerHTML = nickname.charAt(0).toUpperCase()+nickname.slice(1);
			  	$('.bottom-right').notify({
			  	    message: { text: 'Heads up! The device nickname change was successful.' },
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

    $(".identify").click(function (evt) {
        evt.preventDefault();
        var identifier = (this).id;
        identify_id = identifier.split("-");
        agent_id = identify_id[1];
        //alert(identify_id);
        values = {
            "agent_id": agent_id,
        };
        var jsonText = JSON.stringify(values);
        $.ajax({
            url: url_identify_device,
            type: 'POST',
            data: jsonText,
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {
                //alert(data);

                if (data.indexOf("success") > -1) {
                    $('#' + identify_id + "-spin").addClass('fa fa-spinner fa-spin').removeClass('icon-search');
                    //$('#'+identify_id+"-spin").removeClass('icon-search');
                    $("#" + identifier).removeClass('btn-warning').addClass('btn-success disabled');

                    setTimeOut_identifier = setTimeout(function () {
                        $('.bottom-right').notify({
                            message: { text: 'Device did not reply back!'},
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();
                        $('#' + identify_id + "-spin").removeClass('fa fa-spinner fa-spin').addClass('icon-search');
                        $('#' + identifier).removeClass('btn-success disabled').addClass('btn-warning');

                    }, 30000);
                    $('.bottom-right').notify({
                        message: { text: 'Communicating with the device for identification...' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();

                    //clearInterval(setTimeOut_identifier);
                }
            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: { text: 'Oh snap! Try again. ' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });
    });

        //      $(function () {
        //    $("#sortable1").sortable({
        //        connectWith: ".connectedSortable"
        //    }).disableSelection();
        //
        //});

        $(".panel").mousemove(function (e) {
            if (e.which == 1) {
                if ($(".panel-collapse").hasClass("collapse")) {
                    $(".panel-collapse").removeClass("collapse");
                    $(".panel-collapse").addClass("in");
                    $(".panel-body").show();
                    //alert("testing");
                }

            } else {

                $(".panel-body").mouseenter(function (e) {
                    if (e.which == 1) {
                        $(".panel-body").show();
                    }
                });
            }
        });

});