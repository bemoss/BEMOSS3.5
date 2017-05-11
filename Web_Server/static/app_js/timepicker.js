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

$(onStart); //short-hand for $(document).ready(onStart);  
function onStart($) {  
    //alert("on start");
    //table_id:value from the server
    var th_schedule = [["monday_schedule_heat",sch_monday_heat], 
                       ["monday_schedule_cool",sch_monday_cool], 
                       ["tuesday_schedule_heat",sch_tuesday_heat], 
                       ["tuesday_schedule_cool",sch_tuesday_cool], 
                       ["wednesday_schedule_heat",sch_wednesday_heat], 
                       ["wednesday_schedule_cool",sch_wednesday_cool], 
                       ["thursday_schedule_heat",sch_thursday_heat], 
                       ["thursday_schedule_cool",sch_thursday_cool], 
                       ["friday_schedule_heat",sch_friday_heat], 
                       ["friday_schedule_cool",sch_friday_cool], 
                       ["saturday_schedule_heat",sch_saturday_heat], 
                       ["saturday_schedule_cool",sch_saturday_cool], 
                       ["sunday_schedule_heat",sch_sunday_heat], 
                       ["sunday_schedule_cool",sch_sunday_cool]];

    
    for (var j = 0; j < 14; j++) {
        //alert(th_schedule[j]);
        //var table_id = "\"" + th_schedule[j][0] + "\"";
        var table_id = th_schedule[j][0];
        //alert(table_id);
        var table = document.getElementById(table_id);
        //alert(table.rows.length);
    	var noOfRows = table.rows.length;

    	var current_data = th_schedule[j][1];
    	var no_of_periods = current_data.length;
    	console.log("no of periods"+no_of_periods);
    	
    	
    	for (var i = 0; i < no_of_periods; i++) {

    		noOfRows = document.getElementById(table_id).rows.length;

    		var row = table.insertRow(noOfRows);
    		var cell1 = row.insertCell(0);
    		var cell2 = row.insertCell(1);
    		var cell3 = row.insertCell(2);
    		var cell4 = row.insertCell(3);
    		var cell5 = row.insertCell(4);
    		var cell6 = row.insertCell(5);
    		
    		time = current_data[i][0];
    		if (time/60 < 12) {
    			if (time%60 < 10) {
    				time = '0' + Math.floor(time/60) + ':0' + time%60;
    			} else {
    				time = '0' + Math.floor(time/60) + ':' + time%60;
    			}
    		} else {
    			if (time%60 < 10) {
    				time = Math.floor(time/60) + ':0' + time%60;
    			} else {
    				time = Math.floor(time/60) + ':' + time%60;
    			}
    		}

    		cell1.innerHTML = noOfRows;
    		cell2.innerHTML = '<td><input type="text" id="nickname" name="nickname" value="Period'+ noOfRows +'"/></td>';

    		
    		var c3content=document.createElement("input");
    		c3content.setAttribute("type","text");
    		c3content.setAttribute("name","tp" + "_" + table_id + "_" + noOfRows);
    		c3content.setAttribute("id","tp" + "_" + table_id + "_" + noOfRows);  
    		c3content.setAttribute("class","hasDatePicker");
    		c3content.setAttribute("value",time);

    	    cell3.appendChild(c3content);
    	    //temp_value = current_data[i][1];
    		cell4.innerHTML = '<span class="h4" id="temp_' + table_id + '_' + noOfRows + '">' + current_data[i][1] + '</span>  <button class="btn btn-sm btn-primary" type="button" id="reduce' +  "_" + table_id + "_" + noOfRows + '"> - </button> '+
    		'<button class="btn btn-sm btn-warning" type = "button" id="increase_' + table_id + '_' + noOfRows + '"> + </button>';

    		$('.hasDatePicker').timepicker();
    		
    		$('#' + 'reduce_' + table_id + '_' + noOfRows).click(function() {
    			temp_temp = this.id.split("_");
    			temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
    			temp_value = $("#"+ temp_id).text();
    			$("#"+ temp_id).text(parseInt(temp_value)-1);
    		});
    		
    		$('#' + 'increase_' + table_id + '_' + noOfRows).click(function() {
    			temp_temp = this.id.split("_");
    			temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
    			temp_value = $("#"+ temp_id).text();
    			$("#"+ temp_id).text(parseInt(temp_value)+1);
    		});
    }
    
    
		
	}
};

	$('.add_new_period').click(function(evt) {
		evt.preventDefault();
		var parent = this.parentNode.parentNode.parentNode.id;
		//alert(parent);
		var req_table = parent.split('_');
		req_table = req_table[0] + '_schedule_' + req_table[1];
		var table = document.getElementById(req_table);
		noOfRows = document.getElementById(req_table).rows.length;
		var row = table.insertRow(noOfRows);
		var cell1 = row.insertCell(0);
		var cell2 = row.insertCell(1);
		var cell3 = row.insertCell(2);
		var cell4 = row.insertCell(3);
		var cell5 = row.insertCell(4);
		var cell6 = row.insertCell(5);
		
		cell1.innerHTML = noOfRows;
		cell2.innerHTML = '<td><input type="text" id="nickname" name="nickname" value="Period'+ noOfRows +'"/></td>';

		
		var c3content=document.createElement("input");
		c3content.setAttribute("type","text");
		c3content.setAttribute("name","tp" + "_" + table.id + "_" + noOfRows);
		c3content.setAttribute("id","tp" + "_" + table.id + "_" + noOfRows);  
		c3content.setAttribute("class","hasDatePicker");
		c3content.setAttribute("value",time);	

	    cell3.appendChild(c3content);
	    //temp_value = current_data[i][1];
		cell4.innerHTML = '<span class="h4" id="temp_' + table.id + '_' + noOfRows + '">' + '70' + '</span>  <button class="btn btn-sm btn-primary" type="button" id="reduce' +  "_" + table.id + "_" + noOfRows + '"> - </button> '+
		'<button class="btn btn-sm btn-warning" type = "button" id="increase_' + table.id + '_' + noOfRows + '"> + </button>';

		$('.hasDatePicker').timepicker();
		
		$('#' + 'reduce_' + table.id + '_' + noOfRows).click(function() {
			temp_temp = this.id.split("_");
			temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
			temp_value = $("#"+ temp_id).text();
			$("#"+ temp_id).text(parseInt(temp_value)-1);
		});
		
		$('#' + 'increase_' + table.id + '_' + noOfRows).click(function() {
			temp_temp = this.id.split("_");
			temp_id = "temp_"+temp_temp[1]+"_"+temp_temp[2]+"_"+temp_temp[3]+"_"+temp_temp[4];
			temp_value = $("#"+ temp_id).text();
			$("#"+ temp_id).text(parseInt(temp_value)+1);
		});
	
	});


	
