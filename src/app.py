from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import re
import numpy as np
import datetime as dt
from datetime import date

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
load_figure_template(["bootstrap", "sketchy", "cyborg", "minty", "superhero"])
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css],# theme's NAME muct be in caps
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server

# data

df_authored = pd.read_csv('http://atlas.media.uoa.gr/databank/0_csvs_for_per_day/2023-06-24/authored_2023-06-24.csv')
df_authors = pd.read_csv('http://atlas.media.uoa.gr/databank/0_csvs_for_per_day/2023-06-24/authors_2023-06-24.csv')
df_authors_min = pd.read_csv('http://atlas.media.uoa.gr/databank/0_csvs_for_per_day/2023-06-24/authors_min_2023-06-24.csv')

websitesL = ['cnn.gr', 'dikaiologitika.gr', 'efsyn.gr', 'enikos.gr', 'ertnews.gr', 'iefimerida.gr', 'in.gr', 'kathimerini.gr', 'lifo.gr',
             'naftemporiki.gr', 'news.gr', 'news247.gr', 'newsbeast.gr', 'newsbomb.gr', 'newsit.gr', 'protothema.gr', 'skai.gr', 'zougla.gr']

sectionsL = ['Αθλητισμός', 'Απόψεις / Θέματα', 'Αυτοκίνητο', 'Διεθνή', 'Ελλάδα / Κοινωνία', 'Οικονομία', 'Περιβάλλον',
             'Πολιτική', 'Τέχνες / Πολιτισμός', 'Τεχνολογία / Επιστήμη / Υγεία', 'Life', 'Uncategorized']

start_app_date = "24/06/2023"

# components

date_picker = dcc.DatePickerSingle(
    id="my-date-picker-single",
    min_date_allowed=date(2023, 1, 4),
    max_date_allowed=dt.date.today() - dt.timedelta(days=1),
    initial_visible_month=dt.date.today(),
    placeholder="Hμερομηνία",
    display_format='D/M/Y',
    className="pb-2 pt-2",
)

dropdown_site = dcc.Dropdown(
    id="site",
    options = ['όλα τα sites'] + websitesL,
    optionHeight=30,
    value='όλα τα sites',
    clearable=False
)

dropdown_section = dcc.Dropdown(
    id="section",
    options=['όλες οι κατηγορίες'] + sectionsL,
    optionHeight=30,
    value='όλες οι κατηγορίες',
    disabled=False,
    clearable=False
)

###################################################################################################

