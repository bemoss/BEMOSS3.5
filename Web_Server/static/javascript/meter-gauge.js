$(document).ready(function(){
   //li = [sp_li];
   current = [sp_current];
 
   /*light_intensity_meter = $.jqplot('chart8',[li],{
	   grid: {
	   	background: 'rgba(0, 0, 0, 0.25)'
	   },
       seriesDefaults: {
           renderer: $.jqplot.MeterGaugeRenderer,
           rendererOptions: {
               label: 'Light Intensity',
               labelPosition: 'bottom',
               labelHeightAdjust: -5,
               intervalOuterRadius: 85,
               ticks: [0, 200, 400, 600, 800, 1000],
               intervals:[300, 700, 1000],
               intervalColors:['#66cc66', '#E7E658', '#cc6666']
           }
       }
   });*/

	current_meter = $.jqplot('chart9',[current	],{
	   grid: {
	   	background: 'rgba(0, 0, 0, 0.25)'
	   },
       seriesDefaults: {
           renderer: $.jqplot.MeterGaugeRenderer,
           rendererOptions: {
			   label: 'Current(A)',
               intervalOuterRadius: 85,
               ticks: [0, 2, 4, 6, 8],
               //intervals:[3, 5, 8],
               //intervalColors:['#66cc66', '#E7E658', '#cc6666']
           }
       }
   });
});