
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import geopandas as gpd
import plotly.graph_objects as go
from dash_core_components import Checklist, Dropdown
import base64

# Load GeoJSON file using GeoPandas for admin boundaries
admin_gdf = gpd.read_file('D:/ABM/Dashboard_input/Mapshaper/Admin_boundaries.geojson')

# Convert MultiPolygon to Polygon
admin_gdf['geometry'] = admin_gdf['geometry'].apply(lambda geom: geom if geom.is_empty or not geom.has_z else geom[0])

# Load GeoJSON file for Atolls
atoll_gdf = gpd.read_file('D:\\ABM\\Dashboard_input\\Mapshaper\\Atolls.geojson')

# Convert MultiPolygon to Polygon
atoll_gdf['geometry'] = atoll_gdf['geometry'].apply(lambda geom: geom if geom.is_empty or not geom.has_z else geom[0])

# Check if 'Atoll' column is present, if not, replace it with the appropriate column
atoll_column = 'Atoll' if 'Atoll' in atoll_gdf.columns else 'your_alternative_column'

# Load and encode logo images
coastmove_logo_path = 'D:/ABM/photo/coastmove_logo.png'
marshall_islands_logo_path = 'D:/ABM/photo/Marshall_Islands_logo.png'
deltares_logo_path = 'D:/ABM/photo/Deltares_logo.png'  # Added Deltares logo path
vrije_ams_logo_path = 'D:/ABM/photo/Vrije_Ams_logo.png'  # Added Vrije Ams logo path

with open(coastmove_logo_path, "rb") as image_file:
    coastmove_logo_encoded = base64.b64encode(image_file.read()).decode('utf-8')

with open(marshall_islands_logo_path, "rb") as image_file:
    marshall_islands_logo_encoded = base64.b64encode(image_file.read()).decode('utf-8')

with open(deltares_logo_path, "rb") as image_file:  # Read and encode Deltares logo
    deltares_logo_encoded = base64.b64encode(image_file.read()).decode('utf-8')

with open(vrije_ams_logo_path, "rb") as image_file:  # Read and encode Vrije Ams logo
    vrije_ams_logo_encoded = base64.b64encode(image_file.read()).decode('utf-8')

# Initialize the Dash app
app = dash.Dash(__name__)

server=app.server

# Banner with logos on the top
top_banner = html.Div(
    children=[
        html.Img(src=f'data:image/png;base64,{coastmove_logo_encoded}', style={'width': '170px', 'height': '80px'}),
        html.Img(src=f'data:image/png;base64,{marshall_islands_logo_encoded}', style={'height': '80px'}),
        html.H1("Coastal Migration & Adaptation of The Marshall Islands", style={'color': 'black', 'margin': '20px 0', 'padding': '20px', 'background-color': '#95C9E8', 'font-size': '15px'}),
    ],
    style={'width': '100%', 'text-align': 'center', 'display': 'flex', 'justify-content': 'flex-start', 'align-items': 'center', 'background-color': '#95C9E8', 'position': 'fixed', 'top': '0', 'left': '0', 'right': '0', 'z-index': '1000'}
)

# Main content
# Main content
main_content = html.Div(
    children=[
        # Sidebar
        html.Div(
            children=[
                html.H2("Demographics"),
                # Dropdown for selecting demographic variable in the sidebar
                dcc.Dropdown(
                    id='demographic-selector',
                    options=[{'label': col, 'value': col} for col in admin_gdf.columns if col != 'geometry'],
                    value='Population',  # Default demographic variable
                    multi=False,
                ),

                # Checklist for toggling the Atoll layer in the sidebar
                Checklist(
                    id='atoll-layer-toggle',
                    options=[{'label': 'Show Atoll Layer', 'value': 'show_atoll_layer'}],
                    value=[],  # Default is off
                ),

                # Dropdown for selecting Atoll in the sidebar
                Dropdown(
                    id='atoll-selector',
                    options=[],  # Options will be populated dynamically
                    multi=True,
                    placeholder='Select Atoll',
                ),

                # Textbox below the Select Atoll dropdown with smaller font size
                html.Div(
                    children=[
                        dcc.Markdown("The effects of climate change have become an increasingly concerning issue for many small island developing states (SIDS) globally.,"
                                     , style={'color': 'black', 'fontSize': '12px'}),
                    ],
                    style={'margin': '5px'}  # Adjusted margin
                ),
            ],
            style={'width': '20%', 'float': 'left', 'height': '100vh', 'position': 'fixed', 'left': '0', 'top': '80px', 'bottom': '50px', 'overflow-y': 'auto'}
        ),

        # Map
        html.Div(
            children=[
                # Graph component for the choropleth map
                dcc.Graph(
                    id='choropleth-map',
                ),
            ],
            style={'width': '80%', 'float': 'right', 'position': 'fixed', 'top': '80px', 'right': '0', 'bottom': '50px', 'left': '20%'}  # Set position to 'fixed'
        )
    ],
    style={'width': '100%', 'display': 'flex'}  # Set the width of the parent div to 100% and use display: flex
)


