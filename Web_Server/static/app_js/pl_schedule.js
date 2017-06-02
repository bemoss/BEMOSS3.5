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


const stepInterval =30;
var t_old_value = -1;

Array.prototype.remove = function(avalue) {
    var idx = this.indexOf(avalue);
    if (idx !=-1){
        return this.splice(idx,1);
    }
    return false;
};

function convertMinutestoTime(numTime){
    var sminutes = numTime % 60;
    var shours = Math.floor(numTime / 60);
    sminutes = (sminutes < 10 ? '0' : '') + sminutes;
    shours = (shours < 10 ? '0' : '') + shours;
    var stringTime = shours + ':' + sminutes;
    //console.log(stringTime);
    return stringTime.toString();
}

function convertTimeToMinutes(strTime){
    var tstring = strTime.split(':');
    var tminutes = parseInt(tstring[1]);
    var thours = parseInt(tstring[0]);
    var ttime = thours*60 + tminutes;
    //console.log("Minutes  = " + ttime);
    return ttime;
}

function generateTimeRangesforDisabling(arrDisRange){
    var ilength = arrDisRange.length;
     var sdisabledrange = new Array(ilength);
    for (var i = 0; i < ilength; i++) {
        var new_array = new Array(2);
        if (arrDisRange[i]==0)
        {
            new_array = [convertMinutestoTime(0),convertMinutestoTime(1) ] ;
        }
        else {
            new_array = [convertMinutestoTime(arrDisRange[i] - stepInterval / 2), convertMinutestoTime(arrDisRange[i] + stepInterval / 2)];
        }
        //console.log(new_array);
        sdisabledrange[i] = new_array;
    }
    //console.log(sdisabledrange);
    return sdisabledrange;
}

function getNewTimePeriod(disabledRange) {
    var disabledArray = disabledRange;
    for(var idx=0; idx<1440; idx+=stepInterval){
        if (disabledArray.indexOf(idx) < 0) return idx;
    }
    return -1;
}

$(onStart); //short-hand for $(document).ready(onStart);

function onStart($) {

    $.each(disabled_ranges, function(i, item) {
        $.each(item, function(j, sch_range) {
            var compare_val = "tp_" + j + "_schedule";
            var disabled_range = generateTimeRangesforDisabling(sch_range);
            $("input[id^=" + compare_val + "]").timepicker({
                    timeFormat: 'H:i',
                     step: stepInterval,
                     minTime: '00:00',
                     maxTime: '23:59',
                     useSelect: 'True',
                    disableTimeRanges: disabled_range

                 });
        });
    });

     $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');


	$('#sortable-todo li input').on('click', function(e) {

        if($(this).is(":checked"))
		{
			$("#sortable-todo li.todo-list-active").removeClass('todo-list-active');
			$(this).closest('li').addClass('todo-list-active');

		}
	});


    $.each(active_schedule, function(index, item) {

            if (item == 'everyday') {
                $('#everyday_check').prop('checked',true);
            }

            if (item == 'holiday') {
                $('#holiday_check').prop('checked',true);
            }
    });

    var setHeight = $("#actt").height();
    $("#dispp").height(setHeight+'px');

    $("button[id^='off_']").click(function() {
			var off = this.id.split("_");
            var on = "on_" + off[1] + "_" + off[2] + "_" + off[3];
            if ($(this).hasClass('btn-success')) {
                $(this).removeClass('btn-success').addClass('btn-default');
                $('#' + on).removeClass('btn-default').addClass('btn-success');
            } else {
                $(this).removeClass('btn-default').addClass('btn-success');
                $('#' + on).removeClass('btn-success').addClass('btn-default');
            }
    });

    $("button[id^='on_']").click(function() {
        var on = this.id.split("_");
            var off = "off_" + on[1] + "_" + on[2] + "_" + on[3];
            if ($(this).hasClass('btn-success')) {
                $(this).removeClass('btn-success').addClass('btn-default');
                $('#' + off).removeClass('btn-default').addClass('btn-success');
            } else {
                $(this).removeClass('btn-default').addClass('btn-success');
                $('#' + off).removeClass('btn-success').addClass('btn-default');
            }
    });

}

