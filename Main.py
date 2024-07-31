import streamlit as st
import pandas as pd
import plotly.express as px


#Configuração inicial de pagina
st.set_page_config(page_title='F1 Reliability Dashboard',
                   page_icon='🏁',
                   layout='wide',
                   initial_sidebar_state='auto')

#Carregando o dataset (utilizando a memoria cache para não ter que carregar dos csv tempo todo)
@st.cache_data
def load_dataset():
    df_constructors = pd.read_csv('./dataset/constructors.csv')
    df_status = pd.read_csv('./dataset/status.csv')
    df_results = pd.read_csv('./dataset/results.csv')
    df_races = pd.read_csv('./dataset/races.csv')
    df_drivers = pd.read_csv('./dataset/drivers.csv')
    df_constructor_pictures = pd.read_excel('./dataset/constructor_car_pictures.xlsx')
    df_circuits = pd.read_csv('./dataset/circuits.csv')
    df_circuits.rename(columns={'name': 'circuit_name', 'url': 'link'}, inplace=True)
    df_circuits_pictures = pd.read_excel('./dataset/circuits_pictures.xlsx')
    #Construindo a tabela fato principal
    f_races_results = pd.merge(df_results,df_races, on='raceId').\
                            merge(df_drivers,on='driverId').\
                            merge(df_constructors, on='constructorId').\
                            merge(df_status, on='statusId').\
                            merge(df_constructor_pictures, on='constructorId').\
                            merge(df_circuits_pictures, on='circuitId').\
                            merge(df_circuits, on='circuitId')
    f_races_results['driver'] = f_races_results['forename'] + ' ' + f_races_results['surname'] #criando a coluna driver com nome e sobrenome
    return f_races_results

f_races_results = load_dataset() #armazenando a tabela fato na memoria cache para melhorar performance
st.session_state['main_df'] = f_races_results #armazenando informação no session_state para paginas múltiplas e melhorar performance

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

# ---- SIDEBAR ----
#Carregando imagens do logo da F1
st.logo('https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/640px-F1.svg.png')
#st.sidebar.image('https://upload.wikimedia.org/wikipedia/commons/4/45/F1_logo.svg') #logo tradicional carregado como imagem 

link = 'https://www.linkedin.com/in/andr%C3%A9s-michelangelli/'
st.sidebar.markdown(f"Made by [Andrés A. Michelangelli]({link})")

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
    value=(years[0], years[-1]))

#filtrando a tabela fato pelos anos selecionados pelo usuario
races_results_filtered = f_races_results[(f_races_results['year'] >= start_year) & 
                                             (f_races_results['year'] <= end_year)]
st.sidebar.divider()
teams = st.sidebar.multiselect(
                            "Select teams: ",
                            races_results_filtered['name_y'].unique()
                            )

st.sidebar.divider()
options = st.sidebar.multiselect(
                            "Select mechanical issues: ",
                            races_results_filtered[races_results_filtered['status'].str.contains(pattern, case=False, na=False)]['status'].unique()
                            )

#Estabelecendo as condicionais
if options and not teams:
    races_results_filtered = f_races_results[(f_races_results['year'] >= start_year) & 
                                             (f_races_results['year'] <= end_year) & 
                                             (f_races_results['status'].isin(options))]
elif teams and not options:
    races_results_filtered = f_races_results[(f_races_results['year'] >= start_year) & 
                                             (f_races_results['year'] <= end_year) &  
                                             (f_races_results['name_y'].isin(teams))]
elif options and teams:
    races_results_filtered = f_races_results[(f_races_results['year'] >= start_year) & 
                                            (f_races_results['year'] <= end_year) & 
                                            (f_races_results['status'].isin(options)) & 
                                            (f_races_results['name_y'].isin(teams))]

# ---- MAINPAGE ----  

st.title(':bar_chart: F1 Reliability Analysis Dashboard')
#st.markdown('##') #opcional
st.write('  ')

#Estabelecendo colunas e estrutura
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
st.divider()
col1, col2= st.columns([0.7, 0.3])
col3, col4= st.columns(2)

# Calculando e mostrando os KPIs

total_races = races_results_filtered[['raceId']].drop_duplicates().count().iloc[0]
total_seasons = races_results_filtered[['year']].drop_duplicates().count().iloc[0]
total_drivers = races_results_filtered[['driverId']].drop_duplicates().count().iloc[0]
total_teams = races_results_filtered[['constructorId']].drop_duplicates().count().iloc[0]
total_mechanical_issues = races_results_filtered[['status']]
total_mechanical_issues = (total_mechanical_issues[total_mechanical_issues['status'].str.contains(pat=pattern, case=False, na=False)].count()).iloc[0]

with kpi1:
    st.subheader('🏁 Races: ')
    st.subheader(f'{total_races}')