# layout
app.layout = dbc.Container([
    
    html.Div([
        dbc.Row( # *** DATE PICKER ***
            html.Div(
                date_picker,
                className="dbc", style={'text-align':'center'}, 
            ), 
        ),

        dbc.Row([ # *** SELECT SITE AND SECTION DROPDOWNS***
            dbc.Col(
                html.H5(
                    id = "selected-site",
                    className='text-end text-white mt-1'
                ), xl=3, lg=4, md=8, sm=12, xs=12
            ),
            dbc.Col(
                dropdown_site,
                xl=1, lg=2, md=4, sm=12, xs=12
            ),
            dbc.Col( 
                dropdown_section,
                xl=2, lg=2, md=5, sm=12, xs=12
            ),
            dbc.Col(
                html.H5(
                    id = "selected-date",
                    className='text-start text-white mt-1'
                ), xl=2, lg=4, md=8, sm=12, xs=12
            ),
        ], className="g-2 dbc", justify='center'
        ),
        
        dbc.Row( # *** HORIZONTAL LINE ***                 
            html.Hr(style={'borderWidth': "0.3vh"}, className='p-0 m-0 mt-2')#"color": "#FEC700"
        ),
    ], className="dbc sticky-top p-0 m-0", style={"background-color":"#585858"} #bg-white
    ),
        
    dbc.Row([ # ενυπόγραφα/ανυπόγραφα ROW
        html.H5("Ενυπόγραφα / Ανυπόγραφα άρθρα - Αρθρογράφοι", className='text-center text-black mt-2'),
        dbc.Col(
            dcc.Graph(id="authored-articles-pie", figure={},
                      config={'displayModeBar': False}
                     ), xl=4, lg=3, md=8, sm=12, xs=12
        ),
        dbc.Col(
            dcc.Graph(id="authored-words-maean-bar", figure={},
                      config={'displayModeBar': False}
                     ), xl=2, lg=5, md=4, sm=12, xs=12
        ),
        dbc.Col(
            dcc.Graph(id="authored-articles-bar", figure={}, #clear_on_unhover=True,
                      config={
                          #'staticPlot': False,     # True, False
                          'scrollZoom': False,      # True, False
                          'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                          'showTips': False,       # True, False
                          #'displayModeBar': 'hover',  # True, False, 'hover'
                          #'watermark': False,
                          #'modeBarButtonsToRemove': ['pan2d','select2d'],
                      },
                     ), xl=6, lg=4, md=12,sm=12, xs=12
        )
    ]),
    
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="authored-articles-per-site-bar", figure={},
                      config={'displayModeBar': 'hover', 'doubleClick': 'reset', 'watermark': False},  # display values: True, False, 'hover'
                     ), style= {'display': 'block'}, xl=7, lg=7, md=12,sm=12, xs=12
        ),
        dbc.Col(
            html.Div(
                dash_table.DataTable(df_authors_min.to_dict('records'),
                                     [{"name": i, "id": i} for i in df_authors_min.columns],
                                     page_size=8,
                                     sort_action='native',
                                     style_cell = {
                                         #'font-family': 'cursive',
                                         'font-size': '12px',
                                         #'text-align': 'center'
                                     },
                                     style_table={"overflowX": "auto"},
                                     filter_action="native",
                                     style_header={
                                            'backgroundColor': 'rgb(210, 210, 210)',
                                            'color': 'black',
                                            'fontWeight': 'bold'
                                     },
                                     css=[dict(selector= "p", rule= "margin: 0")],
                                     style_as_list_view=True,
                                    ), id="authors-all-min-datatable", className="dbc dbc-row-selectable"
            ),style= {'display': 'block'}, xl=5, lg=5, md=12,sm=12, xs=12, className="g-0 dbc justify='center' pe-4"
        )
    ]),
    
    dbc.Row(
        dbc.Col(
            html.Div(
                dash_table.DataTable(df_authors.to_dict('records'),
                                     [{'id': x, 'name': x, 'presentation': 'markdown'} if x == 'Τίτλος άρθρου' else {'id': x, 'name': x} for x in df_authors.columns],
                                     id="authors-table", 
                                     page_size=8,
                                     sort_action='native',
                                     style_cell = {
                                         #'font-family': 'cursive',
                                         'font-size': '12px',
                                         'text-align': 'right',
                                         #'margin-right': '4px',
                                     },
                                     style_cell_conditional=[
                                         {
                                         'if': {'column_id': 'x'},
                                         'textAlign': 'right'
                                         } for x in ['Αρθρογράφος', 'Τίτλος άρθρου']
                                     ],                                         
                                     style_table={"overflowX": "auto"},#, 'position': 'relative', 'top': '5vh', 'left': '5vw', 'width': '60vw'},
                                     filter_action="native",
                                     style_header={
                                         'backgroundColor': 'rgb(210, 210, 210)',
                                         'color': 'black',
                                         'fontWeight': 'bold'
                                     },
                                     css=[dict(selector= "p", rule= "margin: 0; text-align: right")],
                                     style_as_list_view=True,
                                     ), id="authors-datatable", className="dbc dbc-row-selectable"
            ), style= {'display': 'block'}, width=12, className="g-0 dbc ps-4 pe-4", #justify='center',
        ),
    ),     
    
], fluid=True, className="p-0")

###############################################################################################

# callbacks

@app.callback(# OPTIONS FOR SECTION DROPDOWN
    Output("section", "options"),
    Input("site", "value")
)
def update_section_dpdn_options(site):
    dff=df_authored[df_authored["Website"]==site]
    options = list(sorted(dff["Κατηγορία"].unique()))
    options = ["όλες οι κατηγορίες"] + options[:-1]
    return options

@app.callback( # VALUE FOR SECTION DRPDOWN VALUE
    Output("section", "value"),
    Input("site", "value"),
    State("section", "value")
)
def update_section_dpdn_value(site, s_section):
    dff=df_authored[df_authored["Website"]==site]
    options = list(sorted(dff["Κατηγορία"].unique()))
    if s_section in options:
        value = s_section
    else:
        value = "όλες οι κατηγορίες"
    return value

