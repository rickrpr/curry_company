# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )

# ==========================================
# Funções
# ==========================================

def country_maps( df1 ):
    
    # calcular o valor mediano da latitude e da longitude, agrupado por cidade e tipo de tráfego.
    df_aux = ( df1.loc[: , ['City' , 'Road_traffic_density', 'Delivery_location_latitude' , 'Delivery_location_longitude']]
                  .groupby(['City' , 'Road_traffic_density'])
                  .median()
                  .reset_index() )
    
    # Para desenhar o mapa usar a biblioteca folium:
    # Guardar na variável map
    
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'] , 
                 location_info['Delivery_location_longitude' ]],
                popup=location_info[['City' , 'Road_traffic_density']] ).add_to(map)
        
    folium_static( map, width = 1024 , height = 600)


    
    
def order_share_per_week( df1 ):
    # Calcular o número de entregas por semana e o cálculo do número de entregadores únicos por semana
    # e vou dividir os dois valores, exibindo-os em um gráfico de linha.

    # número de pedidos por semana:
    df_aux1 = (df1.loc[:, ['ID' , 'week_of_year']]
                     .groupby( 'week_of_year')
                     .count().reset_index() )

    # número de entregadores únicos por semana
    df_aux2 = ( df1.loc[: , ['Delivery_person_ID' , 'week_of_year']]
                     .groupby('week_of_year')
                     .nunique().reset_index() )

    # Juntar dois dataframes usando a função merge()
    df_aux = pd.merge(df_aux1 , df_aux2 , how = 'inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux , x = 'week_of_year' , y = 'order_by_deliver')
    st.plotly_chart( fig, use_container_width = True )
          
    return fig



def order_per_week( df1 ):
    
    # Fazer um contagem da colunas “ID” agrupado “Order Date” e usar uma bibliotecas de visualização para mostrar o gráfico de barras.

    # Criar a coluna da semana
    # É necessário calcular a semana da coluna 'Order_Date'.
    # A função strdftime() formata a string no tempo. 
    # A máscara %U pega o Domingo como primeiro dia da semana
    # A mascara %W pega a Segunda feira como primeiro dia da semana
    # .dt transforma string em data
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    df_aux = df1.loc[: ,['ID','week_of_year' ]].groupby('week_of_year').count().reset_index()

    # Plotar gráfico de linhas
    fig = px.line(df_aux, x = 'week_of_year' , y = 'ID')
    st.plotly_chart( fig, use_container_width = True )
    
    return fig



def traffic_order_city( df1 ):
    
    # Contar o número de pedidos, agrupados por cidade e tipo de tráfego e desenhar um gráfico de bolha.
    df_aux = ( df1.loc[: , ['ID' , 'City' , 'Road_traffic_density'] ]
                      .groupby(['City' , 'Road_traffic_density'])
                      .count()
                      .reset_index() )
    
    fig = px.scatter(df_aux, x = 'City' , y = 'Road_traffic_density' , size= 'ID' , color = 'City' )
    st.plotly_chart( fig, use_container_width = True )
    
    return fig
            



def traffic_order_share( df1 ):
    
    # Contar o número de entregas, agrupado pela coluna de densidade de tráfego e calcular a porcentagem que cada valor representa no todo.
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    # gráfico
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
    st.plotly_chart( fig, use_container_width = True )            
    
    return fig


def order_metric(df1):
    
            
    # Order Matric
    # Fazer um contagem da colunas “ID” agrupado “Order Date” e usar uma bibliotecas de visualização para mostrar o gráfico de barras.
    # colunas
    cols = ['ID' , 'Order_Date']
    df_aux = df1.loc[: , cols].groupby('Order_Date').count().reset_index()
    # desenhar o gráfico de colunas
    fig = px.bar(df_aux, x= 'Order_Date' , y= 'ID')
    st.plotly_chart( fig, use_container_width = True )
    
    return fig



def clean_code( df1 ):
    
    """ Essa função tem a responsabilidade de limpar o dataframe
         Tipos de limpeza:
         1. Remoção dos dados NaN
         2. Mudança do tipo da coluna de dados
         3. Remoção dos espaços das variáveis de texto
         4. Formatação da coluna de datas
         5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
         
         Input: Dataframe
         Output: Dataframe
     
    """
    # Eliminar linhas com NaN
    # linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    linhas_selecionadas = ((df1['Delivery_person_Age'] != 'NaN ') & (df1['Delivery_person_Ratings'] 
                          != 'NaN ') & (df1['Delivery_person_ID'] != 'NaN ') & (df1['Road_traffic_density'] 
                          != 'NaN ') & (df1['City'] != 'NaN ') &  (df1['Festival'] != 'NaN ') )
    
    df1 = df1.loc[linhas_selecionadas , :].copy()
    
    # 1. Converter a coluna Age de texto para número inteiro
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    # 2. Converter a coluna Ratings de texto para número decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    
    # 3. Converter a coluna Order_date de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format = '%d-%m-%Y')
    
    
    # 4. Converter a coluna Multiple_deliveries de texto para número inteiro
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas , :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    # 5. Removendo os espacos dentro de strings/text/objects
        # antes é necessário fazer um reset do index
        # drop = True é para não criar uma coluna com cabeçalho "Index"
    #df1 = df1.reset_index(drop = True)
    # Percorrer cada linha para retirar os espaços
    #for i in range(len(df1)):
    #  df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()
    
    # 6. Removendo os espacos dentro de strings/text/objects (método sem usar 'for')
    #(mais rápido)
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    
    # 7. Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

# -------------------------------------------- Início da estrutura lógica do código -----------------------------------------------

# import dataset
df = pd.read_csv( r'dataset/train.csv' )

df1 = clean_code(df)



# VISÃO - Empresa


# ====================================================================
# BARRA LATERAL
# ====================================================================
st.header('Marketplace - Visão Cliente')


#image_path = r'C:\Users\Ricardo\Documents\data_science\repos\ftc\logo.png'
#image = Image.open( image_path )
image = Image.open( 'logo.png' )
st.sidebar.image(image, width=120)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown( """___""")

st.sidebar.markdown( '## Selecione uma data limite' )
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime( 2022, 4, 13),
    min_value=pd.datetime( 2022, 2, 11 ),
    max_value=pd.datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY' )

# st.header( date_slider )
st.sidebar.markdown( """___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medius',  'High', 'Jam'],
    default =  ['Low', 'Medius',  'High', 'Jam'] )

st.sidebar.markdown( """___""")
st.sidebar.markdown( '### Powered by Comunidade DS')

#Filtro de Data
lihas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[lihas_selecionadas, :]

#Filtro de trânsito
lihas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[lihas_selecionadas, :]



# ====================================================================
# LAYOUT NO STREAMLIT
# ====================================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        # Order Metric
        st.markdown( '# Orders per day' )
        fig = order_metric(df1)
        
            
        
        
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            
            st.header( 'Traffic Order Share' )
            fig = traffic_order_share( df1 )
              
                
            
        
        with col2:
            st.header( 'Traffic Order City' )
            fig = traffic_order_city( df1 )
            

    
    
    
with tab2:
    with st.container():
        st.markdown( "# Order per week" )
        fig = order_per_week( df1 )
        
    

    with st.container():
        st.markdown( "# Order Share per week" )
        fig = order_share_per_week( df1 )
               

      
    
    
with tab3:
    st.markdown( "# Country Map" )
    country_maps( df1 )
