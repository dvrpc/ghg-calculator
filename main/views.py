from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.embed import components


def index(request):
    return render(request, "main/base.html")


def test_bokeh(request):
    # Graph X & Y coordinates
    x = [1, 2, 3, 4, 5]
    y = [1, 2, 3, 4, 5]

    plot = figure(
        title="Line Graph",
        x_axis_label="X-axis",
        y_axis_label="Y-axis",
        plot_width=400,
        plot_height=400,
    )

    plot.line(x, y, line_width=2)

    script, div = components(plot)

    return render(request, "main/base.html", {"script": script, "div": div})
