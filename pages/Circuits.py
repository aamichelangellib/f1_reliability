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
    value=(years[-21], years[-1]))

#Definindo a tabela fato principal com os anos selecionados e condicionais
races_results_filtered = f_races_results[(f_races_results['year'] >= start_year) & 
                                             (f_races_results['year'] <= end_year)]

#Definindo opções de paises e circuito, dependendo da tabela fato filtrada pelos anos
st.sidebar.divider()
country = st.sidebar.selectbox('Select country: ',
                               races_results_filtered['country_y'].sort_values(ascending=True).unique(),
                               index=None)

circuit = st.sidebar.selectbox('Select circuit: ',
                                races_results_filtered[races_results_filtered['country_y'] == country]['circuit_name'].sort_values(ascending=True).unique(),
                                index=None)

if country and not circuit:
    races_results_filtered = f_races_results[(f_races_results['year'] >= start_year) & 
                                             (f_races_results['year'] <= end_year) & 
                                             (f_races_results['country_y'] == country)]
elif country and circuit:
    races_results_filtered = f_races_results[(f_races_results['year'] >= start_year) & 
                                            (f_races_results['year'] <= end_year) & 
                                            (f_races_results['country_y'] == country) & 
                                            (f_races_results['circuit_name'] == circuit)]

#Definindo opções multiselect de falhas mecânicas que irão alterar somente o mapa do mundo, o dataframe e histograma
options = st.sidebar.multiselect(
                            "Select mechanical issues: ",
                            races_results_filtered[races_results_filtered['status'].str.contains(pattern, case=False, na=False)]['status'].sort_values(ascending=True).unique()
                            )

# ---- MAINPAGE ----  

st.title(':earth_americas: F1 Circuits Reliability Analysis Dashboard')
#st.markdown('##') #opcional

#Configurando layout com colunas e containers
col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
col4, col5 = st.columns(2)
col6, col7 = st.columns([0.72, 0.28])

#Mostrando bandeira, nome do pais e nome do circuito e layout
with col1: #bandeira
    if country:
        country_flag = races_results_filtered['flag_url_y'].iloc[0]
        st.image(f'{country_flag}', caption=country,width=70)
    #else: #Opcional
        #st.caption(f'<h1 style="text-align: center;">Select country and circuit</h1>', unsafe_allow_html=True)
with col2: #Nome do circuito
    if circuit:
            st.header(f'{circuit}', divider='blue')
with col3: #Layout do circuito
        if circuit:
            circuit_layout = races_results_filtered['picture_url'].iloc[0]
            if pd.notna(circuit_layout) and circuit_layout != 'nan':
                st.image(circuit_layout,width=180)

#Configurando Mapa Mundi mostrando os circuitos utilizando plotly 
with col4:
    circuits_map = races_results_filtered[['circuit_name', 'country_y','lat', 'lng', 'status']]

    if options: #Se a opção options estive ativa, filtrar o df pelas opções multiselect selecionadas pelo usuário
        circuits_map = circuits_map[circuits_map['status'].isin(options)]
    #Groupby para contar todos os valores status que são considerados como falhas mecânicas
    circuits_map = circuits_map[circuits_map['status'].str.contains(pattern, case=False, na=False)].groupby(['circuit_name', 'country_y','lat', 'lng'])['status'].count().reset_index()

    # Calcula a latitude e longitude médias
    mean_lat = circuits_map['lat'].mean()  
    mean_lng = circuits_map['lng'].mean()

    mean_lat = circuits_map['lat'].mean()  
    mean_lng = circuits_map['lng'].mean()

    # Calcula a diferença máxima e mínima de latitude e longitude para ajustar o zoom
    lat_diff = circuits_map['lat'].max() - circuits_map['lat'].min()
    lng_diff = circuits_map['lng'].max() - circuits_map['lng'].min()
    
    map_zoom = 0.2  # Zoom padrão
    if country and lat_diff > 0 and lng_diff > 0:
        map_zoom = max(1, 7 - int(max(lat_diff, lng_diff)))  # Ajustar o zoom dinamicamente

    #mapa em dark ou light mode
    on = st.toggle("Map on dark mode")

    if on:
        map_mode = 'carto-darkmatter'
    else:
        map_mode = 'open-street-map'

    # Cria um mapa de dispersão com Plotly Express
    fig1 = px.scatter_mapbox(
                        circuits_map,
                        lat='lat',
                        lon='lng',
                        hover_name='circuit_name',
                        hover_data={'country_y': True, 'status': True},
                        color='status',
                        color_continuous_scale='Plasma',
                        size='status',
                        size_max=20,
                        zoom=map_zoom,
                        title=f'Mechanical issues by location {options}'
    )


    # Atualiza o layout do mapa para centralizar na média dos pontos
    fig1.update_layout(
                    mapbox_style=map_mode, #para opção light selecionar open-street-map, opção dark: carto-darkmatter
                    mapbox_center={'lat': mean_lat, 'lon': mean_lng},
                    mapbox_zoom=map_zoom  # Ajuste o zoom conforme necessário
    )

    st.plotly_chart(fig1)

