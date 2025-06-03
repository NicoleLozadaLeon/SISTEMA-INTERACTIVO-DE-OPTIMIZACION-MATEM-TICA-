# 🧠 Sistema Interactivo de Optimización Matemática

Este proyecto consiste en el desarrollo de una aplicación interactiva en **Python**, diseñada para modelar y resolver diversos tipos de problemas de **optimización matemática**. Utiliza la biblioteca **Pyomo** e integra solucionadores como **GLPK**, **IPOPT**, **BONMIN**, entre otros.

---

## 🎯 Objetivos del Proyecto

- Crear una interfaz interactiva (consola o web) para seleccionar diferentes tipos de problemas de optimización.
- Implementar módulos para resolver:
  - Programación Lineal (LP)
  - Programación Entera (IP)
  - Programación No Lineal (NLP)
  - Programación Lineal Entera Mixta (MILP)
  - Programación No Lineal Entera Mixta (MINLP)
- Permitir la entrada dinámica de variables, restricciones y funciones objetivo.
- Visualizar resultados y estadísticas del proceso de optimización.

---

## 🧱 Estructura del Sistema

```

code/
│
├── interfaz_de_usuario.py        # Interfaz principal
├── solvers.py                    # solvers utilizados
├── definicion_de_problemas.py    # LP, IP, NLP, MILP, MINLP
├── report.py                     # Generación de reportes y exportación

````

---

## 🔧 Tecnologías Utilizadas

- [Python 3.x](https://www.python.org/)
- [Pyomo](http://www.pyomo.org/)
- [Streamlit](https://streamlit.io/)
- [GLPK](https://www.gnu.org/software/glpk/) / [IPOPT](https://coin-or.github.io/Ipopt/) / [BONMIN](https://coin-or.github.io/Bonmin/)

---

## 🚀 Cómo Ejecutar el Proyecto

1. Instala los requerimientos:
   ```bash
   pip install streamlit pyomo
   sudo apt install glpk-utils  # Para Linux
````

2. Ejecuta la aplicación:

   ```bash
   streamlit run interfaz_de_usuario.py
   ```

---

## 👨‍💻 Autores

* Estudiantes de la asignatura **Optimización** - Semestre I/2025
* Universidad Católica Boliviana

---


