from bokeh.layouts import column
from bokeh.plotting import curdoc

from ghg_calc import grid_inputs, res_inputs, ci_inputs, bar_chart, stacked_bar_chart, pie_chart


curdoc().add_root(column(grid_inputs, res_inputs, ci_inputs))
curdoc().add_root(column(bar_chart, stacked_bar_chart, pie_chart))
