
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt, mpld3
import math
import altair as alt

painel = ("Avarias","Financiamento", "Residual")
carros = ("Mobi", 66000.00 , "Strada", 89990.00)
tipos_carros = ["PickUp","Popular", "Caminhões"]
finan = {"Prazo" : 48, "Taxa Financ" : 0.021}

# acessar TXT para premissas iniciais
df = pd.read_csv("premissas.txt",sep=":")
premissa = {}
for index, row in df.iterrows():
   premissa[row["nome"]] = row["valor"]

def price(carros,finan):
   parc_price = []  
   for carro in range(1,len(carros),2):       
      valor_parcela = carros[carro] * (finan["Taxa Financ"] / (1 - (1 + finan["Taxa Financ"]) ** - finan["Prazo"]))      
      parc_price.append(carros[carro-1])
      parc_price.append('% 0.2f' % valor_parcela)   
   return parc_price
price_par = price(carros,finan)

st.set_page_config( "Alugar", layout="wide")

st.html("""   <style> h3 {color:blue;} </style>  """)

prazo_fin = []
parcelas=[] 
for i in range(int(finan["Prazo"])):
   parcelas.append(price_par[1])
   prazo_fin.append(i+1)
   dados = {"Prazo" : prazo_fin, "Parcela" : parcelas }
prazos = ["48","12","18","24","36","48","60"]
IPVA = int(premissa["IPVA-Strada"])

Seguro = float(premissa["Seguro"])
with st.sidebar:  
      tela = 0
      
      st.title(":red[Comprar ou Alugar] :car:")      
      veiculo = st.selectbox("Veiculo ",tipos_carros)      
      valor = st.number_input("Valor", min_value=50000, max_value=250000, value=90000)
      prazo = st.slider("Prazo Financiamento tabela Price", 12, 60, 48)
      v_ipva = st.number_input("IPVA %", min_value=1.0, max_value=50.0, value=3.0)
      v_seguro = st.number_input("Seguro %", min_value=1.0, max_value=50.0, value=4.0)
      km = st.number_input("Média de KM rodados por ANo",min_value=5000, max_value=80000, value=24000)
      pneus = st.number_input("Valor troca de 4 pneus",min_value=500, max_value=8000, value=1800)
      ano= ((pneus*((km*(prazo/12))/50000))/((km/12)*prazo))+0.1
      print(ano)
      manut = st.number_input("Valor de Manutenção por KM Rodado",min_value=0.010, max_value=2.00, value=ano)     
       
      taxa = st.number_input("Taxa %", min_value=1.0, max_value=50.0, value=2.1)  
      valor_aluguel = st.number_input("Valor Aluguel", min_value=1000, max_value=6000, value=2900) 
      avaria = st.number_input("Avaria mensal veiculo alugado % valor aluguel", min_value=0.8, max_value=50.0, value=2.0) 
      reajuste = st.number_input("Reajuste anual aluguel %", min_value=2.0, max_value=50.0, value=4.0)
      residual = st.number_input("Residual para revenda %", min_value=2.0, max_value=100.0, value=50.0)      
      cont=0
      alugar=[]
      avaria=valor_aluguel*(avaria/100)
      taxa=taxa/100
      v_ipva=v_ipva/100
      v_seguro=v_seguro/100
      reajuste=reajuste/100
      residual = residual/100
      manutencao = (km * manut)/12
      print(manutencao)
      for i in range(48):
         alugar.append(2600)
      
      if st.button("Processar"):
         tela = 1
         carros = (veiculo, valor)         
         finan = {"Prazo" : int(prazo), "Taxa Financ" : taxa}                
         price_par = price(carros,finan)           
         prazo_fin = []
         parcelas=[]    
         aluguel = (veiculo,avaria,reajuste)         
         valor_alu = premissa.items()
         for i in valor_alu:
            if i[0]==veiculo:               
               valor_alu=i[1]
               if valor_alu != valor_aluguel:
                  valor_alu=valor_aluguel
         alugar=[]
         x=0
         
         for i in range(int(prazo)):
            x=valor_alu + avaria         
            if i % 12 == 0 and i > 0:               
               valor_alu=valor_alu+(valor_alu*reajuste)
               y=valor_alu + avaria
               alugar.append(y)
               continue
            alugar.append(x)
         
         for i in range(int(prazo)): 
            x=float(price_par[1]) 
            x=x+manutencao  
            if i == 0:
               x=x+float(premissa["1º Licenciamento"])
            if i % 12 == 0 and i > 0: 
               x=x+float(premissa["Licenciamento"] )
               valor = valor + (valor*float(premissa["Reajuste"]))
               cont = 1
            if cont >=1 :
               if cont <=4 :
                  if price_par[0]=="PickUp":
                     x=x+((valor*v_ipva)/4)                     
                     x=x+((valor*v_seguro)/10)
                  if price_par[0]=="Popular":
                     x=x+((valor*v_ipva)/4)
                     x=x+((valor*v_seguro)/10)
               if cont>4<=11:     
                  x=x+((valor*v_seguro)/10) 
               cont = cont + 1
               if cont == 11 :
                  cont = 0              
            parcelas.append(x)
            prazo_fin.append(i+1)
            dados = {"Prazo" : prazo_fin, "Parcela" : parcelas }
      
