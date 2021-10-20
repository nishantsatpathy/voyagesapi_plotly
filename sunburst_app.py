import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json
from sunburst_vars import *


import plotly.express as px

app = dash.Dash(__name__)
server=app.server
r=requests.options('http://127.0.0.1:8000/voyage/')
md=json.loads(r.text)
#print(md)

#print(df)

yr_range=range(1800,1850)
markerstep=5

app.layout = html.Div(children=[
    dcc.Store(id='memory'),
	html.H3("SUNBURST APP -- DOWNLOADS LARGE DATAFRAME (SLOW-ISH), THEN ALLOWS YOU TO FACET IT (FAST)"),
    html.H4("Voyages",id="figtitle"),
    dcc.Graph(
        id='voyages-sunburst-graph'
    ),
    html.Label('Broad Region'),
    dcc.Dropdown(
    	id='broadregion',
        options=[{'label':md[i]['label'],'value':i} for i in geo_sunburst_broadregion_vars],
        value='voyage_itinerary__imp_broad_region_voyage_begin',
        multi=False
    ),
        html.Label('Region'),
    dcc.Dropdown(
    	id='region',
        options=[{'label':md[i]['label'],'value':i} for i in geo_sunburst_region_vars],
        value='voyage_itinerary__first_landing_region',
        multi=False
    ),
        html.Label('Place'),
    dcc.Dropdown(
    	id='place',
        options= [{'label':md[i]['label'],'value':i} for i in geo_sunburst_place_vars],
        value='voyage_itinerary__first_landing_place',
        multi=False
    ),
		html.Label('Numeric Values'),
	dcc.Dropdown(
    	id='numeric-values',
        options= [{'label':md[i]['label'],'value':i} for i in sunburst_plot_values],
        value='voyage_slaves_numbers__imp_total_num_slaves_embarked',
        multi=False
    ),
    dcc.RangeSlider(
        id='year-slider',
        min=1800,
        max=1850,
        step=1,
        value=[1810,1812],
        marks={str(i*markerstep+yr_range[0]):str(i*markerstep+yr_range[0]) for i in range(int((yr_range[-1]-yr_range[0])/markerstep))}
    )
])

@app.callback(
	[Output('memory','data'),Output('figtitle','children')],
	[Input('year-slider','value')]
	)
def update_df(yr):
	print(yr)
	selected_fields=list(set(geo_sunburst_broadregion_vars+geo_sunburst_region_vars+geo_sunburst_place_vars+sunburst_plot_values))
	r=requests.get('http://127.0.0.1:8000/voyage/dataframes?&voyage_dates__imp_arrival_at_port_of_dis_year=%d,%d&selected_fields=%s' %(yr[0],yr[1],','.join(selected_fields)))
	j=r.text
	ft="Voyages: %d-%d" %(yr[0],yr[1])
	return j,ft
	
@app.callback(
	Output('voyages-sunburst-graph', 'figure'),
	[Input('broadregion', 'value'),
	Input('region', 'value'),
	Input('place', 'value'),
	Input('numeric-values', 'value'),
	Input('memory','data')]
	)
def update_figure(broadregion,region,place,numeric_values,j):
	#filtered_df = df[df.year == selected_year]
	df=pd.read_json(j)
	#sub "unknown" for text vars
	df=df.fillna({i:"unknown" for i in geo_sunburst_broadregion_vars+geo_sunburst_region_vars+geo_sunburst_place_vars})
	figtitle=md[numeric_values]['label'] +' by '+ md[broadregion]['label'] +' // ' + md[region]['label'] + ' // ' + md[place]['label']
	fig = px.sunburst(df, path=[broadregion,region,place], values=numeric_values,height=800,title=figtitle)
	fig.update_layout(transition_duration=500)
	return fig

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=False,port=5000)