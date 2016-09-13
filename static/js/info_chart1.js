function attempts_modal(ids) {
    if ( $('#attempts-modal').length == 0 ) {
        modalframe = '<div class="modal fade" tabindex="-1" role="dialog" id="attempts-modal">';
        modalframe += '<div class="modal-dialog attempts-modal">';
        modalframe += '<div class="modal-content">';
        modalframe += '<div class="modal-header">';
        modalframe += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">';
        modalframe += '<span aria-hidden="true">&times;</span></button>';
        modalframe += '<h4 class="modal-title">Attempts for the day</h4>';
        modalframe += '</div>';
        modalframe += '<div class="modal-body attempts-modal" id="attempts-modal-body">';
        modalframe += '</div>';
        modalframe += '<div class="modal-footer">';
        modalframe += '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';
        modalframe += '</div>';
        modalframe += '</div><!-- /.modal-content -->';
        modalframe += '</div><!-- /.modal-dialog -->';
        modalframe += '</div><!-- /.modal -->';
        $('body').append(modalframe);
    };
    $('#attempts-modal').modal('show');
    ajax('/paideia/default/get_day_attempts?ids=' + ids, [], 'attempts-modal-body');
}

function showChart1(my_raw_data, update_url, user_id) {

    // set chart1 variables
    var margin = { left: 42, right: 90, top: 10, bottom: 180 },
        navMargin = {top: 300, right: 90, bottom: 80, left: 42},
        height = 400 - margin.top - margin.bottom,
        width = 800 - margin.left - margin.right,
        navWidth = width, // for context band
        navHeight = 400 - navMargin.top - navMargin.bottom;
        data = prep_chart_data(my_raw_data);

    var format_time = d3.time.format('%b %e, %Y');

    // helper functions
    function prep_chart_data(raw_json) {
        var data = JSON.parse(raw_json);
        // preprocess data to get usable date objects
        var parse_date = d3.time.format('%Y-%m-%d').parse
        for (var i in data) {
            var myObj = data[i]
            for (var j in myObj) {
                myObj[j].date = parse_date(myObj[j].date);
            }
        }
        console.log(data);
        return data;
    }

    function drawBars(mydata) {
    // Plot the stacked bars
        focus.selectAll('.g.bar.stack').remove();
        context.selectAll('.g.bar.stack').remove();
        var focus_bar = focus
                            .append("g") //<-- g just for the bars to be clipped
                            .attr("class","barClipper")
                            .style('clip-path', 'url(#clipFocus)')
                 .selectAll('.g')
                     .data(mydata.answer_counts)
                 .enter().append('g')
                    .attr('class', 'g bar stack')
                    .attr('transform', function(d) {
                                            return "translate(" + (x(d.date) - x.rangeBand()/2) + ",0)" });

        var focus_rects = focus_bar.selectAll('rect')
                        .data(function(d) { return d.ys; })
                     .enter().append('rect')
                        .attr('width', x.rangeBand())
                        .attr('height', function(d) { return y(d.y0) - y(d.y1); })
                        .attr('y', function(d) { return y(d.y1); })
                        .attr('class', function(d) { return 'rect ' + d['class']; });

        var context_bar = context
                            .append("g") //<-- g just for the bars to be clipped
                            .attr("class","barClipper")
                            .style('clip-path', 'url(#clipNav)')
                  .selectAll('.g')
                     .data(mydata.answer_counts)
                 .enter().append('g')
                    .attr('class', 'g bar stack')
                    .attr('transform', function(d) {
                                            return "translate(" + (x(d.date) - x.rangeBand()/2) + ",0)" });

        var context_rects = context_bar.selectAll('rect')
                        .data(function(d) { return d.ys; })
                     .enter().append('rect')
                        .attr('width', navX.rangeBand())
                        .attr('height', function(d) { return navY(d.y0) - navY(d.y1); })
                        .attr('y', function(d) { return navY(d.y1); })
                        .attr('class', function(d) { return 'rect ' + d['class']; });
    }

    function brushed(my_x, my_x_axis, my_time) {
        my_x = my_x || x;
        my_x_axis = my_x_axis || axes.x_axis;
        my_time = my_time || time;
        my_time.domain(brush.empty() ? navTime.domain() : brush.extent())
            .range([0, width]);
        my_x.domain(max_extent_in_days(my_time))
            .rangeBands([0, width], 0.1, 0);
        focus.selectAll('.bar.stack')
            .attr('transform', function(d) {return "translate(" + (my_time(d.date) - (my_x.rangeBand()/2)) + ",0)"; })
            .attr('width', my_x.rangeBand())
        focus.selectAll('.rect')
            .attr('width', my_x.rangeBand());
        focus.selectAll('.line').attr('d', line);
        svg.select(".x.axis")
            .call(my_x_axis)
            .selectAll('text')
                .style('text-anchor', 'end')
                .attr('transform', 'rotate(-45)')
                .attr('dx', '-.5em')
                .attr('dy', '.5em');
    };

    function updateChart1Data(raw_json) {
        // Get the data again
        data = prep_chart_data(raw_json);

        // update scales with new data
        var max_total_counts = d3.max(data.answer_counts, function(d) { return d.total; });
        var max_extent_dates = d3.extent(data.answer_counts, function(d) { return d.date; });
        var max_extent_in_days = function(timescale) {
            return d3.time.days(timescale.domain()[0], d3.time.day.offset(timescale.domain()[1], 1));
        }
        y.domain([0, max_total_counts]);
        navY.domain([0, max_total_counts]);
        time.domain(max_extent_dates);
        navTime.domain(max_extent_dates);
        x.domain(max_extent_in_days(time));
        navX.domain(max_extent_in_days(navTime));

        // Apply changes to bars
        drawBars(data);

        // Update axes
        axes = setAxes(time, navTime, y, y2);
        svg.select(".x.axis").call(axes.x_axis);
        svg.select(".y.axis").call(axes.y_axis);
        svg.select(".navX.axis").call(axes.nav_x_axis)

        // Re-apply brush selection
        brushed(x, axes.x_axis, time);
    };

    // scales
    var max_total_counts = d3.max(data.answer_counts, function(d) { return d.total; });
    var max_extent_dates = d3.extent(data.answer_counts, function(d) { return d.date; });
    function max_extent_in_days(timescale) {
        return d3.time.days(timescale.domain()[0], d3.time.day.offset(timescale.domain()[1], 1));
    };
    var y = d3.scale.linear().domain([0, max_total_counts]).rangeRound([height, 0]),
        navY = d3.scale.linear().domain([0, max_total_counts]).rangeRound([navHeight, 0]),
        time = d3.time.scale().domain(max_extent_dates).range([0, width]),
        navTime = d3.time.scale().domain(max_extent_dates).range([0, width]),
        x = d3.scale.ordinal().domain(max_extent_in_days(time)).rangeBands([0, width], 0.1, 0), // used to calculate bar widths
        navX = d3.scale.ordinal().domain(max_extent_in_days(navTime)).rangeBands([0, width], 0.1, 0),
        y2 = d3.scale.linear().domain([0, d3.max(data.badge_set_reached, function(d) { return d.set})]).rangeRound([height, 0]),
        navY2 = d3.scale.linear().domain([0, d3.max(data.badge_set_reached, function(d) { return d.set})]).rangeRound([navHeight, 0]);
    //debugging
    console.log(time);
    console.log(max_extent_in_days(time));

    function setAxes(time, navTime, y, y2) {
        var x_axis = d3.svg.axis().scale(time).orient('bottom') //    .tickFormat(d3.time.format('%Y-%m-%d'))
                       .outerTickSize(0),  // at start and end of axis line
            nav_x_axis = d3.svg.axis().scale(navTime).orient('bottom') //    .tickFormat(d3.time.format('%Y-%m-%d'))
                           .outerTickSize(0),  // at start and end of axis line
            y_axis = d3.svg.axis().scale(y).orient('left').tickFormat(d3.format('d'));
            y2_axis = d3.svg.axis().scale(y2).orient('right').tickFormat(d3.format('d'));
        return {
            x_axis: x_axis,
            nav_x_axis: nav_x_axis,
            y_axis: y_axis,
            y2_axis: y2_axis
        };
    }

    axes = setAxes(time, navTime, y, y2);

    // svg context
    var svg = d3.select("#milestones_attempts_combo")
         .append('svg')
            .attr('class', 'chart')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
         .append('g')
            .attr('transform', 'translate(' + margin.left + ','
                    + margin.top + ')');

    var focus = svg.append('g')
        .attr('class', 'focus')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    var context = svg.append('g')
        .attr('class', 'context')
        .attr('transform', 'translate(' + navMargin.left + ',' + navMargin.top + ')');

    // clipping for content update
    svg.append("defs").append("clipPath")
        .attr("id", "clipFocus")
        .append("rect")
        .attr("width", width)
        .attr("height", height);

    svg.append("defs").append("clipPath")
        .attr("id", "clipNav")
        .append("rect")
        .attr("width", navWidth)
        .attr("height", navHeight);

    // Draw bars
    drawBars(data);

    // Plot line
    var line = d3.svg.line()
                .x(function(d) {return time(d.date)})
                .y(function(d) {return y2(d.set)})
                .interpolate('step-after');
    var focus_line = focus
                        .append("g") //<-- g just for the bars to be clipped
                        .attr("class","barClipper")
                        .style('clip-path', 'url(#clipFocus)')
                    .append('path')
                        .datum(data.badge_set_reached)
                        .attr('class', 'line focus-line')
                        .attr('d', line);

    var line2 = d3.svg.line()
                .x(function(d) {return time(d.date)})
                .y(function(d) {return navY2(d.set)})
                .interpolate('step-after');
    var context_line = context
                        .append("g") //<-- g just for the bars to be clipped
                        .attr("class","barClipper")
                        .style('clip-path', 'url(#clipNav)')
                    .append('path')
                        .datum(data.badge_set_reached)
                        .attr('class', 'line context-line')
                        .attr('d', line2);

    // Draw axes
    svg.append('g')
       .attr('class', 'x axis')
       .attr('transform', 'translate(' + margin.left + ', ' + (height + margin.top) + ')')
       .call(axes.x_axis)
       .selectAll('text')
            .style('text-anchor', 'end')
            .attr('transform', 'rotate(-45)')
            .attr('dx', '-.5em')
            .attr('dy', '.5em');

    svg.append('g')
       .attr('class', 'y axis')
       .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')')
       .call(axes.y_axis);

    svg.append('g')
       .attr('class', 'y2 axis')
       .attr('transform', 'translate(' + (width + margin.left) + ', ' + margin.top + ')')
       .call(axes.y2_axis);

    svg.append('g')
        .attr('class', 'navX axis')
        .attr('transform', 'translate(' + margin.left + ', ' + (navMargin.top + navHeight) + ')')
        .call(axes.nav_x_axis)
        .selectAll('text')
            .style('text-anchor', 'end')
            .attr('transform', 'rotate(-45)')
            .attr('dx', '-.5em')
            .attr('dy', '.5em');

    // remove 0 ticks
    svg.selectAll(".tick")
        .filter(function (d) { return d === 0;  })
        .remove();

    // Label axes

    svg.append('text')
        .attr('class', 'label y-axis-label')
        .attr('transform', 'rotate(-90)')
        .attr('x', 0 - ((height + margin.top) / 2))
        .attr('y', 0)
        .style('text-anchor', 'middle')
        .text('Paths Attempted');

    svg.append('text')
        .attr('class', 'label y2-axis-label')
        .attr('transform', 'rotate(90)')
        .attr('x', ((height + margin.top) / 2))
        .attr('y', -(width + margin.left))
        .attr('dy', -(margin.right / 3))
        .style('text-anchor', 'middle')
        .text('Badge Set Reached');

    // define brush
    var brush = d3.svg.brush()
        .x(navTime)
        .on("brush", brushed);

    // Add brush to svg
    context.append('g')
        .attr('class', 'x brush')
        .call(brush)
    .selectAll("rect")
      .attr("y", -6)
      .attr("height", navHeight + 7);

    // Add tooltips
    tooldiv = d3.select('body').append('div')
                .attr("class", "chart1 tooltip ")
                .style('opacity', 0);

    focus.selectAll('.g.bar.stack')
        .on('mouseover', function(d) {
            var matrix = this.getScreenCTM();
            var date = format_time(d.date);
            var rNum = d.ys[0]['y1'];
            var wNum = parseInt(d.ys[1]['y1']) - parseInt(d.ys[1]['y0']);
            tooldiv
                .html(function() {
                    return date + '<br/>' + rNum + ' right<br/>' + wNum + ' wrong';
                })
                .style('left', (window.pageXOffset + matrix.e) + 'px')
                .style('top', (window.pageYOffset + matrix.f) + 'px')
                .style('opacity', 1);
        })
        .on('mouseout', function(d) {
            tooldiv
                .style('opacity', 0);
        })
        .on('click', function(d) {
            attempts_modal(d.ids);
        });

    // update chart1 data via ajax when set selected
    $('#badge_set_chooser').on('change', function(e) {
        var myset = $(this).val();
        var myurl = update_url + '?set=' + myset + '&user_id=' + user_id;
        $.get(myurl, function(data){
            console.log('got ajax data', $.parseJSON(data));
            updateChart1Data(data);
        });
    });
};
