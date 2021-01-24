from os.path import join, dirname
import numpy as np

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput
from bokeh.plotting import figure

from bokeh.models import CustomJS, Select
from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, Grid, ImageURL, LinearAxis, Plot, Range1d


def create_pannel(id):
    # time series data
    ecg_y = np.loadtxt(join(dirname(__file__), 'data/ts_%s.txt'%id))  # ecg values
    ecg_x = np.arange(len(ecg_y))  # ecg time index
    source_ts = ColumnDataSource(data=dict(x=ecg_x, y=ecg_y))  # time series source
    source_triad = ColumnDataSource(data=dict(x=[0,100,200], y=[0,0,0]))  # triadic motif source
    # 
    pannel_ts = figure(plot_height=200, plot_width=400, title="ECG time series (AF)" if id=='AF' else "ECG time series (non-AF)",
                tools="crosshair,pan,reset,save,wheel_zoom",
                x_range=[0, len(ecg_x)], y_range=[min(ecg_y)-0.5, max(ecg_y)+0.5])

    pannel_ts.line('x', 'y', source=source_ts, line_width=1, line_color='black')
    pannel_ts.line('x', 'y', source=source_triad, line_width=1, line_color='red')
    pannel_ts.scatter('x', 'y', source=source_triad, line_width=3, line_color='red')

    
    D = 3
    shape = np.array([len(range(1, (len(ecg_y)-1)//(D-1) + 1)), len(range(0, len(ecg_y)-(D-1)*1)), D])
    
    # Symmetrized Grad-CAM
    xdr = Range1d(start=0, end=3000)
    ydr = Range1d(start=1500, end=0)

    pannel_nAF = figure(title='Symmetrized Grad-CAM of non-AF class', x_range=xdr, y_range=ydr, plot_width=400, plot_height=200)
    pannel_nAF.image_url(url=[join(dirname(__file__),'data/gcam_nAF_%s.png'%id)], x=0, y=shape[0], w=shape[1], h=shape[0], anchor="bottom_left")
    source_triad_img = ColumnDataSource(data=dict(x=[0], y=[0]))
    pannel_nAF.scatter('x', 'y', source=source_triad_img, size=15, marker='circle_x',line_color="white", fill_color="none", alpha=1)
    pannel_nAF.xaxis.visible = False
    pannel_nAF.xgrid.visible = False
    pannel_nAF.yaxis.visible = False
    pannel_nAF.ygrid.visible = False

    pannel_AF = figure(title='Symmetrized Grad-CAM of AF class', x_range=xdr, y_range=ydr, plot_width=400, plot_height=200)
    pannel_AF.image_url(url=['https://yadongz.com/static/img/ecg/gcam_AF_%s.png'%id], x=0, y=shape[0], w=shape[1], h=shape[0], anchor="bottom_left")
    pannel_AF.scatter('x', 'y', source=source_triad_img, size=15, marker='circle_x',line_color="white", fill_color="none", alpha=1)
    pannel_AF.xaxis.visible = False
    pannel_AF.xgrid.visible = False
    pannel_AF.yaxis.visible = False
    pannel_AF.ygrid.visible = False

    # # Set up widgets
    time_index = Slider(title="x", value=0, start=0, end=shape[1], step=1, width=400)
    delay = Slider(title="y", value=1, start=1, end=shape[0], step=1, width=400)

    # Set up callbacks
    def update_data(attrname, old, new):

        start = time_index.value
        gap = delay.value
        # source_triad_img.data = dict(x=[start], y=[gap-1])

        right_bound = len(ecg_y)-(3-1)*gap
        if start + 1> right_bound:
            start = shape[1] - start - 1
            gap = shape[0] - gap + 1
        
        # Get the current slider values
        triad_x = np.arange(start, start+gap*3, gap)
        # Generate the new curve
        triad_y = ecg_y[triad_x]

        source_triad.data = dict(x=triad_x, y=triad_y)

    for w in [time_index, delay]:
        w.on_change('value', update_data)
    
    return time_index, delay, pannel_ts, pannel_AF, pannel_nAF
    
    # return pannel_ts


time_index_1, delay_1, pannel_ts_1, pannel_AF_1, pannel_nAF_1 = create_pannel('AF')
inputs_1 = column(time_index_1, delay_1)
column_1 = column(inputs_1, pannel_ts_1, pannel_AF_1, pannel_nAF_1, width=400)
'''
time_index_2, delay_2, pannel_ts_2, pannel_AF_2, pannel_nAF_2 = create_pannel('nAF')
inputs_2 = column(time_index_2, delay_2)
column_2 = column(inputs_2, pannel_ts_2, pannel_AF_2, pannel_nAF_2, width=400)
'''
curdoc().add_root(column_1)
curdoc().title = "Inpretable Visualization"