#Configurando o grafico de quantidade de falhas mecânicas em função do tempo
with col5:
    #Definindo e Separando os graficos em cada aba (3)
    tabs = st.tabs(['Mechanical issues per year', 'Most frequent mechanical issues', 'Less reliable constructors' ])

    with tabs[0]:
        mechanical_issues_per_year = races_results_filtered[['year', 'status']]

        if options:
            mechanical_issues_per_year = races_results_filtered[races_results_filtered['status'].isin(options)]

        mechanical_issues_per_year = mechanical_issues_per_year[mechanical_issues_per_year['status'].str.contains(pattern, case=False, na=False)].groupby('year')['status'].count().reset_index()
        
        year_diff = end_year - start_year

        if year_diff <= 40: #Configurando o step dinâmico en função do periodo de anos selecionado
            dtick = 1
        else:
            dtick = 2

        fig4 = px.bar(mechanical_issues_per_year, x='year', y='status',
                    labels={'x':'year', 'y':'mechanical issues'},
                    title=f'Mechanical Issues per Year {options}',
                    height=450)
        fig4.update_traces(texttemplate='%{y}',
                        textposition='outside',
                        textfont_color='white',
                        textfont_size=12)
        fig4.update_xaxes(tickmode='linear',  # Define o modo de tick como linear para mostrar todos os anos
                        tickangle=-45,      # Define o ângulo dos ticks para evitar sobreposição
                        dtick=dtick             # Define o intervalo entre ticks como 1 para mostrar cada ano
                        )

        st.plotly_chart(fig4)
    #Configurando o grafico de falhas mecânicas mais frequentes (top 10)
    with tabs[1]:

        mechanical_issues_1 = races_results_filtered[['status']].copy() #Sempre que selecionar apenas uma coluna para fazer groupby, utilizar metodo copy()
        #groupby com metodo size() que permite contar o número total de elementos em cada grupo, incluindo valores nulos.
        mechanical_issues_1 = mechanical_issues_1[mechanical_issues_1['status'].str.contains(pattern, case=False, na=False)].groupby('status').size().reset_index(name='status_count')
        mechanical_issues_1 = mechanical_issues_1.sort_values(by='status_count', ascending=False).head(10)
        fig2 = px.bar(mechanical_issues_1, x='status_count', y='status', orientation='h',
                    labels={'status_count': 'quantity', 'status': 'mechanical issues'},
                    title='Most frequent mechanical issues',
                    text='status_count', height=450)

        fig2.update_yaxes(categoryorder='total ascending')
        fig2.update_traces(textposition='outside', textfont_color='white')

        st.plotly_chart(fig2)
    #Mostrando o gráfico das equipes com mais falhas mecânicas Top 10
    with tabs[2]:
        constructors_mechanical_issues = races_results_filtered[['name_y', 'status']]

        if options:
            constructors_mechanical_issues = races_results_filtered[races_results_filtered['status'].isin(options)]

        constructors_mechanical_issues  = constructors_mechanical_issues [constructors_mechanical_issues ['status'].str.contains(pattern, case=False, na=False)].groupby('name_y')['status'].count().reset_index()
        constructors_mechanical_issues  = constructors_mechanical_issues .sort_values(by='status', ascending=False).head(10)
        fig5 = px.bar(constructors_mechanical_issues, x='status', y='name_y', orientation='h',
                    labels={'status': 'mechanical issues', 'name_y': 'constructor'},
                    title=f'Less reliable constructors (top 10) {options}',
                    text='status', height=450)
        
        fig5.update_yaxes(categoryorder='total ascending')
        fig5.update_traces(textposition='outside', textfont_color='white')

        st.plotly_chart(fig5)

