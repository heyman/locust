$(window).ready(function() {
    if($("#locust_count").length > 0) {
        $("#locust_count").focus().select();
    }
});

$("#box_stop a").click(function(event) {
    event.preventDefault();
    $.get($(this).attr("href"));
    $("body").attr("class", "stopped");
    $(".box_stop").hide();
    $("a.new_test").show();
    $("a.edit_test").hide();
    $(".user_count").hide();
});

$("#box_reset a").click(function(event) {
    event.preventDefault();
    $.get($(this).attr("href"));
});

$(".ramp_test").click(function(event) {
    event.preventDefault();
    $("#start").hide();
    $("#ramp").show();
});

$("#new_test").click(function(event) {
    event.preventDefault();
    $("#ramp").hide();
    $("#start").show();
    $("#locust_count").focus().select();
});

$(".edit_test").click(function(event) {
    event.preventDefault();
    $("#edit").show();
    $("#new_locust_count").focus().select();
});

$(".close_link").click(function(event) {
    event.preventDefault();
    $(this).parent().parent().hide();
});

var alternate = false;

$("ul.tabs").tabs("div.panes > div");

var stats_tpl = $('#stats-template');
var errors_tpl = $('#errors-template');
var exceptions_tpl = $('#exceptions-template');

$('#swarm_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                $("body").attr("class", "hatching");
                $("#start").fadeOut();
                $("#status").fadeIn();
                $(".box_running").fadeIn();
                $("a.new_test").fadeOut();
                $("a.edit_test").fadeIn();
                $(".user_count").fadeIn();
            }
        }
    );
});

$('#ramp_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                $("body").attr("class", "hatching");
                $("#ramp").fadeOut();
                $("#status").fadeIn();
                $(".box_running").fadeIn();
                $("a.new_test").fadeOut();
                $("a.edit_test").fadeIn();
                $(".user_count").fadeIn();
            }
        }
    );
});

$('#edit_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                $("body").attr("class", "hatching");
                $("#edit").fadeOut();
            }
        }
    );
});

var sortBy = function(field, reverse, primer){
    reverse = (reverse) ? -1 : 1;
    return function(a,b){
        a = a[field];
        b = b[field];
       if (typeof(primer) != 'undefined'){
           a = primer(a);
           b = primer(b);
       }
       if (a<b) return reverse * -1;
       if (a>b) return reverse * 1;
       return 0;
    }
}

// Sorting by column
var sortAttribute = "name";
var desc = false;
var report;
$(".stats_label").click(function(event) {
    event.preventDefault();
    sortAttribute = $(this).attr("data-sortkey");
    desc = !desc;

    $('#stats tbody').empty();
    $('#errors tbody').empty();
    alternate = false;
    totalRow = report.stats.pop()
    sortedStats = (report.stats).sort(sortBy(sortAttribute, desc))
    sortedStats.push(totalRow)
    $('#stats tbody').jqoteapp(stats_tpl, sortedStats);
    alternate = false;
    $('#errors tbody').jqoteapp(errors_tpl, (report.errors).sort(sortBy(sortAttribute, desc)));
});

$("#clear_chart").click(function(event) {
    event.preventDefault();
    plot_data = {"mean":[], "10%":[], "25%":[], "50%":[], "75%":[], "90%":[]};
    start_time = new Date().getTime();
    user_counts_reached = [];
});

// For chart x-axis time labels
Number.prototype.toMMSS = function () {
    sec_numb    = this;
    var minutes = Math.floor(sec_numb / 60);
    var seconds = sec_numb - (minutes * 60);

    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    var time    =  minutes+':'+seconds;
    return time;
}

var plot_data = {"mean":[], "10%":[], "25%":[], "50%":[], "75%":[], "90%":[]};
var user_counts_reached = [];
var start_time = new Date().getTime();
var last_reached = 9;
var user_count = 0;
var time, treshold, closest_treshold, offset;

