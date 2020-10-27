from bokeh.layouts import column
from bokeh.plotting import curdoc

from ghg_calc import population_inputs, bar_chart, stacked_bar_chart, pie_chart

doc = curdoc()
doc.add_root(population_inputs)
doc.add_root(column(bar_chart, stacked_bar_chart, pie_chart))