#Configurando o Dataframe 
with col6:  
    #Definindo condicional para alterar ou não o Dataframe em função do multiselect
    if options:
        df_filtered = races_results_filtered[races_results_filtered['status'].isin(options)]
    else:
        df_filtered = races_results_filtered

    #Construindo as tabelas das medidas por separado para depois mezclar (merge)
    #Tabela principal
    df_filtered = df_filtered[['circuit_name','flag_url_y', 'country_y', 'location_y', 'status']]
    df_filtered = df_filtered[df_filtered['status'].str.contains(pattern, case=False, na=False)].groupby(['circuit_name', 'flag_url_y', 'country_y', 'location_y'])['status'].count().reset_index().sort_values(by='status', ascending=False)

    #Calculando a quantidade de corridas por circuito
    races_per_circuit = races_results_filtered[['circuit_name', 'raceId']].drop_duplicates()
    races_per_circuit = races_per_circuit.groupby('circuit_name')['raceId'].count().reset_index().sort_values(by='raceId', ascending=False)

    #Calculando o promedio de falhas mecânicas por circuito
    mean_per_circuit = races_results_filtered[['raceId','circuit_name', 'status']]
    mean_per_circuit = mean_per_circuit[mean_per_circuit['status'].str.contains(pattern, case=False, na=False)].groupby(['raceId','circuit_name'])['status'].count().reset_index()
    mean_per_circuit = mean_per_circuit[['circuit_name', 'status']]
    mean_per_circuit = mean_per_circuit.groupby(['circuit_name'])['status'].mean().reset_index().sort_values(by='status', ascending=False)

    #Calculando e selecionando as falhas mecânicas mais frequentes por circuito
    frequent_failures = races_results_filtered[['circuit_name', 'status']].copy()
    frequent_failures = frequent_failures[frequent_failures['status'].str.contains(pattern, case=False, na=False)]
    # Agrupando por circuito e status e contando a quantidade de ocorrências de cada status
    frequent_failures = frequent_failures.groupby(['circuit_name', 'status'])['status'].count().reset_index(name='status_count')
    # Obtendo o índice dos valores máximos de status_count para cada circuito
    idx = frequent_failures.groupby('circuit_name')['status_count'].idxmax()
    # Filtrando as linhas correspondentes aos índices dos valores máximos
    frequent_failures = frequent_failures.loc[idx].reset_index(drop=True)
    # Ordenando os valores por status_count em ordem decrescente (opcional)
    frequent_failures = frequent_failures.sort_values(by='status_count', ascending=False)

    #Fazendo INNER JOIN nas tabelas criadas para depois definir o novo indice em função do nome do circuito circuit_name
    df_filtered = pd.merge(df_filtered, races_per_circuit, on='circuit_name').merge(mean_per_circuit, on='circuit_name').merge(frequent_failures, on='circuit_name').set_index('circuit_name')
    df_filtered.index.name = 'Circuit' #Alterando o nome do indice para Circuit
    df_filtered['rate'] = round(df_filtered['status_count'] * 100 / df_filtered['status_x'], 0)

    #Utilizando a função st.dataframe do streamlit para criar a tabela com as medidas.
    #É necessário utilizar o condicional para mudar o dataframe se options esta ativo para evitar mostrar Rate%
    if options:
        df_filtered = df_filtered.drop(columns=['status','status_count','rate'])
                            
    st.dataframe(df_filtered,
                    column_config={
                        'flag_url_y': st.column_config.ImageColumn('Country Flag'),
                        'status_x': st.column_config.ProgressColumn('Mechanical issues', format='%d', min_value=0, max_value= int(df_filtered['status_x'].max())),
                        'status_y': st.column_config.ProgressColumn('Mean', format='%d', min_value=0, max_value=int(df_filtered['status_y'].max())),
                        'country_y': st.column_config.Column('Country'),
                        'location_y': st.column_config.Column('Location'),
                        'raceId': st.column_config.Column('Races'),
                        'status': st.column_config.Column('Frequent Failure'),
                        'status_count': st.column_config.Column('Times'),
                        'rate': st.column_config.NumberColumn('Rate', format='%d%%')
                    })
    
#Configurando o histograma de frequencia de falhas mecânicas
with col7:
    df_hist = races_results_filtered[races_results_filtered['status'].isin(mechanical_issues)]

    #Definindo condicional
    if options:
        df_hist = df_hist[df_hist['status'].isin(options)]

    df_hist = df_hist[['laps']]
    
    fig3 = px.histogram(df_hist, x="laps",
                        nbins=20,
                        title=f'Mechanical issues histogram {options}',
                        marginal='box')
    fig3.update_layout(bargap=0.1)

    st.plotly_chart(fig3)


#Configurando KPIs
#Alterando os KPIs em função do multiselect
if options:
    df_kpi = races_results_filtered[races_results_filtered['status'].isin(options)]
else:
    df_kpi = races_results_filtered

#Calculando os KPIs
total_races = df_kpi[['raceId']].drop_duplicates().count().iloc[0]
total_seasons = df_kpi[['year']].drop_duplicates().count().iloc[0]
total_teams = df_kpi[['constructorId']].drop_duplicates().count().iloc[0]
total_mechanical_issues = df_kpi[['status']]
total_mechanical_issues = (df_kpi[df_kpi['status'].str.contains(pat=pattern, case=False, na=False)].count()).iloc[0]
total_countries = df_kpi[['country_y']].drop_duplicates().count().iloc[0]
total_circuits = df_kpi[['circuit_name']].drop_duplicates().count().iloc[0]

#Mostrando os KPIs
kpi1.metric(label='Races', value=total_races)
kpi2.metric(label='Seasons', value=total_seasons)
kpi3.metric(label='Teams', value=total_teams)
kpi4.metric(label='Mechanical issues', value=total_mechanical_issues)
kpi5.metric(label='Countries', value=total_countries)
kpi6.metric(label='Circuits', value=total_circuits)
    
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



