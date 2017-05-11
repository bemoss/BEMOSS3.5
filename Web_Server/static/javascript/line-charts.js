$(document).ready(function(){


    l1 = [['Seoul', 1], ['Paris', 7], ['Singapore',3], ['Hong  Kong',5], ['Chicago', 2], ['New York', 9]];
    l2 = [11, 9, 5, 12, 14];
    l3 = [4, 8, 5, 3, 6];
    l4 = [12, 6, 13, 11, 2];
    l5 = [4, -3, 3, 6, 2, -2];

    pop1980 = [7071639, 2968528, 3005072, 1595138, 789704, 1688210, 785940, 904599];
    pop1990 = [7322564, 3485398, 2783726, 1630553, 983403, 1585577, 935933, 1006877];
    pop2000 = [8008654, 3694644, 2896051, 1974152, 1322025, 1517550, 1160005, 1188603];
    pop2008 = [8363710, 3833995, 2853114, 2242193, 1567924, 1447395, 1351305, 1279910];

    ticks = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "Dallas"];

    plot1 = $.jqplot('chart5',[l2],{
       title: '',
       highlighter: {
           show:true
       },
       cursor: {
           show: true,
           zoom: true
       },
       axes: {
           xaxis: {
               label: 'Time'
           }
       }
    });
    
    plot1b = $.jqplot('chart1b',[l2, l3, l4],{
       stackSeries: true,
       showMarker: false,
       seriesDefaults: {
           fill: true
       }
    });

    plot2 = $.jqplot('chart2',[pop1980, pop1990, pop2000, pop2008],{
       title: 'City Population',
       legend: {
           show: true
       },
       seriesDefaults: {
           renderer: $.jqplot.BarRenderer,
           rendererOptions: {
               barPadding: 2
           }
       },
       series: [
          {label: '1980'},
          {label: '1990'},
          {label: '2000'},
          {label: '2008 (est)'}
       ],
       axes: {
           xaxis: {
               label: 'City',
               renderer: $.jqplot.CategoryAxisRenderer,
               tickRenderer: $.jqplot.CanvasAxisTickRenderer,
               labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
               ticks: ticks,
               tickOptions: {
                   angle: -30
                }
           },
           yaxis: {
               tickRenderer: $.jqplot.CanvasAxisTickRenderer,
               max: 9000000,
               min: 0,
               tickOptions: {
                   formatString: '%d',
                   angle: -30
                }
           }
       }
    });
    
    plot3 = $.jqplot('chart3',[l1],{
       title: 'Global City Index',
       legend: {
           show: true,
           rendererOptions: {
               // numberColumns: 2,
               fontSize: '10pt'
           }
        },
       seriesDefaults: {
           renderer: $.jqplot.FunnelRenderer
       }
    });
        
    plot5 = $.jqplot('chart5',[l1],{
       title: 'Pie Chart',
       seriesDefaults: {
           renderer: $.jqplot.PieRenderer
       },
       legend: {
           show: true
       }
    });
        
    e1 = plot1.themeEngine;
    brass = e1.copy('Default', 'brass');
    brass.title.fontFamily = 'Copperplate, Impact';
    brass.grid.backgroundColor = "rgb(216, 198, 114)";
    brass.grid.drawGridlines = false;
    brass.series[0].lineWidth = 6.5;
    brass.series[0].markerOptions.show = false;
    // brass.axes.xaxis.ticks.fontFamily = "Copperplate, Impact";
    brass.axesStyles.label.fontFamily = "Copperplate, 'Copperplate Gothic Light', Impact";
    brass.axesStyles.ticks.fontFamily = "Copperplate, 'Copperplate Gothic Light', Impact";
    brass.axesStyles.label.fontSize = '14pt';
    
    temp = {
        grid: {
            backgroundColor: "#593D2B",
            gridLineColor: '#E8E8E8',
            gridLineWidth: 3
        },
        title: {
            fontFamily: '"Comic Sans MS", cursive',
            fontSize: '18pt',
            textColor: '#C7CC4E'
        },
        seriesStyles: {
            color: "#DBBCAF",
            lineWidth: 8,
            markerOptions: {
                show: false
            }
        },
        axes: {
            xaxis: {
                label: {
                    fontFamily: '"Comic Sans MS", cursive',
                    textColor: '#C7CC4E'
                }
            }
        }
    };
    
    chocolate = plot1.themeEngine.copy('Default', 'chocolate', temp);
    
    gabe = {
        series: [
            {color: 'rgba(216, 159, 60, 0.6)'},
            {color: 'rgba(159, 216, 60, 0.6)'},
            {color: 'rgba(60, 159, 216, 0.6)'},
        ],
        grid: {
            backgroundColor: '#DEA493'
        }
    }
    
    gabe = plot1b.themeEngine.newTheme('gabe', gabe);
    
    oldstyle = {
        title: {
            fontFamily: 'Times New Roman',
            textColor: 'black'
        },
        axesStyles: {
           borderWidth: 0,
           ticks: {
               fontSize: '12pt',
               fontFamily: 'Times New Roman',
               textColor: 'black'
           },
           label: {
               fontFamily: 'Times New Roman',
               textColor: 'black'
           }
        },
        grid: {
            backgroundColor: 'white',
            borderWidth: 0,
            gridLineColor: 'black',
            gridLineWidth: 2,
            borderColor: 'black'
        },
        series: [
            {color: 'red', highlightColors: ['aqua', 'black', 'blue', 'fuchsia', 'gray', 'green', 'lime', 'maroon', 'navy', 'olive', 'purple', 'red', 'silver', 'teal', 'white', 'yellow']},
            {color: 'green', highlightColors: []},
            {color: 'blue', highlightColors: []},
            {color: 'yellow', highlightColors: 'rgb(255, 245, 185)'}
        ],
        legend: {
            background: 'white',
            textColor: 'black',
            fontFamily: 'Times New Roman',
            border: '1px solid black'
        }
    };
    
    plot2.themeEngine.newTheme('oldstyle', oldstyle);
    
    temp = {
        seriesStyles: {
            seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
            highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
        },
        legend: {
            fontSize: '8pt'
        },
        title: {
            fontSize: '18pt'
        },
        grid: {
            backgroundColor: 'rgb(211, 233, 195)'
        }
    };
    
    plot3.themeEngine.newTheme('uma', temp);
    plot5.themeEngine.newTheme('uma', temp);
});

function switch1() {
    var th = $('#p1switcher').val();
    plot1.activateTheme(th);
}

function switch1b() {
    var th = $('#p1bswitcher').val();
    plot1b.activateTheme(th);
}

function switch2() {
    var th = $('#p2switcher').val();
    plot2.activateTheme(th);
}

function switch3() {
    var th = $('#p3switcher').val();
    plot3.activateTheme(th);
}

function switch5() {
    var th = $('#p5switcher').val();
    plot5.activateTheme(th);
}

function switch35() {
    var th = $('#p35switcher').val();
    plot3.activateTheme(th);
    plot5.activateTheme(th);
}