$( document ).ready(function() {

    $.csrftoken();


    var ws = new WebSocket("ws://" + window.location.host + sch_socket);
    console.log("websocket connection established");
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
             if (topic[3] == device_data.agent_id && topic[4] == 'update_response') {
                 var message_upd = _data['message'];
                 var popup = false;
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
                     $('.bottom-right').notify({
				  	    message: { text: 'The changes you made at '+update_time+" have now been updated in BEMOSS. The device will be scheduled accordingly."},
				  	    type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
				  	  }).show();
                 }else{
                     $('.bottom-right').notify({
				  	    message: { text: 'Failed to update changes!'},
				  	    type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
				  	  }).show();
                 }

             }

         }
     };

    $('#activate_schedules').on('click', function(e) {
        e.preventDefault();
        var to_activate = [];
        var to_make_inactive = [];
        if ($('#everyday_check').prop('checked')) {
            to_activate.push('everyday');

        } else {
            to_make_inactive.push('everyday');
        }
        if ($('#holiday_check').prop('checked')) {
            to_activate.push('holiday');
        } else {
            to_make_inactive.push('holiday');
        }
        var update_time = new Date();
		update_time = update_time.toLocaleTimeString();
        var values = {'active': to_activate,
                  'inactive': to_make_inactive,
                  'device_info': device_info};
		console.log(values);
        console.log(to_activate);
	    var jsonText = JSON.stringify(values);
        $.ajax({
			  url : '/schedule/_activate_scheduler/',
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
              var to_append = '';
              $.each(to_activate, function(index, item) {
                    var typ_sch;
                  if (item == 'weekdayweekend'){
                      typ_sch = 'Weekday/Weekend';
                  }  else if (item == 'everyday'){
                      typ_sch = 'Daily';
                  } else {
                      typ_sch = item.charAt(0).toUpperCase() + item.substring(1);;
                  }
                  to_append = to_append + '<a class="shortcut"><br/><br/>' +
                      '<i class="shortcut-icon icon-list-alt"></i>' +
                      '<span class="shortcut-label"></span>' + typ_sch + '<br/><br/></a>'
              });
              $(".shortcuts").html(to_append);
			  $('.bottom-right').notify({
			  	    message: { text: 'The new settings will be activated shortly.' },
			  	    type: 'blackgloss',
                  fadeOut: { enabled: true, delay: 5000 }
			  	  }).show();
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The activation changes were not successful. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });

    });


    $('.add_new_period').click(function(evt) {
		evt.preventDefault();
		var parent = this.parentNode.parentNode.parentNode.id;
        console.log(parent);

		var req_table = parent;
		req_table = req_table + '_schedule';
        var table =$('#'+req_table).children()[1];
        console.log(table);
		var noOfRows = document.getElementById(req_table).rows.length;

        if (noOfRows > 7) {
            $('.bottom-right').notify({
				  	    message: { text: 'Maximum number of periods exceeded.'},
				  	    type: 'blackgloss',
                fadeOut: { enabled: true, delay: 5000 }
				  	  }).show();
            return false;
        }
        var tr_id = '#' + req_table + ' tbody tr:last td:first';
        console.log( tr_id);
        tr_id = $(tr_id).text();

        if (tr_id == '') {
            tr_id = 0;
        }
        var new_tr_id = parseInt(tr_id) + 1 ;


        var row = table.insertRow();
		var cell1 = row.insertCell(0);
		var cell2 = row.insertCell(1);
		var cell3 = row.insertCell(2);
		var cell4 = row.insertCell(3);
        var cell5 = row.insertCell(4);
        cell1.className = 'col-sm-1 td_id';
        cell2.className = 'col-sm-4 td_nickname';
        cell3.className = 'col-sm-3 td_tp';
        cell4.className = 'col-sm-3 td_status';
        cell5.className = 'col-sm-1 td_delete';


		cell1.innerHTML = new_tr_id;
		cell2.innerHTML = '<input type="text" id="nickname_' + table.parentNode.id + '_' + new_tr_id + '" name="nickname" style="width:100%" value="Period'+ new_tr_id +'"/>';

        var previous_row = parseInt(noOfRows)-1;
        var previous_value = $("#tp" + "_" + table.parentNode.id + "_" + tr_id).val();
        var disabled_time_lookup = table.parentNode.id.replace('_schedule','');

        var scheduler_type = $(this).parents('.dis_sch').attr('id');
        scheduler_type = scheduler_type.split('_');
        scheduler_type = scheduler_type[0];

        var newtimepickerval = getNewTimePeriod(disabled_ranges[scheduler_type][disabled_time_lookup]);
        console.log(newtimepickerval);

		var c3content=document.createElement("input");
		c3content.setAttribute("type","text");
		c3content.setAttribute("name","tp" + "_" + table.parentNode.id + "_" + new_tr_id);
		c3content.setAttribute("id","tp" + "_" + table.parentNode.id + "_" + new_tr_id);
		c3content.setAttribute("class","hasDatePicker");
		c3content.setAttribute("value",convertMinutestoTime(newtimepickerval));
        c3content.setAttribute("style",'width: 100%;');


	    cell3.appendChild(c3content);
        cell4.innerHTML = '<span id="on_off_div"><button class="btn btn-sm btn-success on_off_left" type="button" id="off_' + table.parentNode.id + '_' + new_tr_id + '"> OFF </button>&nbsp;' +
                                        '<button class="btn btn-sm btn-default on_off_left" type="button" id="on_' + table.parentNode.id + '_' + new_tr_id + '"> ON </button></span>';

        cell5.innerHTML = '<button class="btn btn-sm btn-danger delete_td" type="button" id="delete_' + table.parentNode.id + '_' + new_tr_id +'"> x </button>';

        var sdisrange = [];

        disabled_range = disabled_ranges[scheduler_type][disabled_time_lookup];
        disabled_range.push(newtimepickerval);
        disabled_ranges[scheduler_type][disabled_time_lookup] = disabled_range;
        sdisrange = generateTimeRangesforDisabling(disabled_ranges[scheduler_type][disabled_time_lookup]);
        console.log(sdisrange);
        console.log(disabled_ranges[scheduler_type][disabled_time_lookup]);

        var compare_val = "#tp" + "_" + table.parentNode.id + "_" + new_tr_id;

		$(compare_val).timepicker({
                     timeFormat: 'H:i',
                     step: stepInterval,
                     minTime: '00:00',
                     maxTime: '23:59',
                     useSelect: 'True',
                     disableTimeRanges: sdisrange
        });


        compare_val = 'tp_' + table.parentNode.id;

        $("input[id^=" + compare_val + "]").timepicker(
            'option', 'disableTimeRanges', sdisrange
        );

        $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');

        $('#off_' + table.parentNode.id + '_' + new_tr_id).click(function() {
            var off = this.id.split("_");
            var on = "on_" + off[1] + "_" + off[2] + "_" + off[3];
            if ($(this).hasClass('btn-success')) {
                $(this).removeClass('btn-success').addClass('btn-default');
                $('#' + on).removeClass('btn-default').addClass('btn-success');
            } else {
                $(this).removeClass('btn-default').addClass('btn-success');
                $('#' + on).removeClass('btn-success').addClass('btn-default');
            }
        });

        $('#on_' + table.parentNode.id + '_' + new_tr_id).click(function() {
            var on = this.id.split("_");
            var off = "off_" + on[1] + "_" + on[2] + "_" + on[3];
            if ($(this).hasClass('btn-success')) {
                $(this).removeClass('btn-success').addClass('btn-default');
                $('#' + off).removeClass('btn-default').addClass('btn-success');
            } else {
                $(this).removeClass('btn-default').addClass('btn-success');
                $('#' + off).removeClass('btn-success').addClass('btn-default');
            }
        });



	    });


    $('.table').on('showTimepicker', '.hasDatePicker', function() {
        t_old_value = $(this).val();
        t_old_value = convertTimeToMinutes(t_old_value);
        console.log('oldvalue ' + t_old_value);
    });

    $('.table').on('changeTime', '.hasDatePicker', function() {

        var get_id = this.id;
        get_id = get_id.split('_');
        var tget_id = get_id[1];

        var scheduler_type = $(this).parents('.dis_sch').attr('id');
        scheduler_type = scheduler_type.split('_');
        scheduler_type = scheduler_type[0];

        var to_push = $(this).val();
        to_push = convertTimeToMinutes(to_push);

        disabled_range = disabled_ranges[scheduler_type][tget_id];
        disabled_range.push(to_push);
        disabled_ranges[scheduler_type][tget_id] = disabled_range;

        if (t_old_value > -1) {
            console.log('before remove');
            console.log(disabled_range);
            disabled_range.remove(t_old_value);
            console.log(disabled_range);
            disabled_ranges[scheduler_type][tget_id] = disabled_range;
            t_old_value = -1;
        }
        var sdisrange = [];
        sdisrange = generateTimeRangesforDisabling(disabled_ranges[scheduler_type][tget_id]);

        var compare_val = 'tp_' + get_id[1] + '_schedule_' ;

        $("input[id^=" + compare_val + "]").timepicker(
            'option', 'disableTimeRanges', sdisrange
        );

        $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');
        //console.log(disabled_values[tget_id]);
    });

     $('.table').on('click', '.delete_td', function(e) {
        e.preventDefault();
        var tp_id = this.id;
        tp_id = tp_id.replace('delete','tp');
        var tp_val = $("#"+tp_id).val();
        t_old_value = convertTimeToMinutes(tp_val);
        console.log('oldvalue ' + t_old_value);

        var get_id = tp_id.split('_');
        tget_id = get_id[1];

        var scheduler_type = $(this).parents('.dis_sch').attr('id');
        scheduler_type = scheduler_type.split('_');
        scheduler_type = scheduler_type[0];
        disabled_range = disabled_ranges[scheduler_type][tget_id];

        if (t_old_value > -1) {
            console.log('before remove');
            console.log(disabled_range);
            disabled_range.remove(t_old_value);
            console.log(disabled_range);
            disabled_ranges[scheduler_type][tget_id] = disabled_range;
            t_old_value = -1;
        }

        var sdisrange = [];
        sdisrange = generateTimeRangesforDisabling(disabled_ranges[scheduler_type][tget_id]);

        $(this).closest('tr').remove();

        var compare_val = 'tp_' + get_id[1] + '_schedule_';

        $("input[id^=" + compare_val + "]").timepicker(
            'option', 'disableTimeRanges', sdisrange
        );

        $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');


    });


	function stopTimer(setTimeOut_schedule) {
		clearInterval(setTimeOut_schedule);
	}

    function get_update_sch_everyday_values(type) {
        //New addition
        var everyday = {};

        var root_length = 0;
        var root_id;
        if (type == 'everyday') {
            root_length = $("div[id^='everydayy_']").length;
            root_id = 'everydayy_';
        } else if (type == 'weekdayweekend') {
            root_length = $("div[id^='weekdayweekendd_']").length;
            root_id = 'weekdayweekendd_';
        } else if (type == 'holiday') {
            root_length = $("div[id^='holiday_0']").length;
            root_id = 'holiday_0';
        }


        for (var i = 0; i < root_length; i++) {
            var root = $("div[id^=" + root_id + "]")[i].id;
            root = root.split('_');
            root = root[2];
            var json_root = {};
            json_root[root] = [];


            //heat
            var noOfRows = $("#" + root + "_schedule tbody").children().length;
            console.log(noOfRows);
            for (var j = 0; j <= noOfRows - 1; j++) {
                var tr_id = '#' + root + '_schedule tbody tr:eq(' + j + ') td:first';
                console.log(tr_id);
                tr_id = $(tr_id).text();
                console.log(tr_id);
                var nickname = $("#nickname_" + root + "_schedule_" + tr_id).val();
                var at = $("#tp_" + root + "_schedule_" + tr_id).val();
                if (at != '0') {
                    at = at.split(':');
                    at = ((parseInt(at[0]) * 60) + parseInt(at[1])).toString();
                }
                var status = 'OFF';
                if ($("#off_" + root + "_schedule_" + tr_id).hasClass('btn-success')) {
                    status = 'OFF'
                } else if ($("#on_" + root + "_schedule_" + tr_id).hasClass('btn-success')) {
                    status = 'ON';
                }

                var json_current = {};
                json_current = {
                    'id': tr_id,
                    'nickname': nickname,
                    'at': parseInt(at),
                    'status': status};

                json_root[root].push(json_current);

                console.log(json_current);
                console.log(json_root);
            }

            everyday[root] = json_root[root];

            var everyday_to_send = {};

            everyday_to_send[type] = everyday;

        }
            return everyday_to_send;

    }

    //$( "#submit_new_schedule" ).click(function(evt) {
    $( ".individual" ).click(function(evt) {
		evt.preventDefault();
        var type = this.id;
        type = this.id.split('_');
        type = type[1];
		update_time = new Date();
		update_time = update_time.toLocaleTimeString();
        values = {
            'schedule' : get_update_sch_everyday_values(type),
            'device_info' : device_info,
            'user': user
        };
		console.log(values);
	    var jsonText = JSON.stringify(values);
		$.ajax({
			  url : url_schedule_submit,
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
			  	console.log(data.heat);
			  	$('.bottom-right').notify({
			  	    message: { text: 'Your schedule will be updated in BEMOSS shortly.' },
			  	    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
			  	  }).show();
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The scheduling was not successful. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show();
			  }
			 });
	});

    $( ".apply_weekday" ).click(function(evt) {
		evt.preventDefault();
        var days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
        schedule_duplicate(days)
	});

    $( ".apply_weekend" ).click(function(evt) {
		evt.preventDefault();
        var days = ['saturday', 'sunday'];
        schedule_duplicate(days)

    });

    $( ".apply_allday" ).click(function(evt) {
		evt.preventDefault();
        var days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        schedule_duplicate(days)

    });

    function schedule_duplicate(days) {
        var type = 'everyday';
        root_length = $("div[id^='everydayy_']").length;
        root_id = 'everydayy_';

        var sch_list = ['mon_sch', 'tue_sch', 'wed_sch', 'thu_sch', 'fri_sch', 'sat_sch', 'sun_sch'];
        for (var idx = 0, j = sch_list.length; idx < j; idx++) {
            if (document.getElementById(sch_list[idx]).className == 'active') {
                var active_sch = idx;
                break;
            }
        }

        var i = active_sch;
        var root = $("div[id^=" + root_id + "]")[i].id;
        root = root.split('_');
        root = root[2];
        var json_root = {};
        json_root[root] = [];
        var noOfRows = $("#" + root + "_schedule tbody").children().length;
        for (var j = 0; j <= noOfRows - 1; j++) {
            var tr_id = '#' + root + '_schedule tbody tr:eq(' + j + ') td:first';
            tr_id = $(tr_id).text();
            var nickname = $("#nickname_" + root + "_schedule_" + tr_id).val();
            var at = $("#tp_" + root + "_schedule_" + tr_id).val();
            if (at != '0') {
                at = at.split(':');
                at = ((parseInt(at[0]) * 60) + parseInt(at[1])).toString();
            }
            var status = 'OFF';
            if ($("#off_" + root + "_schedule_" + tr_id).hasClass('btn-success')) {
                status = 'OFF'
            } else if ($("#on_" + root + "_schedule_" + tr_id).hasClass('btn-success')) {
                status = 'ON';
            }

            var json_current = {};
            json_current = {
                'id': tr_id,
                'nickname': nickname,
                'at': parseInt(at),
                'status': status
            };

            json_root[root].push(json_current);

        }

        var sch_apply = json_root[root];
        console.log(sch_apply);

        for (var day = 0; day < days.length; day++) {
            var parent = days[day];

            var req_table = parent;
            req_table = req_table + '_schedule';
            var table = $('#' + req_table).children()[1];
            console.log(table);
            var noOfRows = document.getElementById(req_table).rows.length;

            // Delete original schedule.
            for (var j = 1; j <= noOfRows - 1; j++) {
                var btid = 'delete_' + parent + '_schedule_' + j;
                var btn = document.getElementById(btid);
                btn.click();
            }

            for (var j = 0; j < sch_apply.length; j++) {

                var new_tr_id = sch_apply[j]["id"];

                var row = table.insertRow();
                var cell1 = row.insertCell(0);
                var cell2 = row.insertCell(1);
                var cell3 = row.insertCell(2);
                var cell4 = row.insertCell(3);
                var cell5 = row.insertCell(4);
                cell1.className = 'col-sm-1 td_id';
                cell2.className = 'col-sm-4 td_nickname';
                cell3.className = 'col-sm-3 td_tp';
                cell4.className = 'col-sm-3 td_status';
                cell5.className = 'col-sm-1 td_delete';


                cell1.innerHTML = new_tr_id;
                cell2.innerHTML = '<input type="text" id="nickname_' + table.parentNode.id + '_' + new_tr_id + '" name="nickname" style="width:100%" value="' + sch_apply[j]["nickname"] + '"/>';

                var previous_row = parseInt(noOfRows) - 1;
                var previous_value = $("#tp" + "_" + table.parentNode.id + "_" + tr_id).val();
                var disabled_time_lookup = table.parentNode.id.replace('_schedule', '');

                var scheduler_type = "everyday";

                var newtimepickerval = sch_apply[j]["at"];

                var c3content = document.createElement("input");
                c3content.setAttribute("type", "text");
                c3content.setAttribute("name", "tp" + "_" + table.parentNode.id + "_" + new_tr_id);
                c3content.setAttribute("id", "tp" + "_" + table.parentNode.id + "_" + new_tr_id);
                c3content.setAttribute("class", "hasDatePicker");
                c3content.setAttribute("value", convertMinutestoTime(newtimepickerval));
                c3content.setAttribute("style", 'width: 100%;');


                cell3.appendChild(c3content);
                if (sch_apply[j]["status"] == "OFF") {
                    cell4.innerHTML = '<span id="on_off_div"><button class="btn btn-sm btn-success on_off_left" type="button" id="off_' + table.parentNode.id + '_' + new_tr_id + '"> OFF </button>&nbsp;' +
                        '<button class="btn btn-sm btn-default on_off_right" type="button" id="on_' + table.parentNode.id + '_' + new_tr_id + '"> ON </button></span>';
                } else {
                    cell4.innerHTML = '<span id="on_off_div"><button class="btn btn-sm btn-default on_off_left" type="button" id="off_' + table.parentNode.id + '_' + new_tr_id + '"> OFF </button>&nbsp;' +
                        '<button class="btn btn-sm btn-success on_off_right" type="button" id="on_' + table.parentNode.id + '_' + new_tr_id + '"> ON </button></span>';
                }

                cell5.innerHTML = '<button class="btn btn-sm btn-danger delete_td" type="button" id="delete_' + table.parentNode.id + '_' + new_tr_id + '"> x </button>';

                var sdisrange = [];

                disabled_range = disabled_ranges[scheduler_type][disabled_time_lookup];
                disabled_range.push(newtimepickerval);
                disabled_ranges[scheduler_type][disabled_time_lookup] = disabled_range;
                sdisrange = generateTimeRangesforDisabling(disabled_ranges[scheduler_type][disabled_time_lookup]);
                console.log(sdisrange);
                console.log(disabled_ranges[scheduler_type][disabled_time_lookup]);

                var compare_val = "#tp" + "_" + table.parentNode.id + "_" + new_tr_id;

                $(compare_val).timepicker({
                    timeFormat: 'H:i',
                    step: stepInterval,
                    minTime: '00:00',
                    maxTime: '23:59',
                    useSelect: 'True',
                    disableTimeRanges: sdisrange
                });


                compare_val = 'tp_' + table.parentNode.id;

                $("input[id^=" + compare_val + "]").timepicker(
                    'option', 'disableTimeRanges', sdisrange
                );

                $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');

                $('#off_' + table.parentNode.id + '_' + new_tr_id).click(function () {
                    var off = this.id.split("_");
                    var on = "on_" + off[1] + "_" + off[2] + "_" + off[3];
                    if ($(this).hasClass('btn-success')) {
                        $(this).removeClass('btn-success').addClass('btn-default');
                        $('#' + on).removeClass('btn-default').addClass('btn-success');
                    } else {
                        $(this).removeClass('btn-default').addClass('btn-success');
                        $('#' + on).removeClass('btn-success').addClass('btn-default');
                    }
                });

                $('#on_' + table.parentNode.id + '_' + new_tr_id).click(function () {
                    var on = this.id.split("_");
                    var off = "off_" + on[1] + "_" + on[2] + "_" + on[3];
                    if ($(this).hasClass('btn-success')) {
                        $(this).removeClass('btn-success').addClass('btn-default');
                        $('#' + off).removeClass('btn-default').addClass('btn-success');
                    } else {
                        $(this).removeClass('btn-default').addClass('btn-success');
                        $('#' + off).removeClass('btn-success').addClass('btn-default');
                    }
                });

            }
        }

    }

});

