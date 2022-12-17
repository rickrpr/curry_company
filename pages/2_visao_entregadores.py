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

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide' )

# ==========================================
# Funções
# ==========================================

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




# VISÃO - Entregadores


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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '___', '___'] )

with tab1:
    with st.container():
        st.title('Overal Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        with col1:
            # A maior idade dos entregadores:
            maior_idade = df1.loc[: ,'Delivery_person_Age' ].max()
            col1.metric( 'Maior Idade', maior_idade )
            
        with col2:
            # A menor idade dos entregadores:
            menor_idade = df1.loc[: ,'Delivery_person_Age' ].min()
            col2.metric( 'Menor Idade', menor_idade )
            
        with col3:
            # A melhor condição de veículos:
            melhor_condicao = df1.loc[: ,'Vehicle_condition' ].max()
            col3.metric( 'Melhor Condição', melhor_condicao)
            
        with col4:
            # A pior condição de veículos:
            pior_condicao = df1.loc[: ,'Vehicle_condition' ].min()
            col4.metric( 'Pior Condição', pior_condicao )
            
            
    with st.container():
        st.markdown( """___""" )
        st.title('Avaliacoes')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown( '##### Avaliacao medias por entregadores' )
            df_aux = (df1.loc[:, ['Delivery_person_ID' , 'Delivery_person_Ratings']]
                      .groupby('Delivery_person_ID')
                      .mean().reset_index() )
            st.dataframe( df_aux )
                
                
                
        with col2:
            st.markdown( '##### Avaliacao media por transito' )
            # A avaliação média por tipo de tráfego:
            # A média e desvio padrão por tipo de tráfego:
            df_aux01 = (df1.loc[:, ['Delivery_person_Ratings' , 'Road_traffic_density']]
                        .groupby('Road_traffic_density')
                        .agg({'Delivery_person_Ratings' : ['mean' , 'std']}).reset_index())

            # Usar o comando .columns para renomear as colunas
            df_aux01.columns = ['Delivery_person_Ratings','delivery_mean' , 'delivery_std']
            st.dataframe( df_aux01 )
            
            st.markdown("""___""")   
            
                       
            st.markdown( '##### Avaliacao media por clima' )
            # A avaliação média por tipo de condição climática:
            df_aux01 = (df1.loc[:, ['Delivery_person_Ratings' , 'Weatherconditions']]
                        .groupby('Weatherconditions')
                        .agg({'Delivery_person_Ratings' : ['mean' , 'std']}).reset_index())

            # Usar o comando .columns para renomear as colunas
            df_aux01.columns = ['Weatherconditions' ,'delivery_mean' , 'delivery_std']
            st.dataframe( df_aux01 )
            
            
            
            
            
            
            
    with st.container():
        st.markdown("""___""")
        st.title( 'Velocidade de Entrega' )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown( '##### Top Entregadores Mais Rápidos' )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )
            
            
            
            
        with col2:
            st.markdown( '##### Top Entregadores Mais Lentos' )
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )