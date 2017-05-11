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


$(document).ready(function(){
    $.csrftoken();


	  //Plot options
	  var options = {
			    legend: {
			      show: true,
			      labels:["Status","Brightness"]
			    },
                series:[{
                    label: 'Status (0=OFF, 1=ON)',
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
                }, {
                    label: 'Brightness (%)',
                    yaxis: 'y2axis'
                }],
			    cursor: {
			           show: true,
			           zoom: true
			    },
			    seriesDefaults: {
                  show: true,
			      showMarker:false,
			      pointLabels: {show:false},
			      rendererOption:{smooth: true}
			    },
			    axesDefaults: {
			      labelRenderer: $.jqplot.CanvasAxisLabelRenderer
			    },
			    axes: {
			      xaxis: {
			        label: "Time",
			        renderer: $.jqplot.DateAxisRenderer,
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _status[0][0],
		            max: _status[_status.length-1][0]
			      },
			      yaxis: {
			        min:0,
			        max:1,
			        label: "Status (0=OFF, 1=ON)"
			      },
                  y2axis: {
                    min:0,
			        max:100,
			        label: "Brightness (%)"
                  }
			    }
	  };

    var options_brightness = {
			    legend: {
			      show: true,
			      labels:["Brightness"]
			    },
                series:{
                    label: "Brightness (%)",
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
                },
			    cursor: {
			           show: true,
			           zoom: true
			    },
			    seriesDefaults: {
                  show: true,
			      showMarker:false,
			      pointLabels: {show:false},
			      rendererOption:{smooth: true}
			    },
			    axesDefaults: {
			      labelRenderer: $.jqplot.CanvasAxisLabelRenderer
			    },
			    axes: {
			      xaxis: {
			        label: "Time",
			        renderer: $.jqplot.DateAxisRenderer,
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _brightness[0][0],
		            max: _brightness[_brightness.length-1][0]
			      },
			      yaxis: {
			        min:0,
			        max:100,
			        label: "Brightness (%)"
			      }
			    }
	  };



	  //Initialize plot for lighting
      var data_points = [_status, _brightness];
	  var plot1 = $.jqplot('chart100', data_points ,options);
      $("#status").attr('checked','checked');
      $("#brightness").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
            },
            axesStyles: {
               borderWidth: 0,
               label: {
                   fontFamily: 'Sans',
                   textColor: 'white',
                   fontSize: '9pt'
               }
            }
        };


        plot1.themeEngine.newTheme('uma', temp);
        plot1.activateTheme('uma');

        var timeOut;

        function update_plot(_data) {
              _status = _data.status;
              _brightness = _data.brightness;
              var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'status') {
                       new_data.push(_status);
                   } else if (this.id == 'brightness') {
                       new_data.push(_brightness);
                   }
                   options.legend.labels.push(this.value);
                   options.axes.xaxis.min = _status[0][0];
                   options.axes.xaxis.max = _status[_status.length-1][0];
              });
              if ($('input:checked').length == 1 && $('input:checked')[0].id == 'brightness') {
                  options_brightness.legend.labels.push('Brightness');
                  options_brightness.axes.yaxis.min = 0;
                  options_brightness.axes.yaxis.max = 100;
                  options_brightness.axes.xaxis.min = _brightness[0][0];
                  options_brightness.axes.xaxis.max = _brightness[_brightness.length-1][0];

                  if (plot1) {
                        plot1.destroy();
                   }

                  var plot2 = $.jqplot('chart100', new_data ,options_brightness);
                  plot2.themeEngine.newTheme('uma', temp);
                  plot2.activateTheme('uma');

              } else {

                   if (plot1) {
                        plot1.destroy();
                    }

                  plot2 = $.jqplot('chart100', new_data ,options);
                  plot2.themeEngine.newTheme('uma', temp);
                  plot2.activateTheme('uma');
              }



              console.log('nowww');
              $("#auto_update").attr('disabled','disabled');
              $("#stop_auto_update").removeAttr('disabled');
        }


        function do_update() {
            var values = {
		        "device_info": device_info
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/lt_smap_update/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut = setTimeout(do_update, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update').click( function(evt){
          evt.preventDefault();
	      do_update();
	   });

      $('#stop_auto_update').click(function(){
          clearTimeout(timeOut);
          $('#stop_auto_update').attr('disabled', 'disabled');
          $('#auto_update').removeAttr('disabled');
      });

        $('#stack_chart').click( function(evt){
            evt.preventDefault();
	        stackCharts();
	   });

	  function stackCharts(){
        if (timeOut) {
          clearTimeout(timeOut);
          $('#stop_auto_update').attr('disabled', 'disabled');
          $('#auto_update').removeAttr('disabled');
        }
        options.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
           //new_data.push(outdoor_temp);
           if (this.id == 'status') {
               new_data.push(_status);
           } else if (this.id == 'brightness') {
               new_data.push(_brightness);
           }
           options.legend.labels.push(this.value);
           options.axes.xaxis.min = _status[0][0];
           options.axes.xaxis.max = _status[_status.length-1][0];
        });

          if ($('input:checked').length == 1 && $('input:checked')[0].id == 'brightness') {
                  options_brightness.legend.labels.push('Brightness');
                  options_brightness.axes.yaxis.min = 0;
                  options_brightness.axes.yaxis.max = 100;
                  options_brightness.axes.xaxis.min = _brightness[0][0];
                  options_brightness.axes.xaxis.max = _brightness[_brightness.length-1][0];

                  if (plot1) {
                        plot1.destroy();
                   }

                  var plot2 = $.jqplot('chart100', new_data ,options_brightness);
                  plot2.themeEngine.newTheme('uma', temp);
                  plot2.activateTheme('uma');

              } else {

                   if (plot1) {
                        plot1.destroy();
                    }

                  plot2 = $.jqplot('chart100', new_data ,options);
                  plot2.themeEngine.newTheme('uma', temp);
                  plot2.activateTheme('uma');
              }

      }



});