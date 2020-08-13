from django.shortcuts import render

from bokeh.plotting import figure, curdoc
from bokeh.client import pull_session
from bokeh.embed import components, server_session

from . import ghg_calc as ghg


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


def population(request):
    url = "http://localhost:5006/ghg_calc"

    with pull_session(url=url) as session:

        # generate a script to load the customized session
        script = server_session(session_id=session.id, url=url)
        # script = server_session(model=session.root.barchart)
        # print(session.__dir__())
        # print(session.document.__dir__())
        # print(session.document.roots)
        # for root in session.document.roots:
        #     print(root.name)

        # use the script in the rendered page
        return render(request, "main/bokeh.html", {"script": script})