df = pd.DataFrame(dict(dados))

df["Alugar"] = alugar


x = ["Parcela","Alugar"]
if tela == 1:
   graf_linha_A = alt.Chart(df).mark_line(
      point=alt.OverlayMarkDef(color="green",size=50, filled=False, fill="white"),
      color="green"
      ).encode(
      x= alt.X("Prazo", axis=alt.Axis(grid=False), title='Category'),
      y= alt.Y("Parcela",               
      axis=alt.Axis(grid=False),scale=alt.Scale(domain=(1500,5800))),               
      tooltip= ["Prazo","Parcela"],   
      
   ).properties(
      width=1000,
      height=400,
      
      
   )
   graf_linha_B = alt.Chart(df).mark_line(
      point=alt.OverlayMarkDef(color="red",size=50, filled=False, fill="white"),
      color="red"
      ).encode(
      x= alt.X("Prazo"), 
      y= alt.Y("Alugar"),
      tooltip= ["Prazo","Alugar"]
   )

   st.altair_chart(graf_linha_A+graf_linha_B,use_container_width=True)



   ### somar listas

   soma_aluguel = 0
   soma_comprar = 0

   for numero in alugar:
      soma_aluguel = soma_aluguel+numero
   for numero in parcelas:
      soma_comprar += float(numero)


   
   col1, col2, col3 = st.columns(3,vertical_alignment="top", border=True )
   col1.subheader("Alugar " )
   col2.subheader("Comprar" )
   result_alugar_comprar = (((soma_comprar-soma_aluguel)/soma_aluguel)*100)
   if soma_aluguel > soma_comprar :
      col3.subheader("Comprar Melhor Alugar " )
   else :
      col3.subheader("Alugar Melhor Comprar " )
   
   col1, col2, col3 = st.columns(3,vertical_alignment="top" , border=True)
   col1.subheader(":car: " + str(f'R$ {soma_aluguel:,.2f}') )
   col2.subheader(":car: " + str(f'R$ {soma_comprar:,.2f}') )
   if soma_aluguel > soma_comprar :
      col3.subheader("Comprar " + str('% 0.2f' % (((soma_comprar-soma_aluguel)/soma_aluguel)*100)) + '%' + " Alugar")
   else :
      col3.subheader("Alugar " + str('% 0.2f' % (((soma_aluguel-soma_comprar)/soma_aluguel)*100)) + '%' + " Comprar")
   valor_residual = soma_comprar-(valor*residual)
   
   st.html('''<h3><p style="font-size: 32px;background-color:#ADD8E6;text-align:center;">
           Comprar ou Alugar com avaliação residual de revenda do veículo ao término do financiamento</p></h3>
           <hr size="8" width="100%">''')
   
   
   col1, col2, col3,col4 = st.columns([1,1,1.2,1.8],vertical_alignment="top", border=True )
   col1.subheader("Alugar " )
   col2.subheader("Comprar" )
   col3.subheader("Menos "+ str(int(residual*100))+ " % Residual - " + str(int(valor*residual)) )
   result_alugar_comprar = (((soma_comprar-soma_aluguel)/soma_aluguel)*100)
   if soma_aluguel > (soma_comprar-valor_residual) :
      col4.subheader("Melhor Comprar" )
   else :
      col4.subheader("Melhor Alugar " )
   
   col1, col2, col3, col4 = st.columns([1,1,1.2,1.8], vertical_alignment="center", border=True )
   col1.subheader(":car: " + str(f'R$ {soma_aluguel:,.2f}') )
   col2.subheader(":car: " + str(f'R$ {soma_comprar:,.2f}') )
   col3.subheader(":car: " + str(f'R$ {valor_residual:,.2f}') )
   if soma_aluguel > (soma_comprar-valor_residual) :
      col4.subheader("Comprar " + str('% 0.2f' % (((valor_residual-soma_aluguel)/soma_aluguel)*100)) + '%' + " Alugar")
   else :
      col4.subheader("Alugar " + str('% 0.2f' % (((valor_residual-soma_aluguel)/soma_aluguel)*100)) + '%' + " Comprar")
   pd.set_option("display.precision",2)
   def formatar(valor):
      return "$ {:,.2f}".format(valor)
  
   
   
   

   
   
