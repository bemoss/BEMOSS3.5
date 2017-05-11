$(document).ready(function(){
  var s1 = [['a',6], ['b',8], ['c',14], ['d',20]];
  var s2 = [['a', 8], ['b', 12], ['c', 6], ['d', 9]];
  
  var plot3 = $.jqplot('chart3', [s1, s2], {
    seriesDefaults: {
      // make this a donut chart.
      renderer:$.jqplot.DonutRenderer,
      rendererOptions:{
        // Donut's can be cut into slices like pies.
        sliceMargin: 3,
        // Pies and donuts can start at any arbitrary angle.
        startAngle: -90,
        showDataLabels: true,
        // By default, data labels show the percentage of the donut/pie.
        // You can show the data 'value' or data 'label' instead.
        dataLabels: 'value'
      }
    }
  });
});
