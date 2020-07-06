#data
import os
import pandas as pd
import numpy as np
from datetime import datetime as dt
import math

#dashboard
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_ui as dui
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px


#directory
os.chdir(r'D:\Users\Sanja\Desktop\Air_Pollution')

#execute Air_Data_realtime.py script fot getting data
#exec(open('Air_Data_Realtime.py').read())


#import data from existing csv file
air=pd.read_csv('air_pollution_realtime.csv')

#design (used for grid setup)
app=dash.Dash(__name__, assets_url_path='Assets/man.css')



# html and dcc components
def header():
    return  html.Div(
        id='id-header',
        children=[
        #Title
        html.H1('AIR POLLUTION SERBIA',style={'color': 'darksalmon','text-align':'center'}),
        #Line
        html.Div(style={'border':'2px indianred solid'}),
        #Subtitle
        html.H6('Daily pollution data on the territory of Serbia',style={'font-size': '21px','color':'lightsalmon'}),
        ]
    )

def station_dropdown():
    #last day by default
    air_by_date=air[air['Day']==air['Day'].iloc[-1]]
    
    #find station for specific date
    stations=[]
    for name,id in zip(air_by_date['Station_Name'].unique(),air_by_date['Station_ID'].unique()):
        stations.append({'label':name,'value':id})

    return html.Div([
            #Line1
            html.Div(style={'border':'2px darksalmon solid'}),
            #Title
            html.Label('Choose Station',style={'font-size': '15px','color':'lightsalmon'}),
            #Line2
            html.Div(style={'border':'1px darksalmon solid'}),

            dcc.Dropdown(
                id='id-station',
                options=stations,
                value=stations[0].get('value'),
                style={'border': 'hidden',
                       'font-size':'13 px',   
                    },
            ),
           
        ])

def component_multidropdown():
    #last day by default
    air_by_date=air[air['Day']==air['Day'].iloc[-1]]

    #first station default day used as default
    air_by_date_stat=air_by_date[air_by_date['Station_ID']==air_by_date['Station_ID'].iloc[0]]

    #get unique component(pollutant) based on schoosen date and station
    pollutant=[]
    for name,id in zip(air_by_date_stat['Component_Name'].unique(),air_by_date_stat['Component_ID'].unique()):
        pollutant.append({'label':name,'value':id})

    return html.Div(
            children=[
            html.Div(style={'border':'2px darksalmon solid'}),
            html.Label('Choose Pollution Component',style={'font-size': '15px','color':'lightsalmon'}),
            html.Div(style={'border':'1px darksalmon solid'}),

            dcc.Dropdown(
                id='id-component',
                options=pollutant,
                multi=True,
                value=[pollutant[i].get('value') for i in range(0,len(pollutant))],
                style={ 'border': 'hidden',
                        'font-size':'13 px',
                    },
            ),
        ])

def data_picker():
    return html.Div([

            html.Div(style={'border':'2px darksalmon solid'}),
            html.Label('Choose Date',style={'font-size': '15px','color':'lightsalmon'}),
            html.Div(style={'border':'1px darksalmon solid'}),

            dcc.DatePickerSingle(
                id='date-picker-single',
                min_date_allowed=air['Day'].iloc[1],
                max_date_allowed=air['Day'].iloc[-1],
                date=air['Day'].iloc[-1],
                style={'border':'hidden'},
        ),
    ])

def line_chart():
    #last day by default
    air_by_date=air[air['Day']==air['Day'].iloc[-1]]
    #first station default day used as default
    air_by_date_stat=air_by_date[air_by_date['Station_ID']==air_by_date['Station_ID'].iloc[0]]

    traces=[]
    for id in air_by_date_stat['Component_ID'].unique():
            #data by single component
            data_by_comp=air_by_date_stat[air_by_date_stat['Component_ID']==id] 
            name_of_com=str(data_by_comp['Component_Name'].unique())[2:-2] +' in '+ str(data_by_comp['Unit'].unique())[2:-2]

            traces.append(go.Scatter(
                        x =data_by_comp['Hour'],
                        y =data_by_comp['Value'],
                        mode = 'markers+lines',     
                        name = name_of_com))
    return html.Div([
            html.H3('DAILY AIR POLLUTION (STATION) ',style={'color': 'lightsalmon','text-align':'center'}),
            dcc.Graph(
                id='line-graph',
                figure={
                        'data': traces,
                        'layout': go.Layout(
                            xaxis={'title':'HOURS'},
                            yaxis={'title':'COMPONENT'},
                            height= 500,
                        
                            margin={'l':100,'r':50,'t':60}, 
                            font={'color':'lightsalmon'}  
                        )   
                    },
                style={'width': '100%', 'height':'50%'},
            ),
            html.Div(style={'border':'2px darksalmon solid'}),   
        ]
    )


