    var AllClusters = [];

    var Clusters = [{ 
        name: "Cluster0",
        event: 1,
        newevent: false
    }];
    var events = [{
        name: "New Event!",
        value: "20"
    }]
    events.push({
        name: "No Events",
        value: "0.0"
    });

var colors = ["#ffffff", "#00BBBB", "#00CCCC", "#00DDDD", "#00EEEE", "#00FFFF", "#00BB5E", "#00CC66", "#00DD6F", "#00EE77", "#00FF84", "#BBBB00", "#CCCC00", "#DDDD00", "#EEEE00", "#FFFF00J", "#BB5E00", "#CC6600m", "#DD6F00", "#EE7700", "#FF8000", "#BB0000", "#CC0000", "#DD0000", "#EE0000", "#FF0000"];
var context = cubism.context() // set the cubism context
                    .serverDelay(0) // No server delay
                    .clientDelay(0) // No client delay
                    .step(1e3) // step once ever second
                    .size(800); // and make the horizon div 960 px wide.
// console.log(context);
d3.select("#example1").call(function (div) {

    AddAllClusters();
    // console.log(AllClusters);

    div.append("div")
        .attr("class", "axis")
        .call(context.axis().orient("top"));

    RunData();

    div.append("div")
        .attr("class", "rule")
        .call(context.rule());
                    
    RefreshRule();

});

        
        
        // function intToRGB(i){
        //     var i1= 
        //     // for(i = 0; i < 360; i += 360 / i1) {
        //     //     HSLColor c;
        //     //     c.hue = i;
        //     //     c.saturation = 90 + randf() * 10;
        //     //     c.lightness = 50 + randf() * 10;

        //     //     colors.push(c);
        //     // }
        //     i=Math.round(Math.random()* 127) + 127;
        //     var c = (i & 0x00FFFFFF)
        //         .toString(16)
        //         .toUpperCase();

        //     return "00000".substring(0, 6 - c.length) + c;
        // }
        function AddAllClusters() {
            for (var i = 0; i < Clusters.length; i++) {
                var mycluster = random(Clusters[i].name);
                AllClusters.push(mycluster);
            }
        }

        function RunData() {
            // console.log("in run data");
            d3.select("#example1").selectAll(".horizon")
                .data(AllClusters)  
            .enter().append("div")
                .attr("class", "horizon")
                .call(context.horizon().colors(colors));
        }

        function random(name) {
            // console.log("in random");
            var value = 0,
                values = [],
                area = [],
                i = 0,
                last;
            return context.metric(function (start, stop, step, callback) {
                start = +start, stop = +stop;
                if (isNaN(last)) last = start;
                while (last < stop) {
                    last += step;
                    for (var j = 0; j < Clusters.length; j++) { //For all users
                        if (Clusters[j].name == name) { //If the user name in the loop matches the current user name
                            if (Clusters[j].newevent) { //If the user has a new event
                                value = parseInt(events[0].value); //Show a "blip" in event zero
                                Clusters[j].newevent = false; //And switch newevent OFF
                            } else { //Otherwise
                                    value = parseFloat(events[Clusters[j].event].value);
                                         //Write the value of the current user
                                    }
                                values.push(value); //And add it to the values array
                        }
                    }
                }
                callback(null, values = values.slice((start - stop) / step)); //And execute the callback function
            }, name);
        }

        function UpdateRule(i) {
            d3.selectAll(".value").each(function (index, d, k) {
                for (l = 0; l < events.length; l++) {
                    // console.log($(this).text().replace("−", "-"));
                    if ($(this).text().replace("−", "-") == events[l].value) {
                        $(this).text(events[l].name);
                    }
                }
            }).style("right", i == null ? null : context.size() - i + 10 + "px");
        }

        function addNewEvent(t1i) {
            var prefixstring = "";
            var suffixstring = "";
            if (events.length + 4 < 10) {
                suffixstring = ".0"
            }
            if (events.length % 2 == 0) {
                prefixstring = "-"
            }
            events.push({
                name: t1i,
                value: prefixstring + (events.length + 4).toString() + suffixstring
            });
            // colors.push(intToRGB(t1i));
            };

        function addEvent(t1i,j) {
            Clusters[j].newevent = true;
            Clusters[j].event = t1i;
            // console.log("event added ");
        }
        
        function addCluster(ti) { //Add a user function (executed by pressing add user button)
            totalClusters = Clusters.length + 1; //a variable for total users
            Clusters.push({ //add a user to the users object
                name: ti, //name equals username text field value
                event: 1, //default event of 1
                newevent: false //the event for this user has not been created yet, so keep the newevent false
            });
            mycluster = random(Clusters[totalClusters - 1].name); //

            AllClusters.push(mycluster); //push the user onto the AllUsers array of users
            RunData();        //Run the data with the new user
            RefreshRule();    //Refresh the rule for all users (will not refresh new user rule if not invoked)
            // console.log("added cluster");
        }


        function RefreshRule() {
            context.on("focus", function (i) {
                UpdateRule(i)
            });
        }


        function plot(t,t1)
        {
            // console.log("events");
            // console.log(events);
            // console.log("Clusters");
            // console.log(Clusters);
            for(var i=0; i< t1.length; i++)
            {
                var flag=0;
               for(var j=0; j<events.length;j++)
               {
                if(events[j].name == t1[i])
                {
                    t1[i]=j;
                    flag=1;
                    break;
                }
               }
               if(flag==0) 
               {
                // console.log("add new event");
                // console.log(t1[i]);
                addNewEvent(t1[i]);
                t1[i]=j;
               }
               
            }
            for(var i=0;i<t.length;i++)
            {
                var flag=0;
                for(var j=0;j< AllClusters.length;j++)
                {
                    if(AllClusters[j]==t[i])
                     {
                        addEvent(t1[i],j);
                        flag=1;
                        break;
                     }   
                }
                if(flag == 0)
                {
                    addCluster(t[i]);
                    // console.log("adding cluster");
                    // console.log(t[i]);
                    addEvent(t1[i],AllClusters.length-1);
                    // console.log("adding event for");
                }  
            }

           }
           
        function getSelectedOptions(sel) {
            var opts = [], opt;
            
            for (var i=0, len=sel.options.length; i<len; i++) {
                opt = sel.options[i];
                if ( opt.selected ) {
                    opts.push(opt.value);
                }
            }
            return opts;
        }