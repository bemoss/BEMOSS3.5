/**

 *  Authors: BEMOSS Team
 *  Version: 2.0
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
        console.log(item);
        $.each(item, function(j, sch_range) {
            console.log(sch_range);
            console.log(j);
            var tp_id = j.split("_");

            var compare_val = "tp_" + tp_id[0] + "_schedule_" + tp_id[1];
            console.log(compare_val);
            //var disabled_range = [];
            var disabled_range = generateTimeRangesforDisabling(sch_range);
            console.log(sch_range);
            console.log(disabled_range);

            $("input[id^=" + compare_val + "]").timepicker({
                    timeFormat: 'H:i',
                     step: stepInterval,
                     minTime: '00:00',
                     maxTime: '23:59',
                     useSelect: 'True',
                     //disableTimeRanges: [['05:30','06:30'],['13:30','14:30'] ]
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
                //$('#weekdayweekend_check').prop('checked',false);
            }
            /*if (item == 'weekdayweekend') {
                $('#everyday_check').prop('checked',false);
                $('#weekdayweekend_check').prop('checked',true);
            }*/
            if (item == 'holiday') {
                $('#holiday_check').prop('checked',true);
            }
    });

    var setHeight = $("#actt").height();
    $("#dispp").height(setHeight+'px');

    $("button[id^='reduce_']").click(function() {
			var temp_temp = this.id.split("_");
			var temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
			var temp_value = $("#"+ temp_id).text();

            var currentVal = parseFloat(temp_value);
            // If it isn't undefined or its greater than 0
            if (!isNaN(currentVal) && currentVal > 35) {
                // Decrement one
                $("#"+ temp_id).text(currentVal - 1);
            } else {
                // Otherwise put a 0 there
                $("#"+ temp_id).text(35);
            }

            //$("#"+ temp_id).text(parseInt(temp_value)-1);
    });

    $("button[id^='increase_']").click(function() {
        temp_temp = this.id.split("_");
        temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
        temp_value = $("#"+ temp_id).text();

        var currentVal = parseFloat(temp_value);
        if (!isNaN(currentVal) && currentVal < 95) {
            // Increment
           $("#"+ temp_id).text(currentVal + 1);
        } else {
            // Otherwise put the greatest value possible there
           $("#"+ temp_id).text(95);
        }

        //$("#"+ temp_id).text(parseInt(temp_value)+1);
    });

}