def serbia_map():
    #last day by default
    air_by_date=air[air['Day']==air['Day'].iloc[-1]]

    #separated by stations
    map_data_by_location=[]    
    for station in air_by_date['Station_ID'].unique():
        air_by_date_stat=air_by_date[air_by_date['Station_ID']==station] 

        #max value for specific station
        for name,id in zip(air_by_date_stat['Component_Name'].unique(),air_by_date_stat['Component_ID'].unique()):

            #max value for specific component in that place
            com_max=round(air_by_date_stat.loc[air_by_date_stat['Component_ID']==id,'Value'].max(),2)
            #position of max value
            com_max_id=air_by_date_stat.loc[air_by_date_stat['Component_ID']==id,['Value']].idxmax() 
        
            #get location for max values for specific stations
            if math.isnan(com_max_id[0])==False:
                map_data_max=air_by_date_stat.loc[com_max_id[0],:]
            map_data_by_location.append(map_data_max)
    
    #dataframe for map creation
    map_data=pd.DataFrame(map_data_by_location,columns=air.columns)

    
    fig=go.Figure(
        data=px.scatter_mapbox(map_data, lat="Latitude", lon="Longitude",size='Value', color='Component_Name',zoom=6,
                        height=500, width=1600, mapbox_style="open-street-map")
        )
    #fig.update_layout(title_text="MAX POLLUTION",title_font_color='lightsalmon'

    return html.Div([
        dcc.Graph(
            id='id-map',
            figure=fig,  
            style={'width': '100%', 'height':'30%'},                  
        ),
        html.Div(style={'border':'2px darksalmon solid'})
        ,
        
    ])


def summary_table():
    #last day by default
    air_by_date=air[air['Day']==air['Day'].iloc[-1]]
    
    #create by columns
    list_sum=[]
    for name,id in zip(air_by_date['Component_Name'].unique(),air_by_date['Component_ID'].unique()):
        # unit
        unit=air_by_date.loc[air_by_date['Component_ID']==id,'Unit']
        unit=unit.iloc[0]
      
        #max value of component for single day in RS
        com_max=round(air_by_date.loc[air_by_date['Component_ID']==id,'Value'].max(),2)
        com_max_id=air_by_date.loc[air_by_date['Component_ID']==id,['Value']].idxmax()
        com_max_loc=air_by_date.loc[com_max_id[0],'Station_City']
        #unit==air_by_date['Unit'].loc[air_by_date['Component_ID']==id]
       
        #max value of component for single day in RS
        com_min=round(air_by_date.loc[air_by_date['Component_ID']==id,'Value'].min(),2)
        com_min_id=air_by_date.loc[air_by_date['Component_ID']==id,['Value']].idxmin()
        com_min_loc=air_by_date.loc[com_min_id[0],'Station_City']

        #average value of componet for single day in RS
        com_avg=round(air_by_date.loc[air_by_date['Component_ID']==id,'Value'].mean(),2)

        list_sum.append([name, unit ,com_max,com_max_loc,com_min,com_min_loc,com_avg])
        
    table_data=pd.DataFrame(list_sum,columns=['COMPONENT','Unit','MAX','MAX Location','MIN','MIN Location','AVG'])
    
    return html.Div([
            html.Div(style={'border':'2px darksalmon solid'}),

            html.H3('MAX AIR POLLUTION ',style={'color': 'lightsalmon','text-align':'center'}),

            dash_table.DataTable(
                id='id-table',
                columns=[{"name": i, "id": i} for i in table_data.columns],
                data=table_data.to_dict('records') ,
                style_cell={'textAlign':'center','font-size':'11px'},
                style_as_list_view=True,
                style_header={'fontWeight':'bold','font-size':'13px','color':'lightsalmon'},
                
                style_data_conditional=[
                {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                }, 
                ]
            )   
    ])



#grid 
grid = dui.Grid(num_rows=9, num_cols=3, grid_padding=0)

grid.add_element(col=1, row=1, width=3, height=1,element=header())
grid.add_element(col=1, row=2, width=1, height=4,element=data_picker())
grid.add_element(col=2, row=2, width=1, height=2,element=station_dropdown())
grid.add_element(col=3, row=2, width=1, height=2,element=component_multidropdown())
grid.add_element(col=1, row=3, width=1, height=4,element=summary_table())
grid.add_element(col=1, row=4, width=2, height=5,element=serbia_map())
grid.add_element(col=1, row=5, width=2, height=5,element=line_chart())



#main part 
app.layout = html.Div(
    grid.get_component(),
)


#Callbacks

#Update Station Dropdown based on Date
@app.callback(Output('id-station','options'),
              [Input('date-picker-single','date')
              ])

def update_station_dropdown(day):
    air_by_date=air[air['Day']==day]

    stations=[]
    for name,id in zip(air_by_date['Station_Name'].unique(),air_by_date['Station_ID'].unique()):
        stations.append({'label':name,'value':id})
    return stations