@callback( # TITLE START
    Output("selected-site", "children"),
    Input("site", "value")
)
def update_main_title_start(selected_site):
    if selected_site == "όλα τα sites":
        return "Ανάλυση αρθρογραφίας σε"
    else:
        return "Ανάλυση αρθρογραφίας στο"
    
@callback( # TITLE END
    Output("selected-date", "children"),
    Input("my-date-picker-single", "date")
)
def update_main_title_end(date):
    if date:
        date_str = str(date)
        selected_date=date_str[-2:] + "/" + date_str[5:7] + "/" + date_str[:4]
    else:
        selected_date=start_app_date
    return f"στις {selected_date}"

#******************** VISIBILITY OF ELEMENTS IN 2nd ROW *********************
@app.callback(
    Output("authored-articles-per-site-bar", "style"),
    Input("site", "value")
)
def show_hide_authored_container(site):
    if site == 'όλα τα sites':
        return {'display': 'block'}
    if site in websitesL:
        return {'display': 'none'}

@app.callback(
    Output("authors-all-min-datatable", "style"),
    Input("site", "value")
)
def show_hide_authors_all_min_container(site):
    if site == 'όλα τα sites':
        return {'display': 'block'}
    if site in websitesL:
        return {'display': 'none'} 

@app.callback(
    Output("authors-datatable", "style"),
    Input("site", "value")
)
def show_hide_authors_container(site):
    if site == 'όλα τα sites':
        return {'display': 'none'}
    if site in websitesL:
        return {'display': 'block'}
    
#********************* GRAPHS ********************************
# authored articles bar chart content
@app.callback(
    Output("authored-articles-bar", "figure"), 
    Input("site", "value"))
def generate_authored_bar(site):
    authored_colors={'Ενυπόγραφα':'#D93446', 'Ανυπόγραφα':'#585858'}
    dff=df_authored[(df_authored['Website']==site) & (df_authored['Κατηγορία']!="όλες οι κατηγορίες")]
    auth_bar_fig = px.bar(dff, x='Πλήθος άρθρων', y='Κατηγορία',
                          color='Είδος',
                          color_discrete_map=authored_colors,
                          orientation='h',
                          template="sketchy",
                          #labels={'section':'κατηγορία', 'count':'πλήθος άρθρων', 'authored':'είδος'},
                          height=350,
                          #showlegend=False,
                          #text_auto=True
                          #hover_data=["Είδος", "Πλήθος άρθρων"],
                          #title='ανά κατηγορία',
                          #custom_data=['Κατηγορία']
                         )
    auth_bar_fig.update_layout(showlegend=False, yaxis_title=None)
    auth_bar_fig.update_yaxes(ticksuffix = " ")
    return auth_bar_fig

@app.callback(
    Output("authored-words-maean-bar", "figure"),
    #Input(component_id='authored-articles-bar', component_property='hoverData'),   
    [Input("site", "value"),
    Input("section", "value")]
)
def generate_words_mean_bar(site, section):
    authored_colors={'Ενυπόγραφα':'#D93446', 'Ανυπόγραφα':'#585858'}
    dff = df_authored[df_authored['Website']==site]
    if section == "όλες οι κατηγορίες":
        #hov_section = hov_data['points'][0]['y']
        dff=dff[dff['Κατηγορία']=="όλες οι κατηγορίες"]
    else:
        dff=dff[dff['Κατηγορία']==section]
    auth_words_mean_fig = px.bar(dff, y='Μ.Ο. λέξεων', x='Είδος',
                                 hover_data=["Είδος", "Κατηγορία", "Μ.Ο. λέξεων"],
                                 color='Είδος', color_discrete_map=authored_colors,
                                 text_auto=True,
                                 template="sketchy", height=350)
    auth_words_mean_fig.update_layout(showlegend=False, xaxis_title=None) # title="Μ.Ο. λέξεων άρθρων",
    return auth_words_mean_fig         

