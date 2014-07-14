(function() {
    var user_stats = {},
        parse_date = d3.time.format('%Y-%m-%d').parse,
        badge_set_milestones,
        answer_counts;


    // Preprocess server-supplied data
    var preprocess = function() {
        badge_set_milestones = user_stats.badge_set_milestones
            .map(function(d) {
                d.date = parse_date(d.date);
                d.badge_set |= 0;
                return d;
            });

        answer_counts = user_stats.answer_counts
            .map(function(d) {
                d.date = parse_date(d.date);
                d.right |= 0;
                d.wrong |= 0;
            });
    };

    // @TODO: Factor out a Chart class
    var render_milestones = function(opts) {
        // @TODO: Defaults `opts`
        width  = opts.width - opts.margin.left - opts.margin.right;
        height = opts.height - opts.margin.top - opts.margin.bottom;
        var svg = d3.select(opts.container)
                    .append('svg')
                        .attr({ width: opts.width, height: opts.height })
                    .append('g')
                        .attr('transform', 'translate(' + opts.margin.left + ','
                                + opts.margin.top + ')');
        var x = d3.time.scale()
                  .domain(d3.extent(badge_set_milestones, function(d) { return d.date; }))
                  .range([0, width]);
        var y = d3.scale.linear()
                  .domain(d3.extent(badge_set_milestones, function(d) { return d.badge_set; }))
                  .rangeRound([height, 0]);
        var x_axis = d3.svg.axis()
                       .scale(x)
                       .orient('bottom')
                       .ticks(d3.time.day)
                       .tickFormat(d3.time.format('%b %d'));
        var y_axis = d3.svg.axis()
                       .scale(y)
                       .orient('left')
                       .tickFormat(d3.format('d'));


        var line = d3.svg.line()
                     .x(function(d) { return x(d.date); })
                     .y(function(d) { return y(d.badge_set); })
                     .interpolate('step-after');

        svg.selectAll('circle').data(badge_set_milestones).enter()
            .append('circle').attr({
                r: 4,
                cx: function(d) { return x(d.date); },
                cy: function(d) { return y(d.badge_set); }
            }).style('fill', 'steelblue');

        svg.append('path')
           .datum(badge_set_milestones)
           .attr('d', line)
           .style({ stroke: 'steelblue', 'stroke-width': 2, fill: 'none' });

        svg.append('g')
           .attr('class', 'x axis')
           .attr('transform', 'translate(0,' + height + ')')
           .call(x_axis);

        svg.append('g')
           .attr('class', 'y axis')
           .call(y_axis);
    };

    // Expose a lightweight public interface
    user_stats.badge_set_milestones = [];
    user_stats.answer_counts = [];
    user_stats.render_all = function() {
        preprocess();
        render_milestones({
            container: '#stats-milestones',
            width:     400,
            height:    200,
            margin:    { top:    20,
                         right:  20,
                         bottom: 40,
                         left:   40 }
            });
    };
    window.user_stats = user_stats;
})();
