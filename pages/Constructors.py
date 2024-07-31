import streamlit as st
import plotly.express as px
import pandas as pd

#Configuração inicial de pagina
st.set_page_config(page_title='F1 Reliability Dashboard',
                   page_icon='🏁',
                   layout='wide',
                   initial_sidebar_state='auto')

st.logo('https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/640px-F1.svg.png')
link = 'https://www.linkedin.com/in/andr%C3%A9s-michelangelli/'
st.sidebar.markdown(f"Made by [Andrés A. Michelangelli]({link})")

#Carregando o session state
f_races_results = st.session_state['main_df']

#Definindo critérios de seleção da coluna Status como mechanical issues
mechanical_issues = ['Engine', 'Transmission', 'Gearbox', 'Suspension', 'Hydraulics', 'Brakes', 'Differential', 
                       'Clutch', 'Driveshaft', 'Fuel pressure', 'Throttle', 'Steering', 'Exhaust', 'Fuel pump', 
                       'Track rod', 'Pneumatics', 'Engine fire', 'Fuel system', 'Oil line', 'Oil pressure', 'Drivetrain', 'Halfshaft', 
                       'Crankshaft', 'Wheel bearing', 'Vibrations', 'Oil pump', 'Injection', 'Distributor', 'Turbo', 
                       'CV joint', 'Water pump', 'Spark plugs', 'Fuel pipe', 'Oil pipe', 'Axle', 'Water pipe', 
                       'Supercharger', 'Engine misfire', 'Power Unit', 'Brake duct', 'Cooling system', 'Overheating',
                       'Oil leak', 'Mechanical', 'Radiator', 'Electrical', 'Driver Seat', 'Water Pressure', 'Water leak',
                       'Fire', 'Power loss', 'Launch control', 'Ignition', 'Battery', 'Alternator', 'ERS', 'Seat', 'Tyre', 'Puncture',
                       'Wheel', 'Tyre puncture'
                    ]

pattern = '|'.join(mechanical_issues) #definindo pattern e carater "|" para botar mais opções como se fosse "or" entre cada palabra

#Criando o slider para filtrar o dataframe principal por anos
st.sidebar.header("Select filters below:")
st.write(' ')
st.sidebar.divider()
st.sidebar.subheader('Years')

#Definindo a lista de anos disponíveis
years = sorted(f_races_results['year'].unique())

start_year, end_year = st.sidebar.select_slider(
    "Select a range of years: ",
    options=years,
    value=(years[-11], years[-1]))

#Definindo a tabela fato principal com os anos selecionados
races_results_filtered = f_races_results[(f_races_results['year'] >= start_year) & 
                                             (f_races_results['year'] <= end_year)]

#Definindo as opções disponiveis no inputbox de acordo com a tabela fato filtrada por anos
st.sidebar.divider()
team_1 = st.sidebar.selectbox('Select team: ',
                               races_results_filtered['name_y'].sort_values(ascending=True).unique(),
                               index= list(races_results_filtered['name_y'].sort_values(ascending=True).unique()).index('Red Bull')) 

team_2 = st.sidebar.selectbox('Compare with: ', races_results_filtered['name_y'].sort_values(ascending=True).unique(), index=None)

# ---- MAINPAGE ----  

st.title(':racing_car: F1 Constructors Reliability Comparison')
#st.markdown('##')

#Estabelecendo colunas e estrutura
container = st.container()
col1, col2= st.columns(2)
col3, col4 = st.columns(2)
col5 ,col6, col7, col8 = st.columns(4)
col9, col10 = st.columns(2)

# Criando o grafico de problemas mecanicos por ano com base na lista mechanical issues
with container:
    mechanical_issues_year_1 = races_results_filtered[['year', 'name_y', 'status']]
    mechanical_issues_year_2 = mechanical_issues_year_1[mechanical_issues_year_1['status'].str.contains(pattern, case=False, na=False)].groupby(['year', 'name_y'])['status'].count().reset_index()
    mechanical_issues_year_3 = mechanical_issues_year_2[(mechanical_issues_year_2['name_y'] == team_1) | (mechanical_issues_year_2['name_y'] == team_2)] #Considerando as duas opções selecionadas dentro da mesma tabela filtrada

    #OPCIONAL: Grafico de linhas
    fig1 = px.line(mechanical_issues_year_3,
                    x="year", y="status",
                    color='name_y',
                    color_discrete_map={team_1: 'blue', team_2: 'red'},
                    line_shape='spline')
    #st.plotly_chart(fig1)

    #Grafico de barras para comparar equipe 1 com equipe 2
    fig2 = px.bar(mechanical_issues_year_3,
                  x='year',
                  y='status',
                  color='name_y',
                  height=550,
                  barmode='group',
                  title='Mechanical issues per year',
                  labels={'year': 'Year', 'status': 'Mechanical issues', 'name_y': 'Team'},
                  color_discrete_map={team_1: 'blue', team_2: 'red'},
                  template='plotly_dark',
                  hover_name='name_y'
                )
    fig2.update_traces(texttemplate='%{y}',
                       textposition='outside',
                       textfont_color='white',
                       textfont_size=14)
    fig2.update_xaxes(tickmode='linear',  # Define o modo de tick como linear para mostrar todos os anos
                      tickangle=-45,      # Define o ângulo dos ticks para evitar sobreposição
                      dtick=1             # Define o intervalo entre ticks como 1 para mostrar cada ano
                    )
    fig2.update_layout(title_font_size=30,      # Tamanho da fonte do título do gráfico
                        xaxis_title_font_size=20,  # Tamanho da fonte do título do eixo X
                        yaxis_title_font_size=20,  # Tamanho da fonte do título do eixo Y
                        legend_title_font_size=20, # Tamanho da fonte do título da legenda
                        legend_font_size=18,      # Tamanho da fonte dos itens da legenda
                        xaxis_tickfont_size=18,   # Tamanho da fonte dos rótulos do eixo X
                        yaxis_tickfont_size=18    # Tamanho da fonte dos rótulos do eixo Y
                    )
    st.plotly_chart(fig2)

