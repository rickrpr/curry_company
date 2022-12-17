# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽️', layout='wide' )

# ==========================================
# Funções
# ==========================================

def avg_std_time_on_traffic( df1 ):
    # Colunas envolvidas no cálculo do tempo médio de entrega e desvio padrão de entrega por cidade e tipo de tráfego:
    cols = ['City' , 'Time_taken(min)', 'Road_traffic_density']

    df_aux = df1.loc[:, cols].groupby( ['City' , 'Road_traffic_density'] ).agg( {'Time_taken(min)': ['mean' , 'std'] })
    df_aux.columns = ['avg_time' , 'std_time']
    df_aux = df_aux.reset_index()


    fig = px.sunburst( df_aux, path=['City' , 'Road_traffic_density'], values='avg_time',
                     color= 'std_time', color_continuous_scale= 'RdBu',
                     color_continuous_midpoint=np.average(df_aux['std_time']))

    st.plotly_chart( fig )

    return fig



def avg_std_time_graph( df1 ):
    # Colunas envolvidas no cálculo do tempo médio de entrega e desvio padrão de entrega por cidade:
    cols = ['City' , 'Time_taken(min)' ]
    df_aux = df1.loc[:, cols].groupby( 'City' ).agg( {'Time_taken(min)': ['mean' , 'std'] })
    df_aux.columns = ['avg_time' , 'std_time']
    df_aux = df_aux.reset_index()


    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'],
                         error_y=dict( type='data', array=df_aux['std_time'])) )

    fig.update_layout(barmode='group')
    st.plotly_chart( fig )

    return fig



def avg_std_time_delivery( df1, festival, op ):
    """
    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
    Parâmetros:
        Input:
            - df: Dataframe com os dados necessários para o cálculo.
            - op: Tidpo de operação que precisa ser calculado.
                'avg_time': Calcula o tempo médio.
                'std_time': Calcula o desvio padrão do tempo
        Output:
            - df: Dataframe com 2 colunas e 1 linha.
        
    """
        
    cols = ['Time_taken(min)', 'Festival']
    df_aux = ( df1.loc[:, cols].groupby( 'Festival' ).agg( {'Time_taken(min)': ['mean' , 'std'] }) )
    df_aux.columns = ['avg_time' , 'std_time']
    df_aux = df_aux.reset_index()
    linhas_selecionadas = df_aux['Festival'] == festival
    df_aux = np.round(df_aux.loc[linhas_selecionadas , op] , 2)
        
    return df_aux


def distance( df1 , fig ):
    if fig == False:
        cols = ['Delivery_location_latitude' , 'Delivery_location_longitude' , 'Restaurant_latitude' , 'Restaurant_longitude']
        # Comando para calcular distâncias a partir das latitudes e longitudes:
        # haversine((latitude, longitude), (latitude, longitude) )
        # A distancia calculada fica armazenada numa nova coluna chamada 'distance'
        df1['distance'] = df1.loc[: , cols].apply( lambda x: 
                                   haversine( (x['Restaurant_latitude'] , x['Restaurant_longitude']), 
                                              (x['Delivery_location_latitude'] , x['Delivery_location_longitude'] )), axis=1)
        avg_distance = np.round(df1['distance'].mean() , 2)
            
        return avg_distance
            
    else:
        cols = ['Delivery_location_latitude' , 'Delivery_location_longitude' , 'Restaurant_latitude' , 'Restaurant_longitude']
        # Comando para calcular distâncias a partir das latitudes e longitudes:
        # haversine((latitude, longitude), (latitude, longitude) )
        # A distancia calculada fica armazenada numa nova coluna chamada 'distance'
        df1['distance'] = df1.loc[: , cols].apply( lambda x: 
                                   haversine( (x['Restaurant_latitude'] , x['Restaurant_longitude']), 
                                              (x['Delivery_location_latitude'] , x['Delivery_location_longitude'] )), axis=1)
            

        avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
        fig = go.Figure( data=[ go.Pie( labels = avg_distance['City'], values=avg_distance['distance'] , pull = [0.05, 0.05, 0] ) ] )   
            
        return fig



def top_delivers( df1 , top_asc ):
    
    df2 = ( df1.loc[:, ['Delivery_person_ID' , 'Time_taken(min)' , 'City']]
       .groupby(['City' , 'Delivery_person_ID']).max()
       .sort_values(['City' , 'Time_taken(min)'], ascending=top_asc)
       .reset_index() )
    
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian' , :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban' , :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban' , :].head(10)

    df3 = pd.concat([df_aux01 , df_aux02, df_aux03] ).reset_index(drop=True)
    
    return df3




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


df1 = clean_code( df )



# VISÃO - Restaurante


# ====================================================================
# BARRA LATERAL
# ====================================================================
st.header('Marketplace - Visão Entregadores')


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
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '__', '__'] )

with tab1:
    with st.container():
        st.title('Overal Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            
            deliverymen_unique = len( df1.loc[: , 'Delivery_person_ID'].unique() )
            col1.metric( 'Entregadores únicos' ,deliverymen_unique )

        with col2:
            avg_distance = distance( df1, fig=False)
            col2.metric( 'Distância média das entregas' , avg_distance )
   


        with col3:
            df_aux = avg_std_time_delivery( df1, 'Yes', 'avg_time')              
            col3.metric( 'Tempo médio de entrega com festival' , df_aux )
            
            
        with col4:
            df_aux = avg_std_time_delivery( df1, 'Yes', 'std_time')       
            col4.metric( 'STD de entrega com festival' , df_aux )
             
            
            
        with col5:
            
            df_aux = avg_std_time_delivery( df1, 'No', 'avg_time')            
            col5.metric( 'Tempo médio de entrega com festival' , df_aux )
            
            
            
            
        with col6:
            
            df_aux = avg_std_time_delivery( df1, 'No', 'std_time')             
            col6.metric( 'STD de entrega com festival' , df_aux )
            
        
        
        
    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = avg_std_time_graph( df1 )
            
            
        with col2:
            
            # Colunas envolvidas no cálculo do tempo médio de entrega e desvio padrão de entrega por cidade e tipo de pedido:
            cols = ['City' , 'Time_taken(min)', 'Type_of_order']
            
            df_aux = df1.loc[:, cols].groupby( ['City' , 'Type_of_order'] ).agg( {'Time_taken(min)': ['mean' , 'std'] })
            df_aux.columns = ['avg_time' , 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
            

        
    with st.container():
        st.markdown("""___""")
        st.title( 'Distribuição do Tempo' )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # st.title('Distância média por Cidade')
            fig = distance( df1, fig=True )
            st.plotly_chart( fig )
            
                        
        
        with col2:
            fig = avg_std_time_on_traffic( df1 )

        
    with st.container():
        st.markdown("""___""")
