function scatterPlot()
{
    document.getElementById('scatterPlot').innerHTML = "";
    document.getElementById('legend').innerHTML = "";
    dta=[];
    var n = keys.length;
    for( var i=0; i<value.length; i++)
        {
    flag = 0;
        for( var j=0; j<keys.length; j++)
                    {
                        if(keys[j]==value[i])
                        {
                            var timeBase = Math.floor(new Date().getTime() / 1000);
                            var randomVariance = (cluster[i] * 20) ;
                            seriesData[j].push( { x: timeBase, y: randomVariance });
                            flag = 1;
                            break;
                        }
                    }
                    if(flag == 0)
                    {
                        seriesData.push([]);
                        keys.push(value[i]);
                        console.log("keys");
                        console.log(keys);
                            var randomVariance = (cluster[cluster.length-1] * 20);
                            var timeBase = Math.floor(new Date().getTime() / 1000);
                        seriesData[seriesData.length-1].push({x: timeBase, y: randomVariance});
                    }

                }
         var palette = new Rickshaw.Color.Palette( { scheme: 'classic9' } );
    console.log("seriesData");
    console.log(seriesData);
    for(var i=0;i < keys.length;i++)
    {
        var c2=palette.color();
        if(seriesData[i].length<10)
        {
            c2="#ff0000";
        }
        dta.push({"color":c2,"name":keys[i],"data":seriesData[i]});
    }
    console.log("dta");
    console.log(dta);


    
var graph = new Rickshaw.Graph( {
        element: document.getElementById("scatterPlot"),
        width: 900,
        height: 500,
        renderer: 'scatterplot',
        stroke: true,
        preserve: true,
        series: dta
    } );
    graph.render();


var preview = new Rickshaw.Graph.RangeSlider( {
    graph: graph,
    element: document.getElementById('preview'),
} );

var hoverDetail = new Rickshaw.Graph.HoverDetail( {
    graph: graph,
    xFormatter: function(x) {
        return new Date(x * 1000).toString();
    }
} );

var annotator = new Rickshaw.Graph.Annotate( {
    graph: graph,
    element: document.getElementById('timeline')
} );

var legend = new Rickshaw.Graph.Legend( {
    graph: graph,
    element: document.getElementById('legend')

} );

var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
    graph: graph,
    legend: legend
} );

var order = new Rickshaw.Graph.Behavior.Series.Order( {
    graph: graph,
    legend: legend
} );

var highlighter = new Rickshaw.Graph.Behavior.Series.Highlight( {
    graph: graph,
    legend: legend
} );

var smoother = new Rickshaw.Graph.Smoother( {
    graph: graph,
    element: document.querySelector('#smoother')
} );

var ticksTreatment = 'glow';

var xAxis = new Rickshaw.Graph.Axis.Time( {
    graph: graph,
    ticksTreatment: ticksTreatment,
    timeFixture: new Rickshaw.Fixtures.Time.Local()
} );

xAxis.render();

var yAxis = new Rickshaw.Graph.Axis.Y( {
    graph: graph,
    // tickFormat: function(y){return y}
    tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
    ticksTreatment: ticksTreatment
} );

yAxis.render();

}