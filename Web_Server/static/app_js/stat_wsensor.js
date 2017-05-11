/**
 * Created by kruthika on 5/23/15.
 */
/**

 *  Authors: BEMOSS Team
 *  Version: 2.0
 *  Email: aribemoss@gmail.com
 *  Created: "2014-10-13 18:45:40"
 *  Updated: "2015-02-13 15:06:41"
**/

$(document).ready(function(){
    $.csrftoken();

    /**
     * Plot functions and values for Temperature
     * @type {{legend: {show: boolean, labels: string[]}, series: *[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}, y2axis: {min: number, max: number, label: string}}}}
     */

	  //Plot options
	  var options_temp = {
			    legend: {
			      show: true,
			      labels:["Indoor Temperature", "Outdoor Temperature"]
			    },
                series:[{
                    label: 'Temperature (F)',
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
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
		            min : _indoor_temp[0][0],
		            max: _indoor_temp[_indoor_temp.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Temperature (F)"
			      }
			    }
	  };



	  //Initialize plot for power
      var data_points_temp = [_indoor_temp, _outdoor_temp];
	  var plot_temp = $.jqplot('chart100', data_points_temp ,options_temp);
      $("#indoor_temp").attr('checked','checked');
      $("#outdoor_temp").attr('checked','checked');

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


        plot_temp.themeEngine.newTheme('uma', temp);
        plot_temp.activateTheme('uma');

        var timeOut_power;

        function update_plot_temp(_data) {
            var _indoor_temp = _data.indoor_temperature;
            var _outdoor_temp = _data.outdoor_temperature;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'indoor_temp') {
                       new_data.push(_indoor_temp);
                   } else if (this.id == 'outdoor_temp') {
                       new_data.push(_outdoor_temp);
                   }
                   options_temp.legend.labels.push(this.value);
                   options_temp.axes.xaxis.min = _indoor_temp[0][0];
                   options_temp.axes.xaxis.max = _indoor_temp[_indoor_temp.length-1][0];
              });

                   if (plot_temp) {
                        plot_temp.destroy();
                    }

                  plot2_temp = $.jqplot('chart100', new_data ,options_temp);
                  plot2_temp.themeEngine.newTheme('uma', temp);
                  plot2_temp.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_temp").attr('disabled','disabled');
              $("#stop_auto_update_temp").removeAttr('disabled');
        }


        function do_update_temp() {
            var values = {
		        "device_info": device_info,
                "data_req": "temp"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/weather_sensor_smap_update_temp/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_temp(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_temp);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_temp = setTimeout(do_update_temp, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_temp').click( function(evt){
          evt.preventDefault();
	      do_update_temp();
	   });

      $('#stop_auto_update_temp').click(function(){
          clearTimeout(timeOut_temp);
          $('#stop_auto_update_temp').attr('disabled', 'disabled');
          $('#auto_update_temp').removeAttr('disabled');
      });

        $('#stack_chart_temp').click( function(evt){
            evt.preventDefault();
	        stackCharts_temp();
	   });

	  function stackCharts_temp(){
        if (timeOut_temp) {
          clearTimeout(timeOut_temp);
          $('#stop_auto_update_temp').attr('disabled', 'disabled');
          $('#auto_update_temp').removeAttr('disabled');
        }
        options_temp.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   //new_data.push(outdoor_temp);
                   if (this.id == 'indoor_temp') {
                       new_data.push(_indoor_temp);
                   } else if (this.id == 'outdoor_temp') {
                       new_data.push(_outdoor_temp);
                   }

                   options_temp.legend.labels.push(this.value);
                   options_temp.axes.xaxis.min = _indoor_temp[0][0];
                   options_temp.axes.xaxis.max = _indoor_temp[_indoor_temp.length-1][0];
              });


                   if (plot_temp) {
                        plot_temp.destroy();
                    }

                  plot2_temp = $.jqplot('chart100', new_data ,options_power);
                  plot2_temp.themeEngine.newTheme('uma', temp);
                  plot2_temp.activateTheme('uma');

      }

        /**
     * Plot functions and values for Humidity
     * @type {{legend: {show: boolean, labels: string[]}, series: *[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}, y2axis: {min: number, max: number, label: string}}}}
     */

	  //Plot options
	  var options_humidity = {
			    legend: {
			      show: true,
			      labels:["Indoor Humidity", "Outdoor Humidity"]
			    },
                series:[{
                    label: 'Humidity (%)',
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
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
		            min : _indoor_humidity[0][0],
		            max: _indoor_humidity[_indoor_humidity.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Humidity (%)"
			      }
			    }
	  };



	  //Initialize plot for power
      var data_points_humidity = [_indoor_humidity, _outdoor_humidity];
	  var plot_humidity = $.jqplot('chart101', data_points_humidity ,options_humidity);
      $("#indoor_humidity").attr('checked','checked');
      $("#outdoor_humidity").attr('checked','checked');

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


        plot_humidity.themeEngine.newTheme('uma', temp);
        plot_humidity.activateTheme('uma');

        var timeOut_humidity;

        function update_plot_humidity(_data) {
            var _indoor_humidity = _data.indoor_humidity;
            var _outdoor_humidity = _data.outdoor_humidity;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'indoor_humidity') {
                       new_data.push(_indoor_humidity);
                   } else if (this.id == 'outdoor_humidity') {
                       new_data.push(_outdoor_humidity);
                   }
                   options_humidity.legend.labels.push(this.value);
                   options_humidity.axes.xaxis.min = _indoor_humidity[0][0];
                   options_humidity.axes.xaxis.max = _indoor_humidity[_indoor_humidity.length-1][0];
              });

                   if (plot_humidity) {
                        plot_humidity.destroy();
                    }

                  plot2_humidity = $.jqplot('chart101', new_data ,options_humidity);
                  plot2_humidity.themeEngine.newTheme('uma', temp);
                  plot2_humidity.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_humidity").attr('disabled','disabled');
              $("#stop_auto_update_humidity").removeAttr('disabled');
        }


        function do_update_humidity() {
            var values = {
		        "device_info": device_info,
                "data_req": "humidity"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/weather_sensor_smap_update_humidity/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_humidity(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_humidity);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_humidity = setTimeout(do_update_humidity, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_humidity').click( function(evt){
          evt.preventDefault();
	      do_update_humidity();
	   });

      $('#stop_auto_update_humidity').click(function(){
          clearTimeout(timeOut_humidity);
          $('#stop_auto_update_humidity').attr('disabled', 'disabled');
          $('#auto_update_humidity').removeAttr('disabled');
      });

        $('#stack_chart_humidity').click( function(evt){
            evt.preventDefault();
	        stackCharts_humidity();
	   });

	  function stackCharts_humidity(){
        if (timeOut_humidity) {
          clearTimeout(timeOut_humidity);
          $('#stop_auto_update_humidity').attr('disabled', 'disabled');
          $('#auto_update_humidity').removeAttr('disabled');
        }
        options_humidity.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'indoor_humidity') {
                       new_data.push(_indoor_humidity);
                   } else if (this.id == 'outdoor_humidity') {
                       new_data.push(_outdoor_humidity);
                   }

                   options_humidity.legend.labels.push(this.value);
                   options_humidity.axes.xaxis.min = _indoor_humidity[0][0];
                   options_humidity.axes.xaxis.max = _indoor_humidity[_indoor_humidity.length-1][0];
              });


                   if (plot_humidity) {
                        plot_humidity.destroy();
                    }

                  plot2_humidity = $.jqplot('chart101', new_data ,options_humidity);
                  plot2_humidity.themeEngine.newTheme('uma', temp);
                  plot2_humidity.activateTheme('uma');

      }



    /**
     * Plot functions and values for CO2
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_co2 = {
			    legend: {
			      show: true,
			      labels:["CO2"]
			    },
                series:[{
                    label: 'CO2 (ppm)',
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
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
		            min : _co2[0][0],
		            max: _co2[_co2.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "CO2 (ppm)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_co2 = [_co2];
	  var plot_co2 = $.jqplot('chart102', data_points_co2 ,options_co2);
      $("#co2").attr('checked','checked');

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


        plot_co2.themeEngine.newTheme('uma', temp);
        plot_co2.activateTheme('uma');

        var timeOut_co2;

        function update_plot_co2(_data) {
            var _co2 = _data.co2;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'co2') {
                       new_data.push(_co2);
                   }
                   options_co2.legend.labels.push(this.value);
                   options_co2.axes.xaxis.min = _co2[0][0];
                   options_co2.axes.xaxis.max = _co2[_co2.length-1][0];
              });

                   if (plot_co2) {
                        plot_co2.destroy();
                    }

                  plot2_co2 = $.jqplot('chart102', new_data ,options_co2);
                  plot2_co2.themeEngine.newTheme('uma', temp);
                  plot2_co2.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_co2").attr('disabled','disabled');
              $("#stop_auto_update_co2").removeAttr('disabled');
        }


        function do_update_co2() {
            var values = {
		        "device_info": device_info,
                "data_req": "co2"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/weather_sensor_smap_update_co2/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_co2(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_co2);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_co2 = setTimeout(do_update_co2, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_co2').click( function(evt){
          evt.preventDefault();
	      do_update_co2();
	   });

      $('#stop_auto_update_co2').click(function(){
          clearTimeout(timeOut_co2);
          $('#stop_auto_update_co2').attr('disabled', 'disabled');
          $('#auto_update_co2').removeAttr('disabled');
      });

        $('#stack_chart_co2').click( function(evt){
            evt.preventDefault();
	        stackCharts_co2();
	   });

	  function stackCharts_co2(){
        if (timeOut_co2) {
          clearTimeout(timeOut_co2);
          $('#stop_auto_update_co2').attr('disabled', 'disabled');
          $('#auto_update_co2').removeAttr('disabled');
        }
        options_co2.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'co2') {
                       new_data.push(_co2);
                   }
                   options_co2.legend.labels.push(this.value);
                   options_co2.axes.xaxis.min = _co2[0][0];
                   options_co2.axes.xaxis.max = _co2[_co2.length-1][0];
              });


                   if (plot_co2) {
                        plot_co2.destroy();
                    }

                  plot2_co2 = $.jqplot('chart102', new_data ,options_co2);
                  plot2_co2.themeEngine.newTheme('uma', temp);
                  plot2_co2.activateTheme('uma');

      }


    /**
     * Plot functions and values for Pressure
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_pressure = {
			    legend: {
			      show: true,
			      labels:["Pressure"]
			    },
                series:[{
                    label: 'Pressure (Pa)',
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
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
		            min : _pressure[0][0],
		            max: _pressure[_pressure.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Pressure (Pa)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_pressure = [_pressure];
	  var plot_pressure = $.jqplot('chart103', data_points_pressure ,options_pressure);
      $("#pressure").attr('checked','checked');

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


        plot_pressure.themeEngine.newTheme('uma', temp);
        plot_pressure.activateTheme('uma');

        var timeOut_pressure;

        function update_plot_pressure(_data) {
            var _pressure = _data.pressure;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'pressure') {
                       new_data.push(_pressure);
                   }
                   options_pressure.legend.labels.push(this.value);
                   options_pressure.axes.xaxis.min = _pressure[0][0];
                   options_pressure.axes.xaxis.max = _pressure[_pressure.length-1][0];
              });

                   if (plot_pressure) {
                        plot_pressure.destroy();
                    }

                  plot2_pressure = $.jqplot('chart103', new_data ,options_pressure);
                  plot2_pressure.themeEngine.newTheme('uma', temp);
                  plot2_pressure.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_pressure").attr('disabled','disabled');
              $("#stop_auto_update_pressure").removeAttr('disabled');
        }


        function do_update_pressure() {
            var values = {
		        "device_info": device_info,
                "data_req": "pressure"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/weather_sensor_smap_update_pressure/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_pressure(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_pressure);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_pressure = setTimeout(do_update_pressure, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_pressure').click( function(evt){
          evt.preventDefault();
	      do_update_pressure();
	   });

      $('#stop_auto_update_pressure').click(function(){
          clearTimeout(timeOut_pressure);
          $('#stop_auto_update_pressure').attr('disabled', 'disabled');
          $('#auto_update_pressure').removeAttr('disabled');
      });

        $('#stack_chart_pressure').click( function(evt){
            evt.preventDefault();
	        stackCharts_pressure();
	   });

	  function stackCharts_pressure(){
        if (timeOut_pressure) {
          clearTimeout(timeOut_pressure);
          $('#stop_auto_update_pressure').attr('disabled', 'disabled');
          $('#auto_update_pressure').removeAttr('disabled');
        }
        options_pressure.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'pressure') {
                       new_data.push(_pressure);
                   }
                   options_pressure.legend.labels.push(this.value);
                   options_pressure.axes.xaxis.min = _pressure[0][0];
                   options_pressure.axes.xaxis.max = _pressure[_pressure.length-1][0];
              });


                   if (plot_pressure) {
                        plot_pressure.destroy();
                    }

                  plot2_pressure = $.jqplot('chart103', new_data ,options_pressure);
                  plot2_pressure.themeEngine.newTheme('uma', temp);
                  plot2_pressure.activateTheme('uma');

      }

        /**
     * Plot functions and values for Noise
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_noise = {
			    legend: {
			      show: true,
			      labels:["Noise"]
			    },
                series:[{
                    label: 'Noise (db)',
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
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
		            min : _noise[0][0],
		            max: _noise[_noise.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Noise (db)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_noise = [_noise];
	  var plot_noise = $.jqplot('chart104', data_points_noise ,options_noise);
      $("#noise").attr('checked','checked');

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


        plot_noise.themeEngine.newTheme('uma', temp);
        plot_noise.activateTheme('uma');

        var timeOut_noise;

        function update_plot_noise(_data) {
            var _noise = _data.noise;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'noise') {
                       new_data.push(_noise);
                   }
                   options_noise.legend.labels.push(this.value);
                   options_noise.axes.xaxis.min = _noise[0][0];
                   options_noise.axes.xaxis.max = _noise[_noise.length-1][0];
              });

                   if (plot_noise) {
                        plot_noise.destroy();
                    }

                  plot2_noise = $.jqplot('chart104', new_data ,options_noise);
                  plot2_noise.themeEngine.newTheme('uma', temp);
                  plot2_noise.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_noise").attr('disabled','disabled');
              $("#stop_auto_update_noise").removeAttr('disabled');
        }


        function do_update_noise() {
            var values = {
		        "device_info": device_info,
                "data_req": "noise"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/weather_sensor_smap_update_noise/',
				  //url : 'http://38.68.237.143/backend/api/data/uuid/97699b93-9d6d-5e31-b4ef-7ac78fdc985a',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  //dataType: 'jsonp',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_noise(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_noise);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_noise = setTimeout(do_update_noise, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_noise').click( function(evt){
          evt.preventDefault();
	      do_update_noise();
	   });

      $('#stop_auto_update_noise').click(function(){
          clearTimeout(timeOut_noise);
          $('#stop_auto_update_noise').attr('disabled', 'disabled');
          $('#auto_update_noise').removeAttr('disabled');
      });

        $('#stack_chart_noise').click( function(evt){
            evt.preventDefault();
	        stackCharts_noise();
	   });

	  function stackCharts_noise(){
        if (timeOut_noise) {
          clearTimeout(timeOut_noise);
          $('#stop_auto_update_noise').attr('disabled', 'disabled');
          $('#auto_update_noise').removeAttr('disabled');
        }
        options_noise.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'noise') {
                       new_data.push(_noise);
                   }
                   options_noise.legend.labels.push(this.value);
                   options_noise.axes.xaxis.min = _noise[0][0];
                   options_noise.axes.xaxis.max = _noise[_noise.length-1][0];
              });


                   if (plot_noise) {
                        plot_noise.destroy();
                    }

                  plot2_noise = $.jqplot('chart104', new_data ,options_noise);
                  plot2_noise.themeEngine.newTheme('uma', temp);
                  plot2_noise.activateTheme('uma');

      }

});