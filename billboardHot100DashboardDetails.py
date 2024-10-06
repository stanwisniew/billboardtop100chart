import dash
import plotly.express as px
import pandas as pd
from dash import html
from dash import dcc
from dash.dependencies import Input, Output


#data pd
#---------------------------------

df=pd.read_csv("/home/stanislaw/Dane/DataAnalysisSets/hot-100-current.csv")


# Assuming df is already defined and contains a 'chart_week' column in the YYYY-MM-DD format
df['Year'] = pd.to_datetime(df['chart_week']).dt.year  # Create Year column

# Now you can proceed with your filtering and aggregation
no1_performers = df[df["peak_pos"] == 1].groupby("performer").agg(
    number_of_no1_hits=('peak_pos', 'size'),
    max_weeks_on_chart=('wks_on_chart', 'max'), 
    Year=('Year', 'first')  # Retrieve the first year for that performer
).reset_index()

#interactive with Dash

app = dash.Dash("__name__")

unique_years = sorted(no1_performers.Year.unique(), reverse=True)

app.layout = html.Div([
    html.H2("Billboard Hot 100"),
        dcc.Dropdown(id='year-choice',
                 options=[{'label': str(x), 'value': str(x)} for x in unique_years],
                value=str(unique_years[0])   # Default value for the dropdown
                 ),
    dcc.Graph(id="billboard"),
    dcc.Graph(id="details-graph") 
])

@app.callback(
    Output(component_id='billboard', component_property='figure'),
    Input(component_id='year-choice', component_property="value"),
)
def interactive_graph (value_choice):
    print(value_choice)
    dff = no1_performers[no1_performers.Year == int(value_choice)]
    fig = px.bar(data_frame=dff, x='performer', y='number_of_no1_hits', 
                 title=f"Number of weeks spent on top spot by performer in {value_choice}",
                 labels={"number_of_no1_hits": "", "performer": ""})
    return fig

 #Callback for detailed view
 
 
@app.callback(
    Output(component_id='details-graph', component_property='figure'),
    Input(component_id='billboard', component_property='clickData')
)
def update_details_graph(clickData):
    if clickData is None:
        return px.scatter(title="Click on a performer for details")  # Default figure

    performer_name = clickData['points'][0]['x']
    
    # Get details for the selected performer
    performer_details = df[df['performer'] == performer_name]
    
    # Use max to get the highest number of weeks on chart for each song
    performer_details_max = performer_details.groupby('title', as_index=False).agg(
        max_weeks_on_chart=('wks_on_chart', 'max'),  # Get the maximum weeks on chart for each song
        peak_pos=('peak_pos', 'max')  # Get the maximum peak position for each song
    )
    print(performer_details_max)


    # Create a detailed bar chart
    details_fig = px.bar(
        performer_details_max, 
        x='title', 
        y='max_weeks_on_chart', 
        title=f"Details for {performer_name}",
        labels={
            "max_weeks_on_chart": "Number of Weeks on Charts",  # Change display name for the y-axis
            "title": "Song Title",  # Change display name for the x-axis if needed
            "wks_on_chart": "Weeks on Chart",
            "peak_pos": "Peaked on number: ",
        },
        color='peak_pos',
        color_continuous_scale=px.colors.sequential.Viridis,  # Change the color scale here
        color_discrete_sequence=["red", "orange", "yellow", "green", "blue", "purple"],  # Custom colors
        hover_name='title',  # Specify the name to be displayed in hover
        hover_data={
            'max_weeks_on_chart': False,  # Disable default display for max_weeks_on_chart
            'peak_pos': True  # Keep peak_pos in hover
        }
    )
    details_fig.update_traces(hovertemplate='<b>Song Title</b>: %{hovertext}<br>' +
                                            '<b>Weeks on Chart</b>: %{y}<br>' +
                                            '<b>Peaked on number</b>: %{customdata}<extra></extra>',
                               hovertext=performer_details_max['title'],
                               customdata=performer_details_max['peak_pos'])  # Add peak_pos as custom data

    
    return details_fig  # Return the details figure


if __name__ == "__main__":
    app.run_server(port=8000, debug=True)