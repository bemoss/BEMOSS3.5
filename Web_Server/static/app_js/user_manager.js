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

    $('.dropdown-menu li').click(function (event) {
        event.preventDefault();
        var $target = $(event.currentTarget);
        $target.closest('.btn-group')
            .find('[data-bind="label"]').text($target.text())
            .end()
            .children('.dropdown-toggle').dropdown('toggle');

        return false;
    });

    //$('.display').on('click', "a[id^='zonemanager-']" , function() {
    $("a[id^='zonemanager-']").click(function(e) {
        e.preventDefault();// prevent the default anchor functionality
        var this_id = this.id.split("-");
        var user_id = this_id[1];
        $("#ca_panel-" + user_id).show();
        $("#ca_req-" + user_id).show();
    });

    $("a[id^='admin-']").click(function(e) {
        e.preventDefault();// prevent the default anchor functionality
        var this_id = this.id.split("-");
        var user_id = this_id[1];
        $("#ca_panel-" + user_id).hide();
        $("#ca_req-" + user_id).hide();
    });

    $("a[id^='tenant-']").click(function(e) {
        e.preventDefault();// prevent the default anchor functionality
        var this_id = this.id.split("-");
        var user_id = this_id[1];
        $("#ca_panel-" + user_id).hide();
        $("#ca_req-" + user_id).hide();
    });

    $("#approve_users").click(function(e) {
        e.preventDefault();
        var values = [];
        var approve = false;
        $("#newusrs_tbl").find('tr').each(function (rowIndex, r) {
            approve = false;
            var cols = [];
            $(this).find("input[id^='approve_']").each(function () {
                if ($(this).is(':checked')){
                   var usr_id = this.id;
                   usr_id = usr_id.split("_");
                   cols.push(usr_id[1]);
                   cols.push("true");
                   approve = true;
                }
            });
            if (approve) {
                $(this).find("span[id^='role-']").each(function () {
                    cols.push($(this).text());
                });
                $(this).find("span[id^='zone-']").each(function () {
                    cols.push($(this).text());
                });
            }
            if (cols.length!=0) {
                values.push(cols);
            }
            console.log(values);

        });
           values = {
               "data": values
           };
        var jsonText = JSON.stringify(values);

            console.log(jsonText);
            $.ajax({
			  url : url_approve_users,
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

    });


     $("#modify_roles").click(function(e) {
        e.preventDefault();
        var values = [];
        var modify = false;
        $("#allusrs_tbl").find('tr').each(function (rowIndex, r) {
            var cols = [];
            // $(this).find("input[id^='modify_']").each(function () {
            //     if ($(this).is(':checked')){
            //        var usr_id = this.id;
            //        usr_id = usr_id.split("_");
            //        cols.push(usr_id[1]);
            //        modify = true;
            //     }
            // });
            if ($(this).find("span[id^='role-']").length) {
                cols.push($(this).find("td[id^='userid']").text());
                cols.push($(this).find("span[id^='role-']").text());
                cols.push($(this).find("span[id^='zone-']").text());

                if (cols.length != 0) {
                    values.push(cols);
                }
                console.log(values);
            }

        });

         values = {
               "data": values
           };
        var jsonText = JSON.stringify(values);

            console.log(jsonText);
            $.ajax({
              url : url_modify_user_permissions,
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





    });

    $(".delete_user").click(function(e) {
        e.preventDefault();
        var values = [];
        var user_id = this.id;
        user_id = user_id.split("_");
        user_id = user_id[1];

        values = {
           "id": user_id
        };
        var jsonText = JSON.stringify(values);

            console.log(jsonText);
            $.ajax({
			  url : url_delete_users,
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
				//window.location.reload(true);
			  	$('.bottom-right').notify({
			  	    message: { text: 'The user was removed from BEMOSS.' },
			  	    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
			  	  }).show();
                  setTimeout(function(){
                         window.location.reload();
                }, 3000);
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The user could not be removed at the moment. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });

    });


});