$( document ).ready(function() {

    $.csrftoken();

    /*$("#everyday_check").on('click', function(e) {
       if ($("#weekdayweekend_check").prop('checked')) {
            $('#weekdayweekend_check').prop('checked', false);
       }
    });

    $("#weekdayweekend_check").on('click', function(e) {
       if ($("#everyday_check").prop('checked')) {
            $('#everyday_check').prop('checked', false);
       }
    });*/

    $('#activate_schedules').on('click', function(e) {
        e.preventDefault();
        var to_activate = [];
        var to_make_inactive = [];
        if ($('#everyday_check').prop('checked')) {
            to_activate.push('everyday');
            /* to_make_inactive.push('weekdayweekend');
             } else if ($('#weekdayweekend_check').prop('checked')) {
             to_make_inactive.push('everyday');
             to_activate.push('weekdayweekend');
             } else {
             to_make_inactive.push('everyday');
             to_make_inactive.push('weekdayweekend');
             } */
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
			  url : '/submit_active_schedule/',
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
                  } else if (item == 'everyday'){
                      typ_sch = 'Daily';
                  } else {
                      typ_sch = item.charAt(0).toUpperCase() + item.substring(1);
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
		//alert(parent);
        console.log(parent);
        //check_rows = $('#monday_heat table tbody ').children();

		var req_table = parent.split('_');
		req_table = req_table[0] + '_schedule_' + req_table[1];
		//var table = document.getElementById(req_table).children()[1];
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
		//var row = table.insertRow(noOfRows);
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
        cell1.className = 'col-sm-1';
        cell2.className = 'col-sm-3';
        cell3.className = 'col-sm-3';
        cell4.className = 'col-sm-4';
        cell5.className = 'col-md-1';


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
	    //temp_value = current_data[i][1];
		cell4.innerHTML = '<span class="h4" id="temp_' + table.parentNode.id + '_' + new_tr_id + '">' + '70' + '</span><span class="h4">&deg;F</span>  <button class="btn btn-sm btn-primary" type="button" id="reduce' +  "_" + table.parentNode.id + "_" + new_tr_id + '"> - </button> '+
		'<button class="btn btn-sm btn-warning" type = "button" id="increase_' + table.parentNode.id + '_' + new_tr_id + '"> + </button>' ;

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

        //sdisrange = generateTimeRangesforDisabling(disabled_values[disabled_time_lookup]);

        compare_val = 'tp_' + table.parentNode.id + '_';

        $("input[id^=" + compare_val + "]").timepicker(
            'option', 'disableTimeRanges', sdisrange
        );

        $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');

		$('#' + 'reduce_' + table.parentNode.id + '_' + new_tr_id).click(function() {
			temp_temp = this.id.split("_");
			temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
			temp_value = $("#"+ temp_id).text();
			var currentVal = parseFloat(temp_value);
            // If it isn't undefined or its greater than 0
            if (!isNaN(currentVal) && currentVal > 35) {
                // Decrement one
                $("#"+ temp_id).text(currentVal - 1);
            } else {
                // Otherwise put a 0 there
                $("#"+ temp_id).text(35);
            }

			//$("#"+ temp_id).text(parseInt(temp_value)-1);
		});

		$('#' + 'increase_' + table.parentNode.id + '_' + new_tr_id).click(function() {
			temp_temp = this.id.split("_");
			temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
			temp_value = $("#"+ temp_id).text();
			var currentVal = parseFloat(temp_value);
            if (!isNaN(currentVal) && currentVal < 95) {
                // Increment
               $("#"+ temp_id).text(currentVal + 1);
            } else {
                // Otherwise put the greatest value possible there
               $("#"+ temp_id).text(95);
            }
			//$("#"+ temp_id).text(parseInt(temp_value)+1);
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
        var tget_id = get_id[1] + '_' + get_id[3];

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

        var compare_val = 'tp_' + get_id[1] + '_schedule_' + get_id[3] + '_';

        $("input[id^=" + compare_val + "]").timepicker(
            'option', 'disableTimeRanges', sdisrange
        );

        $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');
        //console.log(disabled_values[tget_id]);
    });

     $('.table').on('click', '.delete_td', function(e) {
    //$(".delete_td").on('click', function(e) {
        e.preventDefault();
        var tp_id = this.id;
        tp_id = tp_id.replace('delete','tp');
        var tp_val = $("#"+tp_id).val();
        t_old_value = convertTimeToMinutes(tp_val);
        console.log('oldvalue ' + t_old_value);

        var get_id = tp_id.split('_');
        tget_id = get_id[1] + '_' + get_id[3];

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

        var compare_val = 'tp_' + get_id[1] + '_schedule_' + get_id[3] + '_';

        $("input[id^=" + compare_val + "]").timepicker(
            'option', 'disableTimeRanges', sdisrange
        );

        $('.ui-timepicker-select').addClass('btn btn-default dropdown-toggle');


    });


    function schedule_updated(data_sent){
		var setTimeOut_schedule = setTimeout(function()
		{
			$.ajax({
			  url : '/update_schedule/',
			  type: 'POST',
			  data : data_sent,
			  success : function(data) {
				var update_status = data.status;
			  	if (update_status.indexOf("success") > -1){
			  		stopTimer('setTimeOut_schedule');
				  	$('.bottom-right').notify({
				  	    message: { text: 'The changes you made at '+update_time+' have now been updated in BEMOSS. The device will be scheduled accordingly.'},
				  	    type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
				  	  }).show();
			  	} else {
                    schedule_updated(data_sent)
				  	/*$('.bottom-right').notify({
				  	    message: { text: 'The changes you made at '+update_time+" could not be scheduled currently. However your changes have been saved and will be activated when the scheduler is ready."},
				  	    type: 'blackgloss'
				  	  }).show();
				  	*/
			  	}
			  },
			  error: function(data) {

			  }
			 });
		},3000);
	}


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
            //root = root[1] + '_' + root[2];
            root= root[2];
            var json_root = {};
            json_root[root] = {
                'heat': {},
                'cool': {}
            };


            //heat
            var noOfRows_heat = $("#" + root + "_schedule_heat tbody").children().length;
            console.log(noOfRows_heat);
            json_root[root]['heat'] = [];
            for (var j = 0; j <= noOfRows_heat-1; j++) {
                var tr_id = '#' + root + '_schedule_heat tbody tr:eq(' + j + ') td:first';
                console.log( tr_id);
                tr_id = $(tr_id).text();
                console.log(tr_id);
                var nickname = $("#nickname_" + root + "_schedule_heat_" + tr_id).val();
                var at = $("#tp_" + root + "_schedule_heat_" + tr_id).val();
                at = at.split(':');
                at = ((parseInt(at[0]) * 60) + parseInt(at[1])).toString();
                var set_point = $("#temp_" + root + "_schedule_heat_" + tr_id).text();
                console.log(set_point);
                var json_current = {};
                json_current = {
                    'id':tr_id,
                    'nickname': nickname,
                    'at': at,
                    'setpoint': set_point
                };

                json_root[root]['heat'].push(json_current);
               // json_root[root]['heat'][j] = json_current;

                console.log(json_current);
                console.log(json_root);
            }

            everyday[root] = json_root[root];

            var noOfRows_cool = $("#" + root + "_schedule_cool tbody").children().length;
            console.log(noOfRows_cool);

            json_root[root]['cool'] = [];
            for (j = 0; j <= noOfRows_cool-1; j++) {
                var tr_id = '#' + root + '_schedule_cool tbody tr:eq(' + j + ') td:first';
                console.log( tr_id);
                tr_id = $(tr_id).text();
                console.log(tr_id);
                nickname = $("#nickname_" + root + "_schedule_cool_" + tr_id).val();
                at = $("#tp_" + root + "_schedule_cool_" + tr_id).val();
                at = at.split(':');
                at = ((parseInt(at[0]) * 60) + parseInt(at[1])).toString();
                set_point = $("#temp_" + root + "_schedule_cool_" + tr_id).text();
                json_current = {};
                json_current = {
                    'id':tr_id,
                    'nickname': nickname,
                    'at': at,
                    'setpoint': set_point
                };

                json_root[root]['cool'].push(json_current);
                console.log(json_current);
                console.log(json_root);
            }

            everyday[root]['cool'] = json_root[root]['cool'];
        }

        var everyday_to_send = {};
        if (type == 'holiday'){
            everyday_to_send = everyday;
        } else {
            everyday_to_send[type] = everyday;
        }


        /*
		sch_val = {'heat': sch_heat ,'cool': sch_cool,'update_number':'to_be_added','device_info': device_info };
		//sch_val = {'heat': {'0':sch_heat.zero,'1':sch_heat.one,'2':sch_heat.two,'3':sch_heat.three,'4':sch_heat.four,'5':sch_heat.five,'6':sch_heat.six} ,'cool': {'0':sch_cool.zero,'1':sch_cool.one,'2':sch_cool.two,'3':sch_cool.three,'4':sch_cool.four,'5':sch_cool.five,'6':sch_cool.six}};
		return sch_val;*/
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
		//values = get_update_sch_everyday_values(type);
        values = {
            'schedule' : get_update_sch_everyday_values(type),
            'device_info' : device_info
        };
		console.log(values);
	    var jsonText = JSON.stringify(values);
		$.ajax({
			  url : '/submit_schedule/',
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
				schedule_updated(device_info);
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



});