# Blue banner at the bottom
bottom_banner = html.Div(
    children=[
        # Logos on the bottom left
        html.Div(
            children=[
                html.Img(src=f'data:image/png;base64,{deltares_logo_encoded}', style={'width': '100px', 'height': '50px'}),
                html.Img(src=f'data:image/png;base64,{vrije_ams_logo_encoded}', style={'width': '100px', 'height': '50px'}),
            ],
            style={'width': '100%', 'text-align': 'center', 'display': 'flex', 'justify-content': 'flex-start', 'align-items': 'center', 'background-color': '#95C9E8', 'margin': '0', 'padding': '0'}  # Adjusted margin and padding
        ),
    ],
    style={'width': '100%', 'text-align': 'center', 'display': 'flex', 'justify-content': 'flex-end', 'align-items': 'center', 'background-color': '#95C9E8', 'position': 'fixed', 'bottom': '0', 'left': '0', 'right': '0', 'z-index': '1000'}
)

# Combine the top banner, main content, and bottom banner in the app layout
app.layout = html.Div([top_banner, main_content, bottom_banner])

# Callback to update dropdown options based on Atoll layer toggle
@app.callback(
    Output('atoll-selector', 'options'),
    [Input('atoll-layer-toggle', 'value')]
)
def update_atoll_dropdown_options(checklist_values):
    show_atoll_layer = 'show_atoll_layer' in checklist_values

    # Filter Atoll GeoDataFrame based on selected Atolls
    atoll_gdf_filtered = atoll_gdf if show_atoll_layer else atoll_gdf[atoll_gdf[atoll_column].notnull()]

    # Create options for the Atoll dropdown
    atoll_dropdown_options = [{'label': atoll, 'value': atoll} for atoll in atoll_gdf_filtered[atoll_column].unique() if atoll]  # Filter out None values

    return atoll_dropdown_options

# Callback to update choropleth map based on dropdown and checkbox selection
@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('demographic-selector', 'value'),
     Input('atoll-layer-toggle', 'value'),
     Input('atoll-selector', 'value')]
)
def update_choropleth(selected_demographic, checklist_values, selected_atolls):
    show_atoll_layer = 'show_atoll_layer' in checklist_values

    # Filter Atoll GeoDataFrame based on selected Atolls
    atoll_gdf_filtered = atoll_gdf[atoll_gdf[atoll_column].isin(selected_atolls)] if selected_atolls else atoll_gdf

    # Filter Admin GeoDataFrame based on selected Atolls
    admin_gdf_filtered = admin_gdf[admin_gdf['Atoll'].isin(selected_atolls)] if selected_atolls else admin_gdf

    # Filter out None values from Admin Boundary Dropdown options
    admin_dropdown_options = [{'label': admin, 'value': admin} for admin in admin_gdf_filtered['Atoll'].unique() if admin]

    # Create a scattermapbox plot with Choropleth overlay
    fig = go.Figure()

    # Scattermapbox for the background
    if not show_atoll_layer:
        fig.add_trace(go.Scattermapbox(
            lat=[],
            lon=[],
            mode='markers',
            marker=dict(size=1),
            showlegend=False,
            hoverinfo='none',  # Disable hover info for background points
        ))

    # Choropleth overlay for admin boundaries (if not showing Atoll layer)
    if not show_atoll_layer:
        admin_hover_text = admin_gdf_filtered.apply(
            lambda row: f"Atoll: {row['Atoll']}<br>Population: {row['Population']}<br>Income: {row['Income']}<br>Floodplain: {row['Floodplain']}<br>Risk_Perce: {row['Risk_Perce']}<br>Coast_P: {row['Coast_P']}<br>ID: {row['ID']}",
            axis=1
        ) if 'Atoll' in admin_gdf_filtered.columns else None
        fig.add_trace(go.Choroplethmapbox(
            geojson=admin_gdf_filtered.__geo_interface__,
            locations=admin_gdf_filtered.index,
            featureidkey="id",
            z=admin_gdf_filtered[selected_demographic],
            colorscale="YlOrRd",
            colorbar=dict(
                title=selected_demographic,
                x=0.93,       # Adjusted x-axis value
                y=0.5,
                yanchor='middle',
                xanchor='left',
                thickness=5,  # Adjusted thickness
                len=0.4,      # Adjusted length
            ),
            hoverinfo='location+z+text',
            text=admin_hover_text,
            showlegend=False,
        ))

    # Choropleth overlay for Atolls (if showing Atoll layer)
    if show_atoll_layer:
        atoll_hover_text = atoll_gdf_filtered.apply(
            lambda row: f"Atoll: {row['Atoll']}<br>Population: {row['Population']}<br>Income: {row['Income']}<br>Floodplain: {row['Floodplain']}<br>Risk_Perce: {row['Risk_Perce']}<br>Coast_P: {row['Coast_P']}<br>ID: {row['ID']}",
            axis=1
        ) if atoll_column in atoll_gdf_filtered.columns else None
        fig.add_trace(go.Choroplethmapbox(
            geojson=atoll_gdf_filtered.__geo_interface__,
            locations=atoll_gdf_filtered.index,
            featureidkey="id",
            z=atoll_gdf_filtered[selected_demographic],
            colorscale="YlOrRd",
            colorbar=dict(
                title=selected_demographic,
                x=0.93,       # Adjusted x-axis value
                y=0.5,
                yanchor='middle',
                xanchor='left',
                thickness=5,  # Adjusted thickness
                len=0.4,      # Adjusted length
            ),
            hoverinfo='location+z+text',
            text=atoll_hover_text,
        ))

    # Layout settings with larger initial zoom level
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": 7, "lon": 171},
        mapbox_zoom=4,
        width=800,
        height=600,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)







