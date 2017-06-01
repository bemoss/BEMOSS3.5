/**
 * Created by kruthika on 5/23/15.
 */
/**

 *  Authors: Kruthika Rathinavel
 *  Version: 2.0
 *  Email: kruthika@vt.edu
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
			      labels:["Outdoor Temperature"]
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
			        tickOptions:{formatString:'%m/%d, %H:%M'},

		            min : _outdoor_temp[0][0],
		            max: _outdoor_temp[_outdoor_temp.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Temperature (F)"
			      }
			    }
	  };



	  //Initialize plot for power
      var data_points_temp = [_outdoor_temp];
	  var plot_temp = $.jqplot('chart100', data_points_temp ,options_temp);
      $("#outdoor_temp").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {

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

        var timeOut_temp;

        function update_plot_temp(_data) {

            _outdoor_temp = _data.temperature;

            var new_data = [];

              $.each($('input:checked'), function(index, value){

                    if (this.id == 'outdoor_temp') {
                       new_data.push(_outdoor_temp);
                       options_temp.legend.labels.push(this.value);
                   }

                   options_temp.axes.xaxis.min = _outdoor_temp[0][0];
                   options_temp.axes.xaxis.max = _outdoor_temp[_outdoor_temp.length-1][0];
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
            var from_date = $("#from_date").val();
            var to_date = $("#to_date").val();
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);

				$.ajax({
				  url : '/charts/'+mac+'/',

				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',

				  success : function(data) {

					  console.log ("testing");
					  console.log (typeof(data));


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
			//},5000);
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

                   if (this.id == 'outdoor_temp') {
                       new_data.push(_outdoor_temp);
                       options_temp.legend.labels.push(this.value);
                   }


                   options_temp.axes.xaxis.min = _outdoor_temp[0][0];
                   options_temp.axes.xaxis.max = _outdoor_temp[_outdoor_temp.length-1][0];
              });


                   if (plot_temp) {
                        plot_temp.destroy();
                    }


                  plot2_temp = $.jqplot('chart100', new_data ,options_temp);
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
			      labels:["Outdoor Humidity"]
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
			        tickOptions:{formatString:'%m/%d, %H:%M'},

		            min : _outdoor_humidity[0][0],
		            max: _outdoor_humidity[_outdoor_humidity.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Humidity (%)"
			      }
			    }
	  };



	  //Initialize plot for power
      var data_points_humidity = [_outdoor_humidity];
	  var plot_humidity = $.jqplot('chart101', data_points_humidity ,options_humidity);
      $("#indoor_humidity").attr('checked','checked');
      $("#outdoor_humidity").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {

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

            _outdoor_humidity = _data.humidity;

            var new_data = [];

              $.each($('input:checked'), function(index, value){

                    if (this.id == 'outdoor_humidity') {
                       new_data.push(_outdoor_humidity);
                       options_humidity.legend.labels.push(this.value);
                   }

                   options_humidity.axes.xaxis.min = _outdoor_humidity[0][0];
                   options_humidity.axes.xaxis.max = _outdoor_humidity[_outdoor_humidity.length-1][0];
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
            var from_date = $("#from_date").val();
            var to_date = $("#to_date").val();
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);

				$.ajax({
				  url : '/charts/'+mac+'/',

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

                     if (this.id == 'outdoor_humidity') {
                       new_data.push(_outdoor_humidity);
                       options_humidity.legend.labels.push(this.value);
                   }


                   options_humidity.axes.xaxis.min = _outdoor_humidity[0][0];
                   options_humidity.axes.xaxis.max = _outdoor_humidity[_outdoor_humidity.length-1][0];
              });


                   if (plot_humidity) {
                        plot_humidity.destroy();
                    }


                  plot2_humidity = $.jqplot('chart101', new_data ,options_humidity);
                  plot2_humidity.themeEngine.newTheme('uma', temp);
                  plot2_humidity.activateTheme('uma');

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
			        tickOptions:{formatString:'%m/%d, %H:%M'},

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
	  var plot_pressure = $.jqplot('chart102', data_points_pressure ,options_pressure);
      $("#pressure").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {

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
            _pressure = _data.pressure;

            var new_data = [];

              $.each($('input:checked'), function(index, value){

                   if (this.id == 'pressure') {

                       if (typeof(_pressure) == 'string')
                       {
                           _pressure = $.parseJSON(_pressure);
                       }
                       new_data.push(_pressure);
                        options_pressure.legend.labels.push(this.value);
                   }

                   options_pressure.axes.xaxis.min = _pressure[0][0];
                   options_pressure.axes.xaxis.max = _pressure[_pressure.length-1][0];
              });

                   if (plot_pressure) {
                        plot_pressure.destroy();
                    }


                  plot2_pressure = $.jqplot('chart102', new_data ,options_pressure);
                  plot2_pressure.themeEngine.newTheme('uma', temp);
                  plot2_pressure.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_pressure").attr('disabled','disabled');
              $("#stop_auto_update_pressure").removeAttr('disabled');
        }


        function do_update_pressure() {
            var from_date = $("#from_date").val();
            var to_date = $("#to_date").val();
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
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
			//},5000);
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
                       if (typeof(_pressure) == 'string')
                       {
                           _pressure = $.parseJSON(_pressure);
                       }
                       new_data.push(_pressure);
                       options_pressure.legend.labels.push(this.value);
                   }

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
     * Plot functions and values for wind
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_wind = {
			    legend: {
			      show: true,
			      labels:["Wind"]
			    },
                series:[{
                    label: 'Wind (mi/hr)',
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
			        tickOptions:{formatString:'%m/%d, %H:%M'},

		            min : _wind[0][0],
		            max: _wind[_wind.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Wind (mi/hr)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_wind = [_wind];
	  var plot_wind = $.jqplot('chart104', data_points_wind ,options_wind);
      $("#wind").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {

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


        plot_wind.themeEngine.newTheme('uma', temp);
        plot_wind.activateTheme('uma');

        var timeOut_wind;

        function update_plot_wind(_data) {
            _wind = _data.v_wind;

            var new_data = [];

              $.each($('input:checked'), function(index, value){

                   if (this.id == 'wind') {
                       if (typeof(_wind) == 'string') {
                           _wind = $.parseJSON(_wind);
                       }
                       new_data.push(_wind);
                       options_wind.legend.labels.push(this.value);
                   }

                   options_wind.axes.xaxis.min = _wind[0][0];
                   options_wind.axes.xaxis.max = _wind[_wind.length-1][0];
              });

                   if (plot_wind) {
                        plot_wind.destroy();
                    }


                  plot2_wind = $.jqplot('chart104', new_data ,options_wind);
                  plot2_wind.themeEngine.newTheme('uma', temp);
                  plot2_wind.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_wind").attr('disabled','disabled');
              $("#stop_auto_update_wind").removeAttr('disabled');
        }


        function do_update_wind() {
            var from_date = $("#from_date").val();
            var to_date = $("#to_date").val();
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);

				$.ajax({
				  url : '/weather_sensor_smap_update_wind/',

				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',

				  success : function(data) {

					  console.log ("testing");
					  console.log (data);
                      update_plot_wind(data);

				  },
				  error: function(data) {

                      clearTimeout(timeOut_wind);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_wind = setTimeout(do_update_wind, 30000);
			//},5000);
	}

    	  //Auto update the chart
	  $('#auto_update_wind').click( function(evt){
          evt.preventDefault();
	      do_update_wind();
	   });

      $('#stop_auto_update_wind').click(function(){
          clearTimeout(timeOut_wind);
          $('#stop_auto_update_wind').attr('disabled', 'disabled');
          $('#auto_update_wind').removeAttr('disabled');
      });

        $('#stack_chart_wind').click( function(evt){
            evt.preventDefault();
	        stackCharts_wind();
	   });

	  function stackCharts_wind(){
        if (timeOut_wind) {
          clearTimeout(timeOut_wind);
          $('#stop_auto_update_wind').attr('disabled', 'disabled');
          $('#auto_update_wind').removeAttr('disabled');
        }
        options_wind.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'wind') {
                       if (typeof(_wind) == 'string') {
                           _wind = $.parseJSON(_wind);
                       }
                       new_data.push(_wind);
                        options_wind.legend.labels.push(this.value);
                   }

                   options_wind.axes.xaxis.min = _wind[0][0];
                   options_wind.axes.xaxis.max = _wind[_wind.length-1][0];
              });


                   if (plot_wind) {
                        plot_wind.destroy();
                    }


                  plot2_wind = $.jqplot('chart104', new_data ,options_wind);
                  plot2_wind.themeEngine.newTheme('uma', temp);
                  plot2_wind.activateTheme('uma');

      }


    $("#get_stat").click(function(evt) {
        evt.preventDefault();
        var from_date = $("#from_date").val();
        var to_date = $("#to_date").val();
        get_statistics(from_date, to_date);

    });

    function get_statistics(from_date, to_date) {
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);

				$.ajax({
				  url : '/charts/' + mac + '/',

				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',

				  success : function(data) {



                      if (data.temperature.length == 0) {
                          $('.bottom-right').notify({
					  	    message: { text: 'No data found for the selected time period.'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
                      } else {

                          update_plot_temp(data);
                          $("#auto_update_temp").removeAttr('disabled');
                          $("#stop_auto_update_temp").attr('disabled','disabled');
                          update_plot_humidity(data);
                          $("#auto_update_humidity").removeAttr('disabled');
                          $("#stop_auto_update_humidity").attr('disabled','disabled');
                          update_plot_pressure(data);
                          $("#auto_update_pressure").removeAttr('disabled');
                          $("#stop_auto_update_pressure").attr('disabled','disabled');
                          update_plot_wind(data);
                          $("#auto_update_co2").removeAttr('disabled');
                          $("#stop_auto_update_co2").attr('disabled','disabled');
                          update_plot_co2(data);
                          $("#auto_update_wind").removeAttr('disabled');
                          $("#stop_auto_update_wind").attr('disabled','disabled');

                      }
				  },
				  error: function(data) {


                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'+data},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });

    }

    $("#export_data").click(function(evt) {
        evt.preventDefault();
        var from_date = $("#from_date").val();
        var to_date = $("#to_date").val();
        export_to_spreadsheet(from_date, to_date);

    });


    function export_to_spreadsheet(from_date, to_date) {
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
            $.ajax({
              url : 'charts/download_sheet/' + mac + '/',
              type: 'POST',
              data: jsonText,
              dataType: 'json',
              success : function(data) {
                  if (data.length == 0) {
                      $('.bottom-right').notify({
                        message: { text: 'No data found for the selected time period.'},
                        type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
                      }).show();
                  } else {
                      JSONToCSVConvertor(data, mac, true);

                  }
              },
              error: function(data) {
                  $('.bottom-right').notify({
                        message: { text: 'Communication Error. Try again later!'+data},
                        type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
                      }).show();
              }
             });
    }


    function JSONToCSVConvertor(JSONData, ReportTitle, ShowLabel) {
        //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
        var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;
        var CSV = '';
        //This condition will generate the Label/Header
        if (ShowLabel) {
            var row = "";
            //This loop will extract the label from 1st index of on array
            for (var index in arrData[0]) {
                //Now convert each value to string and comma-seprated
                row += index + ',';
            }
            row = row.slice(0, -1);
            //append Label row with line break
            CSV += row + '\r\n';
        }
        //1st loop is to extract each row
        for (var i = 0; i < arrData.length; i++) {
            var row = "";
            //2nd loop will extract each column and convert it in string comma-seprated
            for (var index in arrData[i]) {
                row += '"' + arrData[i][index] + '",';
            }
            row.slice(0, row.length - 1);
            //add a line break after each row
            CSV += row + '\r\n';
        }
        if (CSV == '') {
            alert("Invalid data");
            return;
        }
        //Generate a file name
        var fileName = "timeseries_";
        //this will remove the blank-spaces from the title and replace it with an underscore
        fileName += ReportTitle.replace(/ /g,"_");
        //Initialize file format you want csv or xls
        var uri = 'data:text/csv;charset=utf-8,' + escape(CSV);
        //this trick will generate a temp <a /> tag
        var link = document.createElement("a");
        link.href = uri;
        //set the visibility hidden so it will not effect on your web-layout
        link.style = "visibility:hidden";
        link.download = fileName + ".csv";
        //this part will append the anchor tag and remove it after automatic click
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }



});