function updateChart() {
    $.get('/chart/distribution/fetch', function (data) {
        time = (new Date().getTime() - start_time) / 1000;
        report = JSON.parse(data);
        
        // Add the latest data from report
        for (var key in report) {
          if (report[key])
            plot_data[key].push([time,report[key]]);
        }
        if (plot_data.mean.length > 20) { // Max 20 datapoints
          for (var l in plot_data)
            plot_data[l].shift();
        }
        
        // Mark user count thresholds
        threshold = Math.pow(10,Math.floor(Math.log(user_count)/ Math.log(10))); // 10, 100 1000 10000 etc
        closest_threshold = Math.floor(user_count/threshold)*threshold;          // closest threshold reached ex 70, 80, 90, 100, 200, 300 etc
        if (closest_threshold > last_reached) {
          user_counts_reached.push([time, closest_threshold, [plot_data.mean[plot_data.mean.length-1][0], plot_data.mean[plot_data.mean.length-1][1]]]);
          last_reached = closest_threshold;
        }
        if (user_counts_reached.length && user_counts_reached[0][2][0] <= plot_data.mean[0][0]) { // remove points outside the chart
          user_counts_reached.shift();
        }

        dataset = [
        { label: "Average", data: plot_data['mean'], lines: { show: true }, color: "rgb(250,250,250)"},
        { label: "10%-90%", id: 'f10%', data: plot_data['10%'], lines: { show: true, lineWidth: 0, fill: false }, color: "rgba(50,250,50,0.2)" },
        { label: "25%-75%", id: 'f25%', data: plot_data['25%'], lines: { show: true, lineWidth: 0, fill: 0.2 }, color: "rgba(50,250,50,0.4)", fillBetween: 'f10%' },
        { label: "Median", id: 'f50%', data: plot_data['50%'], lines: { show: true, lineWidth: 1, fill: 0.4, shadowSize: 0 }, color: "rgb(50,250,50)", fillBetween: 'f25%' },
        { id: 'f75%', data: plot_data['75%'], lines: { show: true, lineWidth: 0, fill: 0.4 }, color: "rgb(50,250,50)", fillBetween: 'f50%' },
        { id: 'f90%', data: plot_data['90%'], lines: { show: true, lineWidth: 0, fill: 0.2 }, color: "rgb(50,250,50)", fillBetween: 'f75%' },
        ];
        
        if ($("ul.tabs").find("a.current").is("#distribution_link")  // We only draw chart when "Distribution" tab is selected and a test is running
        && $("body").attr("class") != "ready" && $("body").attr("class") != "stopped") {   
        
            var plot = $.plot($("#distribution_chart"), dataset, {
                xaxis: {
                    tickFormatter: function(v, axis) { return v.toMMSS()},
                    tickDecimals: 0,
                    minTickSize: 5,
                    color: "rgb(200,200,200)"
                },
                yaxis: { 
                    tickFormatter: function (v) { return v + " ms"; } ,
                    color: "rgb(200,200,200)"
                },
                legend: {
                    container: $("#chart_legend"),
                    noColumns: 4,
                }
            });

            // Render the user count thresholds
            for(var i=0; i<user_counts_reached.length; i++) {
                offset = plot.pointOffset({x: user_counts_reached[i][2][0], y: user_counts_reached[i][2][1] });
                $("#distribution_chart").append('<div style="position:absolute;left:'+ offset.left + 'px;top:'+
                offset.top +'px;color:#FFF">'+ user_counts_reached[i][1] +' users</div>');
            }
        }
            setTimeout(updateChart, 4000);
    });
}
updateChart();

function updateStats() {
    $.get('/stats/requests', function (data) {
        report = JSON.parse(data);
        $("#total_rps").html(Math.round(report.total_rps*100)/100);
        //$("#fail_ratio").html(Math.round(report.fail_ratio*10000)/100);
        $("#fail_ratio").html(Math.round(report.fail_ratio*100));
        $("#status_text").html(report.state);
        $("#userCount").html(report.user_count);
        user_count = report.user_count;
        if (report.slave_count)
            $("#slaveCount").html(report.slave_count)

        $('#stats tbody').empty();
        $('#errors tbody').empty();

        alternate = false;

        totalRow = report.stats.pop()
        sortedStats = (report.stats).sort(sortBy(sortAttribute, desc))
        sortedStats.push(totalRow)
        $('#stats tbody').jqoteapp(stats_tpl, sortedStats);
        alternate = false;
        $('#errors tbody').jqoteapp(errors_tpl, (report.errors).sort(sortBy(sortAttribute, desc)));
        setTimeout(updateStats, 2000);
    });
}
updateStats();

function updateExceptions() {
    $.get('/exceptions', function (data) {
        $('#exceptions tbody').empty();
        $('#exceptions tbody').jqoteapp(exceptions_tpl, data.exceptions);
        setTimeout(updateExceptions, 5000);
    });
}
updateExceptions();