# ---- MAINPAGE: EQUIPE 1 ----
with col1:
    #Definindo e selecionando imagens de bandeira e carro por equipe
    team_flag_1 = (races_results_filtered[races_results_filtered['name_y'] == team_1]['flag_url_x']).iloc[0]
    team_country_1 = (races_results_filtered[races_results_filtered['name_y'] == team_1]['nationality_y']).iloc[0]
    st.image(f'{team_flag_1}', caption=team_country_1,width=70)
    car_1 = (races_results_filtered[races_results_filtered['name_y'] == team_1]['car_url']).iloc[0]
    if pd.notna(car_1) and car_1 != 'nan':
        st.image(car_1,width=400)
    else:
        st.caption(f'<h1 style="text-align: center;">Car image not available</h1>', unsafe_allow_html=True)
with col3:
    st.header(f'{team_1}', divider='blue')
    
with col5:
    #KPIs
    total_races_1 = races_results_filtered[['raceId','name_y']]
    total_races_1 = int(total_races_1[total_races_1['name_y'] == team_1].drop_duplicates().count().iloc[0])
    total_wins_1 = races_results_filtered[['raceId', 'name_y', 'positionOrder']]
    total_wins_1 = int(total_wins_1[(total_wins_1['name_y'] == team_1) & (total_wins_1['positionOrder'] == 1)].drop_duplicates().count().iloc[0])
    team_1_failures = int(mechanical_issues_year_2[mechanical_issues_year_2['name_y'] == team_1]['status'].sum())
    podiums_lost_1 = int(races_results_filtered[(races_results_filtered['grid'] <= 3) & (races_results_filtered['name_y'] == team_1) & (races_results_filtered['status'].isin(mechanical_issues))].count().iloc[0])
 
    st.subheader(f':checkered_flag: Races: {total_races_1}')
    st.subheader(f':trophy: Wins: {total_wins_1}')
    st.subheader(f':wrench: Mechanical issues: {team_1_failures}')
    st.subheader(f':red_circle: Podiums lost: {podiums_lost_1}')
with col6:
    #KPIs
    total_seasons_1 = races_results_filtered[['year','name_y']]
    total_seasons_1 = int(total_seasons_1[total_seasons_1['name_y'] == team_1].drop_duplicates().count().iloc[0])
    total_podiums_1 = races_results_filtered[['raceId', 'name_y', 'positionOrder']]
    total_podiums_1 = int(total_podiums_1[(total_podiums_1['name_y'] == team_1) & (total_podiums_1['positionOrder'] <= 3)].drop_duplicates().count().iloc[0])
    wins_lost_1 = int(races_results_filtered[(races_results_filtered['grid'] == 1) & (races_results_filtered['name_y'] == team_1) & (races_results_filtered['status'].isin(mechanical_issues))].count().iloc[0])
    mechanical_issues_year_2 = mechanical_issues_year_1[mechanical_issues_year_1['status'].str.contains(pattern, case=False, na=False)].groupby(['year', 'name_y'])['status'].count().reset_index()
    worst_season_1 = mechanical_issues_year_2[(mechanical_issues_year_2['name_y'] == team_1)].sort_values(by='status',ascending=False).iloc[0,0]

    st.subheader(f':earth_americas: Seasons: {total_seasons_1}')
    st.subheader(f':medal: Podiums: {total_podiums_1}')
    st.subheader(f':x: Victories lost: {wins_lost_1}')
    st.subheader(f':black_circle: Worst season: {worst_season_1}')
with col9:
    #Calculando a confiabilidade da equipe
    races_finished_1 = races_results_filtered[['year', 'name_y', 'status']]
    #Filtrando o df com status que contem Finished ou o simbolo '+'
    races_finished_1 = races_finished_1[(races_finished_1['status'].str.contains(r'Finished|\+', case=False, na=False)) & (races_finished_1['name_y'] == team_1)].groupby(['year', 'name_y'])['status'].count().reset_index()
    races_finished_1 = races_finished_1['status'].sum()
    reliability_1 = round((races_finished_1 *100 / (team_1_failures + races_finished_1)), 1)

    st.markdown(f'<h1 style="text-align: center;">Reliability: {reliability_1}%</h1>', unsafe_allow_html=True)


