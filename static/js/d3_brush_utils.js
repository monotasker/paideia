// Utility brush control functions from http://wrobstory.github.io/2013/11/D3-brush-and-tooltip.html

function brushmove(brush) {
  var extent = brush.extent();
  points.classed("selected", function(d) {
    is_brushed = extent[0] <= d.index && d.index <= extent[1];
    return is_brushed;
  });
}

function brushend() {
  get_button = d3.select(".clear-button");
  if(get_button.empty() === true) {
    clear_button = svg.append('text')
      .attr("y", 460)
      .attr("x", 825)
      .attr("class", "clear-button")
      .text("Clear Brush");
  }

  x.domain(brush.extent());

  transition_data();
  reset_axis();

  points.classed("selected", false);
  d3.select(".brush").call(brush.clear());

  clear_button.on('click', function(){
    x.domain([0, 50]);
    transition_data();
    reset_axis();
    clear_button.remove();
  });
}

function transition_data() {
  svg.selectAll(".point")
    .data(data)
  .transition()
    .duration(500)
    .attr("cx", function(d) { return x(d.index); });
}

function reset_axis() {
  svg.transition().duration(500)
   .select(".x.axis")
   .call(xAxis);
}
