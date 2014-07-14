(function() {
    var user_stats = {},
        parse_date = d3.time.format('%Y-%m-%d').parse,
        badge_set_milestones,
        answer_counts;

    // Custom date formatting -- takes current year into account
    var format_date = (function() {
        var day       = d3.time.format('%d'),
            month     = d3.time.format('%b'),
            year      = function(d) { return d3.format('02d')(d.getFullYear() % 100); },
            this_year = new Date().getFullYear();

        return function(d) {
            var output = month(d) + ' ' + (+day(d));
            if(d.getFullYear() !== this_year)
                output += " '" + year(d);

            return output;
        };
    })();

    // Preprocess server-supplied data
    var preprocess = function() {
        badge_set_milestones = user_stats.badge_set_milestones
            .map(function(d) {
                d.date = parse_date(d.date);
                return d;
            });

        answer_counts = user_stats.answer_counts
            .map(function(d) {
                d.date  = parse_date(d.date);
                d.total = d.right + d.wrong
                d.ys    = [{ 'class': 'right', y0: 0, y1: d.right },
                           { 'class': 'wrong', y0: d.right, y1: d.right + d.wrong }];
                return d;
            });
    };

    // TODO: Factor out a Chart class
    var render_milestones = function(opts) {
        // TODO: Defaults `opts`
        // Conventional margins
        width  = opts.width - opts.margin.left - opts.margin.right
                    - opts.inner_margin.left - opts.inner_margin.right;
        height = opts.height - opts.margin.top - opts.margin.bottom
                    - opts.inner_margin.top - opts.inner_margin.bottom;

        // Set up axes
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

        // Construct SVG container
        var svg = d3.select(opts.container)
                    .append('svg')
                        .attr('class', 'chart')
                        .attr('width', opts.width)
                        .attr('height', opts.height)
                    .append('g')
                        .attr('transform', 'translate(' + opts.margin.left + ','
                                + opts.margin.top + ')');

        // Generator for the data line
        var line = d3.svg.line()
                     .x(function(d) { return x(d.date); })
                     .y(function(d) { return y(d.badge_set); })
                     .interpolate('step-after');

        // Plot the data
        var inner = svg.append('g')
                        .attr('class', 'inner')
                        .attr('transform', 'translate(' + opts.inner_margin.left + ','
                                    + opts.inner_margin.top + ')');

        inner.append('path')
           .datum(badge_set_milestones)
           .attr('d', line)
           .style('fill', 'none');

        // Plot axes
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

    var render_answers = function(opts) {
        // Conventional margins
        width  = opts.width - opts.margin.left - opts.margin.right
                    - opts.inner_margin.left - opts.inner_margin.right;
        height = opts.height - opts.margin.top - opts.margin.bottom
                    - opts.inner_margin.top - opts.inner_margin.bottom;

        // Set up axes
        var time = d3.time.scale()
                     .domain(d3.extent(answer_counts, function(d) { return d.date; }))
                     .range([0, width]);
        var x = d3.scale.ordinal()
                  .domain(d3.time.days(time.domain()[0],
                                       d3.time.day.offset(time.domain()[1], 1)))
                  .rangeBands([0, width], 0, 0);
        var y = d3.scale.linear()
                  .domain([0, d3.max(answer_counts, function(d) { return d.total; })])
                  .rangeRound([height, 0]);
        var x_axis = d3.svg.axis()
                       .scale(time)
                       .orient('bottom')
                       .tickFormat(format_date)
                       .outerTickSize(0);
        var y_axis = d3.svg.axis()
                       .scale(y)
                       .orient('left')
                       .tickFormat(d3.format('d'))
                       .outerTickSize(0);

        // Construct SVG container
        var svg = d3.select(opts.container)
                    .append('svg')
                        .attr('class', 'chart')
                        .attr('width', opts.width)
                        .attr('height', opts.height)
                    .append('g')
                        .attr('transform', 'translate(' + opts.margin.left + ','
                                + opts.margin.top + ')');

        // Plot the data
        var inner = svg.append('g')
                        .attr('class', 'inner')
                        .attr('transform', 'translate(' + opts.inner_margin.left + ','
                                    + opts.inner_margin.top + ')');

        var group = inner.selectAll('.g')
                         .data(answer_counts)
                     .enter().append('g')
                        .attr('class', 'g')
                        .attr('transform', function(d) { return 'translate(' + x(d.date) + ',0)'; });
        group.selectAll('rect')
                .data(function(d) { return d.ys; })
             .enter().append('rect')
                .attr('width', x.rangeBand())
                .attr('height', function(d) { return y(d.y0) - y(d.y1); })
                .attr('y', function(d) { return y(d.y1); })
                .attr('class', function(d) { return d['class']; });

        // Plot axes
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
        render_answers({
            container: '#stats-answers',
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
