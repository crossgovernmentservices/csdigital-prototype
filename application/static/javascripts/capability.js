(function($, window){

  var capData = {
    labels: ["2013", "2014", "2015", "2016"],
    datasets: [
        {
            label: "Awareness",
            strokeColor: "#912B88",
            pointColor: "#912B88",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data: [50000, 56000, 66000, 80000]
        },
        {
            label: "Working",
            strokeColor: "#D53880",
            pointColor: "#D53880",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data: [30000, 36000, 38000, 40000]
        },
        {
            label: "Practitioner",
            strokeColor: "#F47738",
            pointColor: "#F47738",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data: [5000, 12000, 23000, 40000]
        },
        {
            label: "Expert",
            strokeColor: "#85994B",
            pointColor: "#85994B",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data: [1000, 1200, 1275, 1700]
        }]
  };

  var ctx = document.getElementById("capChart").getContext("2d");
  var myLineChart = new Chart(ctx).Line(capData, {
    datasetFill : false,
    legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].strokeColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
  });

  $(function() {
    $(".capability-btns").on('click', 'a', function() {
      var for_selector = $(this).parents(".capability-btns").data('svg-for');
      var svg = $( "." + for_selector );
      console.log($(this).data('class-to-add'));
      svg.attr( "class", for_selector + " " + $(this).data('class-to-add') );
      $(this)
        .parents(".capability-btns")
          .find("a")
            .removeClass("active")
          .end()
        .end()
      .addClass("active");

      return false;
    });
  });
}).call(this, jQuery, window);
