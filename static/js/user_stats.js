(function() {
    var user_stats = {},
        parse_date = d3.time.format('%Y-%m-%d').parse,
        badge_set_milestones,
        answer_counts;

    // Custom date formatting -- takes current year into account
    var format_date = (function() {
        var month     = d3.time.format('%b'),
            day       = function(d) { return '' + (+d3.time.format('%d')(d)); },
            year      = function(d) { return "'" + ('' + d.getFullYear()).substring(2); }
            this_year = new Date().getFullYear();

        return function(d) {
            var output = month(d) + ' ' + day(d);
            if(d.getFullYear() !== this_year)
                output += ' ' + year(d);

            return output;
        };
    })();

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
        width  = opts.width - opts.margin.left - opts.margin.right
                    - opts.inner_margin.left - opts.inner_margin.right;
        height = opts.height - opts.margin.top - opts.margin.bottom
                    - opts.inner_margin.top - opts.inner_margin.bottom;
        var svg = d3.select(opts.container)
                    .append('svg')
                        .attr('class', 'chart')
                        .attr('width', opts.width)
                        .attr('height', opts.height)
                    .append('g')
                        .attr('transform', 'translate(' + opts.margin.left + ','
                                + opts.margin.top + ')');
        var x = d3.time.scale()
                  .domain(d3.extent(badge_set_milestones, function(d) { return d.date; }))
                  .range([0, width]);
        var y = d3.scale.linear()
                  .domain([0, d3.max(badge_set_milestones, function(d) { return d.badge_set; })])
                  .rangeRound([height, 0]);
        var x_axis = d3.svg.axis()
                       .scale(x)
                       .orient('bottom')
                       .tickFormat(format_date)
                       .outerTickSize(0);
        var y_axis = d3.svg.axis()
                       .scale(y)
                       .orient('left')
                       .ticks(y.domain()[1])
                       .tickFormat(d3.format('d'))
                       .outerTickSize(0);

        var line = d3.svg.line()
                     .x(function(d) { return x(d.date); })
                     .y(function(d) { return y(d.badge_set); })
                     .interpolate('step-after');

        var inner = svg.append('g')
                        .attr('class', 'inner')
                        .attr('transform', 'translate(' + opts.inner_margin.left + ','
                                    + opts.inner_margin.top + ')');

        inner.append('path')
           .datum(badge_set_milestones)
           .attr('d', line)
           .style('fill', 'none');

        svg.append('g')
           .attr('class', 'x axis')
           .attr('transform', 'translate(' + opts.inner_margin.left + ',' +
                (height + opts.inner_margin.top + opts.inner_margin.bottom) + ')')
           .call(x_axis)
           .selectAll('text')
                .style('text-anchor', 'end')
                .style('transform', 'rotate(-45deg)')
                .attr('dx', '-.5em')
                .attr('dy', '.5em');

        svg.append('g')
           .attr('class', 'y axis')
           .attr('transform', 'translate(0,' + opts.inner_margin.top + ')')
           .call(y_axis);
    };

    // Expose a lightweight public interface
    user_stats.badge_set_milestones = [];
    user_stats.answer_counts = [];
    user_stats.render_all = function() {
        preprocess();
        render_milestones({
            container: '#stats-milestones',
            width:     700,
            height:    300,
            margin:    { top:    20,
                         right:  20,
                         bottom: 80,
                         left:   50 },
            inner_margin: { top:    0,
                            right:  0,
                            bottom: 0,
                            left:   10 }
            });
    };
    window.user_stats = user_stats;
})();