with kpi2:
    st.subheader(':earth_americas: Seasons: ')
    st.subheader(f'{total_seasons}')
with kpi3:
    st.subheader(':bust_in_silhouette: Drivers: ')
    st.subheader(f'{total_drivers}')
with kpi4:
    st.subheader(':racing_car: Constructors: ')
    st.subheader(f'{total_teams}')
with kpi5:
    st.subheader(':wrench: Mechanical issues: ')
    st.subheader(f'{total_mechanical_issues}')

# Criando o grafico de problemas mecanicos por ano com base na lista mechanical issues
with col1:
    mechanical_issues_year_1 = races_results_filtered[['year', 'status']]
    mechanical_issues_year_2 = mechanical_issues_year_1[mechanical_issues_year_1['status'].str.contains(pattern, case=False, na=False)].groupby('year')['status'].count().reset_index()
    
    fig1 = px.bar(mechanical_issues_year_2, x='year', y='status',
                labels={'x':'year', 'y':'mechanical issues'},
                title='Mechanical Issues per Year',
                height=500)
    fig1.update_traces(texttemplate='%{y}',
                       textposition='outside',
                       textfont_color='white',
                       textfont_size=12)
    fig1.update_xaxes(tickmode='linear',  # Define o modo de tick como linear para mostrar todos os anos
                      tickangle=-45,      # Define o ângulo dos ticks para evitar sobreposição
                      dtick=2             # Define o intervalo entre ticks como 1 para mostrar cada ano
                    )

    st.plotly_chart(fig1)

#Criando grafico de pizza para % de mechanical issues (race outcomes)
with col2:
    outcomes = races_results_filtered[['status']].count().iloc[0]

    values = [total_mechanical_issues, outcomes - total_mechanical_issues]
    labels = ['Mechanical Issues', 'Other Outcomes']
    # Criando o gráfico de pizza
    fig4 = px.pie(values=values,
                names=labels,
                title='Mechanical Issues as Percentage of Total Outcomes',
                hole= 0.5)
    fig4.update_traces(textfont_size=15)

    # Exibindo o gráfico no Streamlit
    st.plotly_chart(fig4)

#Criando o grafico de problemas mecânicos por equipe
with col3:
    c_mechanical_issues_1 = races_results_filtered[['name_y', 'status']]
    c_mechanical_issues_2 = c_mechanical_issues_1[c_mechanical_issues_1['status'].str.contains(pattern, case=False, na=False)].groupby('name_y')['status'].count().reset_index()
    
    #Definindo opção para mostrar os 10 últimos colocados junto com condicionais
    tail1 = st.toggle("Show teams with less failures")

    if tail1:
        c_mechanical_issues_2 = c_mechanical_issues_2.sort_values(by='status', ascending=False).tail(10)
        order1 = 'total descending'
        title1 = 'Top 10 Mechanical issues by constructor (ascending)'
    else:
        c_mechanical_issues_2 = c_mechanical_issues_2.sort_values(by='status', ascending=False).head(10)
        order1 = 'total ascending'
        title1 = 'Top 10 Mechanical issues by constructor (descending)'
    #Graficando o resultado
    fig2 = px.bar(c_mechanical_issues_2, x='status', y='name_y', orientation='h',
                labels={'status': 'mechanical issues', 'name_y': 'constructor'},
                title=title1,
                text='status', height=400)

    fig2.update_yaxes(categoryorder=order1)
    fig2.update_traces(textposition='outside', textfont_color='white')

    st.plotly_chart(fig2)

#Criando grafico de problemas mecanicos mais frecuentes
with col4:
    mechanical_issues_3 = races_results_filtered[['status']].copy()
    mechanical_issues_4 = mechanical_issues_3[mechanical_issues_3['status'].str.contains(pattern, case=False, na=False)].groupby('status').size().reset_index(name='status_count')
    
    #Definindo opção para mostrar os 10 últimos colocados junto com condicionais
    tail2 = st.toggle('Show less frequent mechanical issues')

    if tail2:
        mechanical_issues_4 = mechanical_issues_4.sort_values(by='status_count', ascending=False).tail(10)
        order2 = 'total descending'
        title2 = 'Less frequent mechanical issues'
    else:
        mechanical_issues_4 = mechanical_issues_4.sort_values(by='status_count', ascending=False).head(10)
        order2 = 'total ascending'
        title2 = 'Most frequent mechanical issues'
    #Graficando
    fig3 = px.bar(mechanical_issues_4, x='status_count', y='status', orientation='h',
                labels={'status_count': 'quantity', 'status': 'mechanical issues'},
                title=title2,
                text='status_count', height=400)

    fig3.update_yaxes(categoryorder=order2)
    fig3.update_traces(textposition='outside', textfont_color='white')

    st.plotly_chart(fig3)

##---- HIDE STREAMLIT STYLE -----
##Codigo para ocultar marca d'agua e botões do streamlit
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