#Update Component Dropdown based on Date and Station_ID
@app.callback([Output('id-component','options'),Output('id-component','value')],
              [Input('date-picker-single','date'),Input('id-station','value')
               ])

def update_component_dropdown(day,station):
    air_by_date=air[air['Day']==day]
    air_by_date_stat=air_by_date[air_by_date['Station_ID']==station]
    
    pollutant=[]
    for name,id in zip(air_by_date_stat['Component_Name'].unique(),air_by_date_stat['Component_ID'].unique()):
        pollutant.append({'label':name,'value':id})

    values=[pollutant[i].get('value') for i in range(0,len(pollutant))]

    return pollutant, values


#Update Line Graph
@app.callback(Output('line-graph','figure'),
             [Input('date-picker-single','date'),
             Input('id-station','value'),
             Input('id-component','value')])

def update_line_chart(day, station, component):
    #filter data by date
    air_by_date=air[air['Day']==day]
    #filter by date and by station
    air_by_date_stat=air_by_date[air_by_date['Station_ID']==station]
    #component by hours

    traces=[]
    for id in component:
                data_by_comp=air_by_date_stat[air_by_date_stat['Component_ID']==id]
                name_of_com=str(data_by_comp['Component_Name'].unique())[2:-2]+' in '+ str(data_by_comp['Unit'].unique())[2:-2]
                traces.append(go.Scatter(
                        x =data_by_comp['Hour'],
                        y =data_by_comp['Value'],
                        mode = 'markers+lines',     
                        name = name_of_com))
    figure1={
            'data': traces,
            'layout': go.Layout(
                xaxis={'title':'HOURS'},
                yaxis={'title':'COMPONENT'},
                height= 500,
                #width=1500,
                margin={'l':100,'r':50,'t':60},
                font={'color':'lightsalmon'}
                )   
            }

    return figure1


#Update  Summry Table based on Date
@app.callback(Output('id-table','data'),
              [Input('date-picker-single','date')
              ])
        
def update_summary_table(day):
    #change by date
    air_by_date=air[air['Day']==day]
    
    #create by columns
    list_sum=[]
    for name,id in zip(air_by_date['Component_Name'].unique(),air_by_date['Component_ID'].unique()):
        # unit
        unit=air_by_date.loc[air_by_date['Component_ID']==id,'Unit']
        unit=unit.iloc[0]

        #max value of component for single day in RS
        com_max=round(air_by_date.loc[air_by_date['Component_ID']==id,'Value'].max(),2)
        com_max_id=air_by_date.loc[air_by_date['Component_ID']==id,['Value']].idxmax()
        com_max_loc=air_by_date.loc[com_max_id[0],'Station_City']

        #max value of component for single day in RS
        com_min=round(air_by_date.loc[air_by_date['Component_ID']==id,'Value'].min(),2)
        com_min_id=air_by_date.loc[air_by_date['Component_ID']==id,['Value']].idxmin()
        com_min_loc=air_by_date.loc[com_min_id[0],'Station_City']

        #average value of componet for single day in RS
        com_avg=round(air_by_date.loc[air_by_date['Component_ID']==id,'Value'].mean(),2)

        list_sum.append([name,unit,com_max,com_max_loc,com_min,com_min_loc,com_avg])
        
    table_data=pd.DataFrame(list_sum,columns=['COMPONENT','Unit','MAX','MAX Location','MIN','MIN Location','AVG'])

    return table_data.to_dict('records')


#Update Map based on date
@app.callback(Output('id-map','figure'),
              [Input('date-picker-single','date')
              ])

def update_serbia_map(day):
    data1=air[air['Day']==day]

    map_data_by_location=[]
    #separated by stations
    for station in data1['Station_ID'].unique():
        data2=data1[data1['Station_ID']==station] 

        #max value for specific station
        for name,id in zip(data2['Component_Name'].unique(),data2['Component_ID'].unique()):

            com_max=round(data2.loc[data2['Component_ID']==id,'Value'].max(),2) #max value for specific component in that place
            com_max_id=data2.loc[data2['Component_ID']==id,['Value']].idxmax() #position of max value

            if math.isnan(com_max_id[0])==False:
                map_data_max=data2.loc[com_max_id[0],:]
            map_data_by_location.append(map_data_max)

    map_data=pd.DataFrame(map_data_by_location,columns=air.columns)
    
    fig=go.Figure(
        data=px.scatter_mapbox(map_data, lat="Latitude", lon="Longitude",size='Value',color='Component_Name',
                        hover_name="Station_City",hover_data=["Station_City", "Value"],
                        zoom=6, height=500, width=1600, mapbox_style="open-street-map")
                )
    

    return fig



#Run
if __name__ == "__main__":
    app.run_server(debug=True)