# ---- MAINPAGE: EQUIPE 2 ----
with col2:
    if team_2:
        #Definindo e selecionando imagens de bandeira e carro por equipe
        team_flag_2 = (races_results_filtered[races_results_filtered['name_y'] == team_2]['flag_url_x']).iloc[0]
        team_country_2 = (races_results_filtered[races_results_filtered['name_y'] == team_2]['nationality_y']).iloc[0]
        st.image(f'{team_flag_2}', caption=team_country_2, width=70)
        car_2 = (races_results_filtered[races_results_filtered['name_y'] == team_2]['car_url']).iloc[0]
        if pd.notna(car_2) and car_1 != 'nan':
            st.image(car_2, width=400)
        else:
            st.caption(f'<h1 style="text-align: center;">Car image not available</h1>', unsafe_allow_html=True)
with col4:
    if team_2:
        st.header(f'{team_2}', divider='red')
    else:
        st.markdown(f'<h1 style="text-align: center;">Select another team to compare</h1>', unsafe_allow_html=True)
with col7:
    if team_2:
        #KPIs
        total_races_2 = races_results_filtered[['raceId','name_y']]
        total_races_2 = int(total_races_2[total_races_2['name_y'] == team_2].drop_duplicates().count().iloc[0])
        total_wins_2 = races_results_filtered[['raceId', 'name_y', 'positionOrder']]
        total_wins_2 = int(total_wins_2[(total_wins_2['name_y'] == team_2) & (total_wins_2['positionOrder'] == 1)].drop_duplicates().count().iloc[0])
        team_2_failures = int(mechanical_issues_year_2[mechanical_issues_year_2['name_y'] == team_2]['status'].sum())
        podiums_lost_2 = int(races_results_filtered[(races_results_filtered['grid'] <= 3) & (races_results_filtered['name_y'] == team_2) & (races_results_filtered['status'].isin(mechanical_issues))].count().iloc[0])
    
        st.subheader(f':checkered_flag: Races: {total_races_2}')
        st.subheader(f':trophy: Wins: {total_wins_2}')
        st.subheader(f':wrench: Mechanical issues: {team_2_failures}')
        st.subheader(f':red_circle: Podiums lost: {podiums_lost_2}')
    else:
        st.write(" ")
with col8:
    if team_2:
    #KPIs
        total_seasons_2 = races_results_filtered[['year','name_y']]
        total_seasons_2 = int(total_seasons_2[total_seasons_2['name_y'] == team_2].drop_duplicates().count().iloc[0])
        total_podiums_2 = races_results_filtered[['raceId', 'name_y', 'positionOrder']]
        total_podiums_2 = int(total_podiums_2[(total_podiums_2['name_y'] == team_2) & (total_podiums_2['positionOrder'] <= 3)].drop_duplicates().count().iloc[0])
        wins_lost_2 = int(races_results_filtered[(races_results_filtered['grid'] == 1) & (races_results_filtered['name_y'] == team_2) & (races_results_filtered['status'].isin(mechanical_issues))].count().iloc[0])
        mechanical_issues_year_2 = mechanical_issues_year_1[mechanical_issues_year_1['status'].str.contains(pattern, case=False, na=False)].groupby(['year', 'name_y'])['status'].count().reset_index()
        worst_season_2 = mechanical_issues_year_2[(mechanical_issues_year_2['name_y'] == team_2)].sort_values(by='status',ascending=False).iloc[0,0]

        st.subheader(f':earth_americas: Seasons: {total_seasons_2}')
        st.subheader(f':medal: Podiums: {total_podiums_2}')
        st.subheader(f':x: Victories lost: {wins_lost_2}')
        st.subheader(f':black_circle: Worst season: {worst_season_2}')
    else:
        st.write(" ")
with col10:
    if team_2:
        #Calculando a confiabilidade da equipe
        races_finished_2 = races_results_filtered[['year', 'name_y', 'status']]
        #Filtrando o df com status que contem Finished ou o simbolo '+'
        races_finished_2 = races_finished_2[(races_finished_2['status'].str.contains(r'Finished|\+', case=False, na=False)) & (races_finished_2['name_y'] == team_2)].groupby(['year', 'name_y'])['status'].count().reset_index()
        races_finished_2 = races_finished_2['status'].sum()
        reliability_2 = round((races_finished_2 *100 / (team_2_failures + races_finished_2)), 1)

        st.markdown(f'<h1 style="text-align: center;">Reliability: {reliability_2}%</h1>', unsafe_allow_html=True)

    else:
        st.write(" ")

# ---- HIDE STREAMLIT STYLE -----
#Codigo para ocultar marca d'agua e botões do streamlit
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