#authored articles pie chart content
@app.callback(
    Output("authored-articles-pie", "figure"),
    #Input(component_id='authored-articles-bar', component_property='hoverData'),   
    [Input("site", "value"),
    Input("section", "value")]
)
def generate_authored_pie(site, section):
    authored_colors={'Ενυπόγραφα':'#D93446', 'Ανυπόγραφα':'#585858'}
    dff = df_authored[(df_authored['Website']==site) & (df_authored['Κατηγορία']!="όλες οι κατηγορίες")]
    if site == 'όλα τα sites':
        if section=="όλες οι κατηγορίες":
            text=dff['Πλήθος άρθρων'].sum().astype(str)
            title='<b>Όλα τα sites</b> | Όλες οι κατηγορίες'
        else:
            #print(f'hover data: {hov_data}')
            #print(hov_data['points'][0]['customdata'][0])
            text=dff['Πλήθος άρθρων'].sum().astype(str)
            dff=dff[dff['Κατηγορία']==section]
            title=f'<b>Όλα τα sites</b> | Κατηγορία: {section}'
    else:
        if section=="όλες οι κατηγορίες":
            text=dff['Πλήθος άρθρων'].sum().astype(str)
            title=f'<b>{site}</b> | Όλες οι κατηγορίες'
        else:
            #print(f'hover data: {hov_data}')
            #print(hov_data['points'][0]['customdata'][0])           
            dff=dff[dff['Κατηγορία']==section]
            text=dff['Πλήθος άρθρων'].sum().astype(str)
            title=f'<b>{site}</b> | Κατηγορία: {section}'
    auth_pie_fig = px.pie(dff, values="Πλήθος άρθρων", names="Είδος", hole=.35, color="Είδος", color_discrete_map=authored_colors)
    auth_pie_fig.update_traces(textposition='inside', textinfo='percent+label')
    auth_pie_fig.update_layout(
        template="sketchy", title = title, height=350,
        annotations=[dict(text=text, font_size=14, showarrow=False)]
    )
    return auth_pie_fig

# authored articles per site bar chart content
@app.callback(
    Output("authored-articles-per-site-bar", "figure"),
    #Input(component_id='authored-articles-bar', component_property='hoverData')#,   
    #Input("site", "value")
    Input("section", "value")
)
def generate_authored_per_site_bar_chart(section):
    authored_colors={'Ενυπόγραφα':'#D93446', 'Ανυπόγραφα':'#585858'}
    dff=df_authored[df_authored.Website != 'όλα τα sites']
    if section=='Όλες οι κατηγορίες':
        title='Όλες οι κατηγορίες'
        dff=dff[dff['Κατηγορία']=='όλες οι κατηγορίες']
        #auth_per_site_fig = px.bar(dff, y='Πλήθος άρθρων', x='Website', hover_data=["Είδος", "Κατηγορία", "Πλήθος άρθρων"], color='Είδος', color_discrete_map=authored_colors, template="sketchy", height=350) 
    else:
        #print(f'hover data: {hov_data}')
        # print(hov_data['points'][0]['customdata'][0])
        #hov_section = hov_data['points'][0]['y']
        dff=dff[dff['Κατηγορία']==section]
        title=f'Κατηγορία: {section}'
        #auth_per_site_fig = px.bar(dff, y='Πλήθος άρθρων', x='Website', hover_data=["Είδος", "Κατηγορία", "Πλήθος άρθρων"], color='Είδος', color_discrete_map=authored_colors, template="sketchy", height=350) 
    auth_per_site_fig = px.bar(dff, y='Πλήθος άρθρων', x='Website', hover_data=["Είδος", "Κατηγορία", "Πλήθος άρθρων"],
                               color='Είδος', color_discrete_map=authored_colors, template="sketchy", height=350, text_auto=True,)
    auth_per_site_fig.update_layout(showlegend=False, title=title)
    return auth_per_site_fig

# update the table
@app.callback(
    Output('authors-table', 'data'),
    Input('site', 'value'),
    Input('section', 'value')
)
def update_authors_datatable_output(site, section):
    if section == "όλες οι κατηγορίες":
        return df_authors[df_authors["Website"]==site].to_dict('records')
    return df_authors[(df_authors['Website']==site) & (df_authors['Κατηγορία']==section)].to_dict('records')

###############################################################################################

# run the app
if __name__ == '__main__':
    app.run_server()