$( document ).ready(function() {

	
	$.csrftoken();
	
	var sch_tbl_heat = ["monday_schedule_heat", 
	               "tuesday_schedule_heat",
	               "wednesday_schedule_heat",
                   "thursday_schedule_heat",
	               "friday_schedule_heat",
	               "saturday_schedule_heat",
	               "sunday_schedule_heat",
	               ];

	var sch_tbl_cool = ["monday_schedule_cool", 
	                    "tuesday_schedule_cool",
	                    "wednesday_schedule_cool",
	                    "thursday_schedule_cool",
	                    "friday_schedule_cool",
	                    "saturday_schedule_cool",
	                    "sunday_schedule_cool"];
	
	function schedule_updated(data_sent){
		var setTimeOut_schedule = setTimeout(function()
		{ 
			$.ajax({
			  url : '/update_schedule/',
			  type: 'POST',
			  data : data_sent,
			  //dataType : 'text',
			  success : function(data) {
				update_status = data.status;
			  	if (update_status=="success"){
			  		stopTimer('setTimeOut_schedule');
				  	$('.bottom-right').notify({
				  	    message: { text: 'The changes you made at '+update_time+" have now been updated in the device"},
				  	    type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
				  	  }).show();
			  	} else {
				  	$('.bottom-right').notify({
				  	    message: { text: 'The changes you made at '+update_time+" could not be updated in the device. Please try again!"},
				  	    type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
				  	  }).show(); 
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

	function get_update_sch_values() {
		var sch_heat = {zero:[],one:[],two:[],three:[],four:[],five:[],six:[]};
		var sch_cool = {zero:[],one:[],two:[],three:[],four:[],five:[],six:[]};
		
		for (var j = 0; j < 7; j++) {
			
	        var table_id = sch_tbl_heat[j];
	        var table = document.getElementById(table_id);
	        var noOfRows = table.rows.length;
	    	
	    	for (var i = 1; i < noOfRows; i++) {
	    		tp_val =  "tp_"  + table_id + '_' + i;
	    		tp_val = document.getElementById(tp_val).value;
	    		tp_val = tp_val.split(":");
	    		tp_val = ( parseInt(tp_val[0])*60)+ parseInt(tp_val[1]);
	    		temp_val = "temp_" + table_id + '_' + i;
	    		temp_val = parseInt(document.getElementById(temp_val).innerHTML);
	    		
	    		switch (table_id) {
	    		  case 'monday_schedule_heat':
	    			  sch_heat.zero.push(tp_val);
	    			  sch_heat.zero.push(temp_val);
	    			  break;
	    		  case 'tuesday_schedule_heat':
	    			  sch_heat.one.push(tp_val);
	    			  sch_heat.one.push(temp_val);
	    			  break;
	    		  case 'wednesday_schedule_heat':
	    			  sch_heat.two.push(tp_val);
	    			  sch_heat.two.push(temp_val);
	    			  break;
	    		  case 'thursday_schedule_heat':
	    			  sch_heat.three.push(tp_val);
	    			  sch_heat.three.push(temp_val);
	    			  break;
	    		  case 'friday_schedule_heat':
	    			  sch_heat.four.push(tp_val);
	    			  sch_heat.four.push(temp_val);
	    			  break;
	    		  case 'saturday_schedule_heat':
	    			  sch_heat.five.push(tp_val);
	    			  sch_heat.five.push(temp_val);
	    			  break;
	    		  case 'sunday_schedule_heat':
	    			  sch_heat.six.push(tp_val);
	    			  sch_heat.six.push(temp_val);
	    			  break;
	    		}
	    	}
	    	
		}
		
		//sch_heat = {'\'0\':[' sch_heat.zero.toString() + '],\'1\':[' + sch_heat.one.toString() + '],\'2\':[' + sch_heat.two.toString() + '],\'3\':[' + sch_heat.three.toString() + '],\'4\':[' + sch_heat.four.toString() + '],\'5\':[' + sch_heat.five.toString() + '],\'6\':[' + sch_heat.six.toString()+']'};
		sch_heat = {'0':sch_heat.zero,'1':sch_heat.one,'2':sch_heat.two,'3':sch_heat.three,'4':sch_heat.four,'5':sch_heat.five,'6':sch_heat.six};
		
		for (var j = 0; j < 7; j++) {
			
	        var table_id = sch_tbl_cool[j];
	        var table = document.getElementById(table_id);
	        var noOfRows = table.rows.length;
	    	
	    	for (var i = 1; i < noOfRows; i++) {
	    		tp_val =  "tp_"  + table_id + '_' + i;
	    		tp_val = document.getElementById(tp_val).value;
	    		tp_val = tp_val.split(":");
	    		tp_val = ( parseInt(tp_val[0])*60)+ parseInt(tp_val[1]);
	    		temp_val = "temp_" + table_id + '_' + i;
	    		temp_val = parseInt(document.getElementById(temp_val).innerHTML);
	    		
	    		switch (table_id) {
	    		  case "monday_schedule_cool":
	    			  sch_cool.zero.push(tp_val);
	    			  sch_cool.zero.push(temp_val);
	    			  break;
	    		  case "tuesday_schedule_cool":
	    			  sch_cool.one.push(tp_val);
	    			  sch_cool.one.push(temp_val);
	    			  break;
	    		  case "wednesday_schedule_cool":
	    			  sch_cool.two.push(tp_val);
	    			  sch_cool.two.push(temp_val);
	    			  break;
	    		  case "thursday_schedule_cool":
	    			  sch_cool.three.push(tp_val);
	    			  sch_cool.three.push(temp_val);
	    			  break;
	    		  case "friday_schedule_cool":
	    			  sch_cool.four.push(tp_val);
	    			  sch_cool.four.push(temp_val);
	    			  break;
	    		  case "saturday_schedule_cool":
	    			  sch_cool.five.push(tp_val);
	    			  sch_cool.five.push(temp_val);
	    			  break;
	    		  case "sunday_schedule_cool":
	    			  sch_cool.six.push(tp_val);
	    			  sch_cool.six.push(temp_val);
	    			  break;
	    		}
	    	}
	    	
		}
		//sch_cool = {'\'0\':[' + sch_cool.zero.toString() + '],\'1\':[' + sch_cool.one.toString() + '],\'2\':[' + sch_cool.two.toString() + '],\'3\':[' + sch_cool.three.toString() + '],\'4\':[' + sch_cool.four.toString() + '],\'5\':[' + sch_cool.five.toString() + '],\'6\':[' + sch_cool.six.toString()+']'};
		sch_cool = {'0':sch_cool.zero,'1':sch_cool.one,'2':sch_cool.two,'3':sch_cool.three,'4':sch_cool.four,'5':sch_cool.five,'6':sch_cool.six};
		//sch_val = '{\'heat\':{'+ sch_heat + '},\'cool\':{' + sch_cool + '}}';
		sch_val = {'heat': sch_heat ,'cool': sch_cool,'update_number':'to_be_added' };
		//sch_val = {'heat': {'0':sch_heat.zero,'1':sch_heat.one,'2':sch_heat.two,'3':sch_heat.three,'4':sch_heat.four,'5':sch_heat.five,'6':sch_heat.six} ,'cool': {'0':sch_cool.zero,'1':sch_cool.one,'2':sch_cool.two,'3':sch_cool.three,'4':sch_cool.four,'5':sch_cool.five,'6':sch_cool.six}};
		return sch_val;
	}
	
	$( "#submit_new_schedule" ).click(function(evt) {
		evt.preventDefault();
		update_time = new Date();
		update_time = update_time.toLocaleTimeString();
		//alert(update_time);
		values = get_update_sch_values();
		//alert(values);
	    var jsonText = JSON.stringify(values);
	    //alert(jsonText);
		$.ajax({
			  url : '/submit_schedule/',
			  type: 'POST',
			  data: jsonText,
			  contentType: "application/json; charset=utf-8",
			  dataType: 'json',
			  success : function(data) {
				schedule_update = data.update_number;
				schedule_updated(schedule_update);
			  	//alert(data);
			  	console.log(data.heat);
			  	$('.bottom-right').notify({
			  	    message: { text: 'Your thermostat schedule will be updated in BEMOSS shortly.' },
			  	    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
			  	  }).show(); 
			  },
			  error: function(data) {
				  $('.bottom-right').notify({
				  	    message: { text: 'The schedule was not successful. Try again later.' },
				  	    type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
				  	}).show(); 
			  }
			 });
	});

});