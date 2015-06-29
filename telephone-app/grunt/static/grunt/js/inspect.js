function visualize(chain) {
  chain = JSON.parse(chain);

  var nestedMessages = chain.messages;

  var maxWidth = 5,
      widthPerChain = 120,
      maxDepth = 4,
      heightPerGeneration = 200;

  var svgWidth = maxWidth * widthPerChain,
      svgHeight = maxDepth * heightPerGeneration;

  var bumpDown = 40;
  var circleSize = 40;

  treeChart = d3.layout.tree();
  treeChart.size([svgWidth, svgHeight-(2*bumpDown)])
    .children(function(d) { return d.children });

  var linkGenerator = d3.svg.diagonal()
    .projection(function (d) {return [d.x, d.y+bumpDown]})

  var bumpTextsRight = 30,
      bumpTextsDown = -5,
      buttonGutter = 20;

  var containerWidth = parseFloat(d3.select("div.container").style("max-width"));
  if (containerWidth < svgWidth) {
    d3.select("div.container").style("max-width", (svgWidth + 2*bumpDown + bumpTextsRight) + "px");
  }

  var svg = d3.select("svg");

  // Clear the previous chain
  svg
    .selectAll("g")
    .remove();

  svg
    .selectAll("path")
    .remove();

  // Adjust the size of the svg element
  svg
    .attr("width", svgWidth + bumpTextsRight)
    .attr("height", svgHeight)

  // Bind the message data into g elements
  svg
    .selectAll("g.message")
    .data(treeChart(nestedMessages))
    .enter()
    .append("g")
    .attr("class", function (message) {
      var type = message.audio ? "filled" : "empty";
      return "message " + type;
    })
    .attr("transform", function (message) {
      return "translate(0," + circleSize + ")";
    });

  // Add the links
  svg
    .selectAll("path")
    .data(treeChart.links(treeChart(nestedMessages)))
    .enter().insert("path","g")
    .attr("d", linkGenerator)
    .style("fill", "none")
    .style("stroke", "black")
    .style("stroke-width", "2px");

  var messages = svg.selectAll("g.message");

  // Create a circle for each message
  messages
    .append("circle")
    .attr("r", 20)
    .attr("cx", function (message) { return message.x; })
    .attr("cy", function (message) { return message.y; })

  // Label each circle
  messages
    .append("text")
    .text(function (message) { return message.pk; })
    .attr("x", function (message) { return message.x; })
    .attr("y", function (message) { return message.y; })
    .attr("text-anchor", "middle")
    .attr("dy", ".35em")
    .style("fill", function (message) {
      return message.audio ? "white" : "black";
    });

  var filled = svg.selectAll("g.filled")

  // Add play button
  filled
    .append("text")
    .attr("x", function (message) { return message.x + bumpTextsRight; })
    .attr("y", function (message) { return message.y + bumpTextsDown; })
    .text("play")
    .on("click", function (message) {
      $("audio").attr("src", message.audio);
      $("audio").trigger("play");
    });

  // Add split button
  filled
    .append("text")
    .attr("x", function (message) { return message.x + bumpTextsRight; })
    .attr("y", function (message) { return message.y + bumpTextsDown + buttonGutter; })
    .text("split")
    .on("click", function (message) {
      $.post(message.sprout_url,
        {csrfmiddlewaretoken: csrf_token},
        function (data) { visualize(data); }
      );
    });

  var empty = svg.selectAll("g.empty");

  // Add upload button
  empty
    .append("text")
    .attr("x", function (message) { return message.x + bumpTextsRight; })
    .attr("y", function (message) { return message.y + bumpTextsDown; })
    .text("upload")
    .on("click", function (message) {
      window.location.href = message.upload_url;
    })

  // Add close button
  empty
    .append("text")
    .attr("x", function (message) { return message.x + bumpTextsRight; })
    .attr("y", function (message) { return message.y + bumpTextsDown + buttonGutter; })
    .text("close")
    .on("click", function (message) {
      $.post(message.close_url,
        {csrfmiddlewaretoken: csrf_token},
        function (data) { visualize(data); }
      );
    })

  var nodes = messages.selectAll("circle");

  nodes
    .on("click", function (message) {
      var circle = d3.select(this);
      circle.classed("active", !circle.classed("active"));
    });

}
