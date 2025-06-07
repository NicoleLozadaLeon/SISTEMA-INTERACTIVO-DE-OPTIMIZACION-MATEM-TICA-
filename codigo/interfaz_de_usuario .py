import streamlit as st
from solvers import LP, IP, NLP, MILP, MINLP

# Título de la aplicación
st.title("🔍 Sistema Interactivo de Optimización Matemática")

# Menú desplegable
opcion = st.selectbox("Seleccione el tipo de problema a resolver:", [
    "Ninguno",
    "Programación Lineal (LP)",
    "Programación Entera (IP)",
    "Programación No Lineal (NLP)",
    "Programación Entera Mixta (MILP)",
    "Programación No Lineal Mixta (MINLP)"
])
   

if opcion == "Programación Lineal (LP)":
    lp_solver = LP()
    lp_solver.interfaz()

elif opcion == "Programación Entera (IP)":
    ip_solver = IP()
    ip_solver.interfaz()
elif opcion == "Programación No Lineal (NLP)":
    nlp_solver = NLP()
    nlp_solver.interfaz()
elif opcion == "Programación Entera Mixta (MILP)":
    milp_solver = MILP()
    milp_solver.interfaz()
elif opcion == "Programación No Lineal Mixta (MINLP)":
    minlp_solver = MINLP()
    minlp_solver.interfaz()



