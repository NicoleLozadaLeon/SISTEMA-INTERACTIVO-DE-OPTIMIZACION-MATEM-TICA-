import streamlit as st
from pyomo.environ import *
import numpy as np
from pyomo.opt import SolverStatus, TerminationCondition

class LP:
    def __init__(self):
        self.elementos = []
        self.parametros = {}
        self.restricciones = []
        self.param_objetivo = ""
        self.tipo_objetivo = None

    # ---------------------------
    # Parsers
    # ---------------------------

    def parse_lista(self, texto):
        """
        Convierte una cadena de texto separada por comas en una lista de elementos limpios.
        """
        return [item.strip().replace(" ", "_") for item in texto.split(",") if item.strip()]

    def parse_restricciones(self, restricciones_input, param_names):
        """
        Convierte las entradas de restricciones del usuario en una lista de diccionarios estructurados.
        """
        restricciones = []
        operadores_validos = {"≤": "<=", "≥": ">=", "=": "==", "<": "<", ">": ">", "≠": "!="}

        for idx, restr in enumerate(restricciones_input):
            parametro = restr.get('parametro')
            operador = restr.get('operador')
            valor = restr.get('valor')

            if parametro not in param_names:
                st.error(f"Restricción {idx+1}: Parámetro '{parametro}' no reconocido.")
                continue
            if operador not in operadores_validos:
                st.error(f"Restricción {idx+1}: Operador '{operador}' no válido.")
                continue
            try:
                valor = float(valor)
            except ValueError:
                st.error(f"Restricción {idx+1}: Valor '{valor}' no es numérico.")
                continue

            restricciones.append({
                'parametro': parametro,
                'operador': operadores_validos[operador],
                'valor': valor
            })
        return restricciones

    # ---------------------------
    # Validadores
    # ---------------------------

    def validar_parametros(self, param_names):
        """
        Verifica que cada parámetro tenga valores asignados para todos los elementos.
        """
        for nombre_param in param_names:
            valores = self.parametros.get(nombre_param, {})
            if set(valores.keys()) != set(self.elementos):
                st.error(f"El parámetro '{nombre_param}' no tiene valores para todos los elementos.")
                return False
        return True

    # ---------------------------
    # Constructor del Modelo
    # ---------------------------

    def construir_modelo(self):
        """
        Construye y resuelve el modelo de programación lineal utilizando Pyomo.
        """
        model = ConcreteModel()
        model.i = Set(initialize=self.elementos)

        # Definir parámetros
        for pname in self.parametros:
            model.add_component(pname, Param(model.i, initialize=self.parametros[pname]))

        # Definir variables de decisión
        model.x = Var(model.i, within=NonNegativeReals)

        # Definir función objetivo
        expr_objetivo = sum(getattr(model, self.param_objetivo)[i] * model.x[i] for i in model.i)
        model.objetivo = Objective(expr=expr_objetivo, sense=self.tipo_objetivo)

        # Definir restricciones
        model.restricciones = ConstraintList()
        for restr in self.restricciones:
            expr = sum(getattr(model, restr['parametro'])[i] * model.x[i] for i in model.i)
            if restr['operador'] == "<=":
                model.restricciones.add(expr <= restr['valor'])
            elif restr['operador'] == ">=":
                model.restricciones.add(expr >= restr['valor'])
            elif restr['operador'] == "==":
                model.restricciones.add(expr == restr['valor'])
            elif restr['operador'] == "<":
                model.restricciones.add(expr < restr['valor'])
            elif restr['operador'] == ">":
                model.restricciones.add(expr > restr['valor'])
            elif restr['operador'] == "!=":
                model.restricciones.add(expr != restr['valor'])

        # Resolver modelo
        solver = SolverFactory('glpk')
        resultado = solver.solve(model)

        # Mostrar resultados
        if resultado.solver.status == 'ok' and resultado.solver.termination_condition == 'optimal':
            st.success("✅ Optimización completada con éxito.")
            st.markdown(f"**Valor óptimo de la función objetivo: {model.objetivo():.2f}**")
            for i in model.i:
                st.write(f"{i}: {model.x[i]():.2f}")
        else:
            st.error("La optimización no encontró una solución óptima.")

    # ---------------------------
    # Interfaz de Usuario (UI)
    # ---------------------------

    def interfaz(self):
        st.subheader("📦 Calculadora de Programación Lineal")

        # Paso 1: Ingresar nombres de elementos
        elementos_default = "Desk, Table, Chairs"
        parametros_default = "L, F, C, P"
        param_values_default = {
            "L": {"Desk": 8, "Table": 6, "Chairs": 1},
            "F": {"Desk": 4, "Table": 2, "Chairs": 1.5},
            "C": {"Desk": 2, "Table": 1.5, "Chairs": 0.5},
            "P": {"Desk": 60, "Table": 30, "Chairs": 20}
        }

        elementos_input = st.text_input("Ingrese los nombres de los elementos separados por comas:", value=elementos_default)
        self.elementos = self.parse_lista(elementos_input)

        # Paso 2: Ingresar nombres de parámetros
        parametros_input = st.text_input("Ingrese los nombres de los parámetros separados por comas:", value=parametros_default)
        param_names = self.parse_lista(parametros_input)

        # Paso 3: Asignar valores a los parámetros
        st.markdown("### Parámetros por elemento")
        for pname in param_names:
            self.parametros[pname] = {}
            st.markdown(f"#### Parámetro `{pname}`")
            for el in self.elementos:
                # Usa el valor por defecto si existe, si no, usa 1.0
                default_val = param_values_default.get(pname, {}).get(el, 1.0)
                val = st.number_input(f"{pname}[{el}]", value=default_val, key=f"{pname}_{el}")
                self.parametros[pname][el] = val

        # Paso 4: Definir Función Objetivo
        st.markdown("### Definir Función Objetivo")
        self.param_objetivo = st.selectbox("Seleccione el parámetro para la función objetivo:", param_names)
        objetivo_input = st.selectbox("Seleccione la función objetivo:", ["Maximizar", "Minimizar"])
        self.tipo_objetivo = maximize if objetivo_input == "Maximizar" else minimize

        # Paso 5: Definir Restricciones
        st.markdown("### Definir Restricciones")
        num_restr = st.number_input("Cantidad de restricciones:", min_value=1, value=3, step=1)
        operadores = ["≤", "≥", "=", "<", ">", "≠"]
        restricciones_default = [
            {"parametro": "L", "operador": "≤", "valor": 48},
            {"parametro": "F", "operador": "≤", "valor": 20},
            {"parametro": "C", "operador": "≤", "valor": 8},
        ]
        restricciones_input = []

        for idx in range(int(num_restr)):
            with st.expander(f"Restricción {idx+1}"):
                # Usa valores por defecto si existen, si no, usa el primero de cada lista
                def_param = restricciones_default[idx]["parametro"] if idx < len(restricciones_default) and restricciones_default[idx]["parametro"] in param_names else param_names[0]
                def_op = restricciones_default[idx]["operador"] if idx < len(restricciones_default) else operadores[0]
                def_val = restricciones_default[idx]["valor"] if idx < len(restricciones_default) else 10.0

                parametro = st.selectbox(
                    f"Seleccione el parámetro para la restricción {idx+1}:",
                    param_names,
                    index=param_names.index(def_param) if def_param in param_names else 0,
                    key=f"param_{idx}"
                )
                operador = st.selectbox(
                    f"Seleccione el operador para la restricción {idx+1}:",
                    operadores,
                    index=operadores.index(def_op) if def_op in operadores else 0,
                    key=f"op_{idx}"
                )
                valor = st.number_input(
                    f"Ingrese el valor para la restricción {idx+1}:",
                    value=def_val,
                    key=f"valor_{idx}"
                )
                restricciones_input.append({'parametro': parametro, 'operador': operador, 'valor': valor})
        # Parsear y validar restricciones
        self.restricciones = self.parse_restricciones(restricciones_input, param_names)

        # Validar parámetros y resolver modelo
        if st.button("Resolver"):
            if self.validar_parametros(param_names):
                self.construir_modelo()

        if st.button("Salir", key="salir_boton_1"):
            st.write("Has salido de la aplicación.")
            st.stop()

class IP:
    def __init__(self):
        self.elementos = []
        self.parametros = {}
        self.restricciones = []
        self.param_objetivo = ""
        self.tipo_objetivo = None

    def parse_lista(self, texto):
        return [item.strip().replace(" ", "_") for item in texto.split(",") if item.strip()]

    def parse_restricciones(self, restricciones_input, param_names):
        restricciones = []
        operadores_validos = {"≤": "<=", "≥": ">=", "=": "==", "<": "<", ">": ">", "≠": "!="}
        for idx, restr in enumerate(restricciones_input):
            parametro = restr.get('parametro')
            operador = restr.get('operador')
            valor = restr.get('valor')
            if parametro not in param_names:
                st.error(f"Restricción {idx+1}: Parámetro '{parametro}' no reconocido.")
                continue
            if operador not in operadores_validos:
                st.error(f"Restricción {idx+1}: Operador '{operador}' no válido.")
                continue
            try:
                valor = float(valor)
            except ValueError:
                st.error(f"Restricción {idx+1}: Valor '{valor}' no es numérico.")
                continue
            restricciones.append({
                'parametro': parametro,
                'operador': operadores_validos[operador],
                'valor': valor
            })
        return restricciones

    def validar_parametros(self, param_names):
        for nombre_param in param_names:
            valores = self.parametros.get(nombre_param, {})
            if set(valores.keys()) != set(self.elementos):
                st.error(f"El parámetro '{nombre_param}' no tiene valores para todos los elementos.")
                return False
        return True

    def construir_modelo(self):
        model = ConcreteModel()
        model.i = Set(initialize=self.elementos)

        for pname in self.parametros:
            model.add_component(pname, Param(model.i, initialize=self.parametros[pname]))

        model.x = Var(model.i, domain=NonNegativeIntegers)  # tipo entero

        expr_objetivo = sum(getattr(model, self.param_objetivo)[i] * model.x[i] for i in model.i)
        model.objetivo = Objective(expr=expr_objetivo, sense=self.tipo_objetivo)

        model.restricciones = ConstraintList()
        for restr in self.restricciones:
            expr = sum(getattr(model, restr['parametro'])[i] * model.x[i] for i in model.i)
            if restr['operador'] == "<=":
                model.restricciones.add(expr <= restr['valor'])
            elif restr['operador'] == ">=":
                model.restricciones.add(expr >= restr['valor'])
            elif restr['operador'] == "==":
                model.restricciones.add(expr == restr['valor'])
            elif restr['operador'] == "<":
                model.restricciones.add(expr < restr['valor'])
            elif restr['operador'] == ">":
                model.restricciones.add(expr > restr['valor'])
            elif restr['operador'] == "!=":
                model.restricciones.add(expr != restr['valor'])

        solver = SolverFactory('glpk')
        resultado = solver.solve(model)

        if resultado.solver.status == 'ok' and resultado.solver.termination_condition == 'optimal':
            st.success("✅ Optimización completada con éxito.")
            st.markdown(f"**Valor óptimo de la función objetivo: {model.objetivo():.2f}**")
            for i in model.i:
                st.write(f"{i}: {model.x[i]():.2f}")
        else:
            st.error("La optimización no encontró una solución óptima.")

    def interfaz(self):
        st.subheader("📦 Calculadora de Programación Entera")

        # Ejemplo por defecto
        elementos_default = "Caja1, Caja2"
        parametros_default = "Ganancia, Tiempo"
        param_values_default = {
            "Ganancia": {"Caja1": 20, "Caja2": 30},
            "Tiempo": {"Caja1": 4, "Caja2": 6}
        }
        restricciones_default = [
            {"parametro": "Tiempo", "operador": "≤", "valor": 16},
            {"parametro": "Ganancia", "operador": "≥", "valor": 40}
        ]

        elementos_input = st.text_input("Ingrese los nombres de los elementos separados por comas:", value=elementos_default)
        self.elementos = self.parse_lista(elementos_input)

        parametros_input = st.text_input("Ingrese los nombres de los parámetros separados por comas:", value=parametros_default)
        param_names = self.parse_lista(parametros_input)

        st.markdown("### Parámetros por elemento")
        for pname in param_names:
            self.parametros[pname] = {}
            st.markdown(f"#### Parámetro `{pname}`")
            for el in self.elementos:
                default_val = param_values_default.get(pname, {}).get(el, 1.0)
                val = st.number_input(f"{pname}[{el}]", value=default_val, key=f"ip_{pname}_{el}")
                self.parametros[pname][el] = val

        st.markdown("### Definir Función Objetivo")
        self.param_objetivo = st.selectbox("Seleccione el parámetro para la función objetivo:", param_names, key="ip_obj")
        objetivo_input = st.selectbox("Seleccione la función objetivo:", ["Maximizar", "Minimizar"], key="ip_tipo")
        self.tipo_objetivo = maximize if objetivo_input == "Maximizar" else minimize

        st.markdown("### Definir Restricciones")
        num_restr = st.number_input("Cantidad de restricciones:", min_value=1, value=len(restricciones_default), step=1, key="ip_restr_count")
        operadores = ["≤", "≥", "=", "<", ">", "≠"]
        restricciones_input = []

        for idx in range(int(num_restr)):
            with st.expander(f"Restricción {idx+1}"):
                def_param = restricciones_default[idx]["parametro"] if idx < len(restricciones_default) and restricciones_default[idx]["parametro"] in param_names else param_names[0]
                def_op = restricciones_default[idx]["operador"] if idx < len(restricciones_default) else operadores[0]
                def_val = restricciones_default[idx]["valor"] if idx < len(restricciones_default) else 10.0

                parametro = st.selectbox(f"Seleccione el parámetro para la restricción {idx+1}:", param_names, index=param_names.index(def_param) if def_param in param_names else 0, key=f"ip_param_{idx}")
                operador = st.selectbox(f"Seleccione el operador para la restricción {idx+1}:", operadores, index=operadores.index(def_op) if def_op in operadores else 0, key=f"ip_op_{idx}")
                valor = st.number_input(f"Ingrese el valor para la restricción {idx+1}:", value=def_val, key=f"ip_valor_{idx}")
                restricciones_input.append({'parametro': parametro, 'operador': operador, 'valor': valor})

        self.restricciones = self.parse_restricciones(restricciones_input, param_names)

        if st.button("Resolver", key="ip_resolver"):
            if self.validar_parametros(param_names):
                self.construir_modelo()

        if st.button("Salir", key="ip_salir"):
            st.write("Has salido de la sección IP.")
            st.stop()

class NLP:
    def __init__(self):
        self.variables = []
        self.funcion_objetivo = ""
        self.tipo_objetivo = None
        self.restricciones = []

    def parse_lista(self, texto):
        return [v.strip().replace(" ", "_") for v in texto.split(",") if v.strip()]

    def construir_modelo(self):
        model = ConcreteModel()
        model.vars = Var(self.variables, domain=Reals, initialize=1.0)

        try:
            expr_obj = eval(self.funcion_objetivo, {}, {v: model.vars[v] for v in self.variables})
            model.objetivo = Objective(expr=expr_obj, sense=self.tipo_objetivo)
        except Exception as e:
            st.error(f"Error en la función objetivo: {e}")
            return

        model.restricciones = ConstraintList()
        for restr in self.restricciones:
            try:
                lado_izq = eval(restr['expresion'], {}, {v: model.vars[v] for v in self.variables})
                op = restr['operador']
                valor = restr['valor']
                if op == "<=":
                    model.restricciones.add(lado_izq <= valor)
                elif op == ">=":
                    model.restricciones.add(lado_izq >= valor)
                elif op == "==":
                    model.restricciones.add(lado_izq == valor)
                elif op == "<":
                    model.restricciones.add(lado_izq < valor)
                elif op == ">":
                    model.restricciones.add(lado_izq > valor)
                elif op == "!=":
                    model.restricciones.add(lado_izq != valor)
            except Exception as e:
                st.error(f"Error en restricción: {e}")
                return

        solver = SolverFactory('ipopt')
        resultado = solver.solve(model)

        if resultado.solver.status == 'ok' and resultado.solver.termination_condition == 'optimal':
            st.success("✅ Optimización completada con éxito.")
            st.markdown(f"**Valor óptimo de la función objetivo: {model.objetivo():.4f}**")
            for v in self.variables:
                st.write(f"{v} = {model.vars[v]():.4f}")
        else:
            st.error("La optimización no encontró una solución óptima.")

    def interfaz(self):
        st.subheader("📐 Calculadora de Programación No Lineal (NLP)")

        vars_input = st.text_input("Ingrese las variables separadas por coma:", value="x1, x2")
        self.variables = self.parse_lista(vars_input)

        st.markdown("### Función Objetivo")
        self.funcion_objetivo = st.text_input("Ingrese la función objetivo en términos de las variables:", value="80*x1 + 120*x2 - 3*x1**2 - 2*x2**2 - 0.8*x1*x2")
        objetivo_input = st.selectbox("Seleccione el tipo de optimización:", [ "Maximizar", "Minimizar"], key="nlp_tipo")
        self.tipo_objetivo = maximize if objetivo_input == "Maximizar" else minimize

        st.markdown("### Restricciones")
        num_restr = st.number_input("Cantidad de restricciones:", min_value=0, value=1, step=1, key="nlp_num_restr")
        operadores = ["≤", "≥","=", "<", ">", "≠"]
        restricciones_input = []

        for i in range(int(num_restr)):
            with st.expander(f"Restricción {i+1}"):
                expr = st.text_input(f"Expresión de la restricción {i+1} (lado izquierdo):", value="x1**2 + 1.5*x2**2", key=f"nlp_expr_{i}")
                op = st.selectbox(f"Operador:", operadores, key=f"nlp_op_{i}")
                val = st.number_input(f"Valor derecho de la restricción {i+1}:", value=500, key=f"nlp_val_{i}")
                restricciones_input.append({
                    'expresion': expr,
                    'operador': {"≤": "<=", "≥": ">=", "=": "==", "<": "<", ">": ">", "≠": "!="}[op],
                    'valor': val
                })

        self.restricciones = restricciones_input

        if st.button("Resolver", key="nlp_resolver"):
            self.construir_modelo()

        if st.button("Salir", key="nlp_salir"):
            st.write("Has salido de la sección NLP.")
            st.stop()

class MILP:
    def __init__(self):
        self.variables_enteras = []
        self.variables_continuas = []
        self.funcion_objetivo = ""
        self.tipo_objetivo = None
        self.restricciones = []

    def parse_lista(self, texto):
        return [v.strip().replace(" ", "_") for v in texto.split(",") if v.strip()]

    def construir_modelo(self):
        model = ConcreteModel()

        # Crear variables enteras y continuas como atributos del modelo
        for v in self.variables_enteras:
            setattr(model, v, Var(domain=Integers))
        for v in self.variables_continuas:
            setattr(model, v, Var(domain=Reals))

        # Diccionario para acceder fácilmente a todas las variables por nombre
        all_vars = {v: getattr(model, v) for v in self.variables_enteras + self.variables_continuas}

        try:
            expr_obj = eval(self.funcion_objetivo, {}, all_vars)
            model.objetivo = Objective(expr=expr_obj, sense=self.tipo_objetivo)
        except Exception as e:
            st.error(f"Error en la función objetivo: {e}")
            return

        model.restricciones = ConstraintList()
        for restr in self.restricciones:
            try:
                lado_izq = eval(restr['expresion'], {}, all_vars)
                op = restr['operador']
                valor = restr['valor']
                if op == "<=":
                    model.restricciones.add(lado_izq <= valor)
                elif op == ">=":
                    model.restricciones.add(lado_izq >= valor)
                elif op == "==":
                    model.restricciones.add(lado_izq == valor)
                elif op == "<":
                    model.restricciones.add(lado_izq < valor)
                elif op == ">":
                    model.restricciones.add(lado_izq > valor)
                elif op == "!=":
                    model.restricciones.add(lado_izq != valor)
            except Exception as e:
                st.error(f"Error en restricción: {e}")
                return


        solver = SolverFactory('glpk')
        resultado = solver.solve(model)

        if (
            resultado.solver.status == SolverStatus.ok and 
            resultado.solver.termination_condition == TerminationCondition.optimal
        ):
            st.success("✅ Optimización completada con éxito.")
            st.markdown(f"**Valor óptimo de la función objetivo: {model.objetivo():.4f}**")
            for v in all_vars:
                st.write(f"{v} = {all_vars[v]():.4f}")
        else:
            st.error("La optimización no encontró una solución óptima.")
            st.write(f"🔍 Estado del solver: {resultado.solver.status}")
            st.write(f"📌 Condición de terminación: {resultado.solver.termination_condition}")


    def interfaz(self):
        st.subheader("📐 Calculadora de Programación Entera Mixta (MILP)")

        # Ejemplo por defecto
        enteras_default = "x"
        continuas_default = "y, z"
        funcion_objetivo_default = "x + 2*y + 3*z"
        restricciones_default = [
            {"expresion": "x + y", "operador": "<=", "valor": 10},
            {"expresion": "y + z", "operador": ">=", "valor": 5},
            {"expresion": "x", "operador": ">=", "valor":20},
            {"expresion": "y", "operador": ">=", "valor":11},
            {"expresion": "z", "operador": "<=", "valor": 100}
        ]


        enteras_input = st.text_input("Variables enteras (separadas por coma):", value=enteras_default)
        continuas_input = st.text_input("Variables continuas (separadas por coma):", value=continuas_default)

        self.variables_enteras = self.parse_lista(enteras_input)
        self.variables_continuas = self.parse_lista(continuas_input)

        st.markdown("### Función Objetivo")
        self.funcion_objetivo = st.text_input("Ingrese la función objetivo:", value=funcion_objetivo_default)
        objetivo_input = st.selectbox("Tipo de optimización:", ["Maximizar", "Minimizar"], key="milp_tipo")
        self.tipo_objetivo =maximize if objetivo_input == "Maximizar" else minimize

        st.markdown("### Restricciones")
        num_restr = st.number_input("Cantidad de restricciones:", min_value=0, value=len(restricciones_default), step=1, key="milp_num_restr")
        operadores = ["≤", "≥", "=", "<", ">", "≠"]
        restricciones_input = []

        for i in range(int(num_restr)):
            with st.expander(f"Restricción {i+1}"):
                def_expr = restricciones_default[i]["expresion"] if i < len(restricciones_default) else "x + y"
                def_op = restricciones_default[i]["operador"] if i < len(restricciones_default) else operadores[0]
                def_val = restricciones_default[i]["valor"] if i < len(restricciones_default) else 10.0

                expr = st.text_input(f"Expresión {i+1}:", value=def_expr, key=f"milp_expr_{i}")
                op = st.selectbox("Operador:", operadores, index=operadores.index(def_op) if def_op in operadores else 0, key=f"milp_op_{i}")
                val = st.number_input("Valor derecho:", value=def_val, key=f"milp_val_{i}")
                restricciones_input.append({
                    'expresion': expr,
                    'operador': {"≤": "<=", "≥": ">=", "=": "==", "<": "<", ">": ">", "≠": "!="}[op],
                    'valor': val
                })

        self.restricciones = restricciones_input

        if st.button("Resolver", key="milp_resolver"):
            self.construir_modelo()

        if st.button("Salir", key="milp_salir"):
            st.write("Has salido de la sección MILP.")
            st.stop()

class MINLP:
    def __init__(self):
        self.variables_enteras = []
        self.variables_continuas = []
        self.funcion_objetivo = ""
        self.tipo_objetivo = None
        self.restricciones = []

    def parse_lista(self, texto):
        return [v.strip().replace(" ", "_") for v in texto.split(",") if v.strip()]

    def construir_modelo(self):
        model = ConcreteModel()

        # ✅ Combinar todas las variables para indexar
        todas_las_vars = self.variables_enteras + self.variables_continuas
        model.vars = Var(todas_las_vars, domain=Reals)

        # ✅ Cambiar el dominio de las variables enteras
        for v in self.variables_enteras:
            model.vars[v].domain = Integers

        try:
            expr_obj = eval(self.funcion_objetivo, {}, {v: model.vars[v] for v in model.vars})
            model.objetivo = Objective(expr=expr_obj, sense=self.tipo_objetivo)
        except Exception as e:
            st.error(f"Error en la función objetivo: {e}")
            return

        model.restricciones = ConstraintList()
        for restr in self.restricciones:
            try:
                lado_izq = eval(restr['expresion'], {}, {v: model.vars[v] for v in model.vars})
                op = restr['operador']
                valor = restr['valor']
                if op == "<=":
                    model.restricciones.add(lado_izq <= valor)
                elif op == ">=":
                    model.restricciones.add(lado_izq >= valor)
                elif op == "==":
                    model.restricciones.add(lado_izq == valor)
                elif op == "<":
                    model.restricciones.add(lado_izq < valor)
                elif op == ">":
                    model.restricciones.add(lado_izq > valor)
                elif op == "!=":
                    model.restricciones.add(lado_izq != valor)
            except Exception as e:
                st.error(f"Error en restricción: {e}")
                return

        solver = SolverFactory('ipopt') #✅ Cambiar el solver a 'bonmin' en caso de tener problemas con 'ipopt'
        resultado = solver.solve(model)

        if resultado.solver.status == 'ok' and resultado.solver.termination_condition == 'optimal':
            st.success("✅ Optimización completada con éxito.")
            st.markdown(f"**Valor óptimo de la función objetivo: {model.objetivo():.4f}**")
            for v in model.vars:
                st.write(f"{v} = {model.vars[v]():.4f}")
        else:
            st.error("La optimización no encontró una solución óptima.")

    def interfaz(self):
        st.subheader("📐 Calculadora de Programación No Lineal Mixta (MINLP)")

                # ✅ Valores por defecto del caso de prueba
        enteras_input = st.text_input("Variables enteras (separadas por coma):", value="x")
        continuas_input = st.text_input("Variables continuas (separadas por coma):", value="y, z")

        self.variables_enteras = self.parse_lista(enteras_input)
        self.variables_continuas = self.parse_lista(continuas_input)

        st.markdown("### Función Objetivo")
        self.funcion_objetivo = st.text_input(
            "Ingrese la función objetivo:",
            value="x**2 + 2*y**2 + 3*z + x*y"
        )
        objetivo_input = st.selectbox("Tipo de optimización:", [ "Maximizar", "Minimizar"], key="minlp_tipo")
        self.tipo_objetivo = minimize if objetivo_input == "Minimizar" else maximize

        st.markdown("### Restricciones")
        num_restr = st.number_input("Cantidad de restricciones:", min_value=0, value=5, step=1, key="minlp_num_restr")
        operadores = ["≤", "≥", "=", "<", ">", "≠"]
        restricciones_input = []

        # ✅ Restricciones predefinidas
        valores_defecto = [
            ("x + y + z", "≤", 10.0),
            ("x**2 + y", "≥", 2.0),
            ("y + z**2", "≤", 8.0),
            ("x", "≥", 0.0),
            ("y", "≥", 0.0),
        ]
        for i in range(int(num_restr)):
            with st.expander(f"Restricción {i+1}"):
                expr_default, op_default, val_default = valores_defecto[i] if i < len(valores_defecto) else ("", "≤", 0.0)
                expr = st.text_input(f"Expresión {i+1}:", value=expr_default, key=f"minlp_expr_{i}")
                op = st.selectbox("Operador:", operadores, index=operadores.index(op_default), key=f"minlp_op_{i}")
                val = st.number_input("Valor derecho:", value=val_default, key=f"minlp_val_{i}")
                restricciones_input.append({
                    'expresion': expr,
                    'operador': {"≤": "<=", "≥": ">=", "=": "==", "<": "<", ">": ">", "≠": "!="}[op],
                    'valor': val
                })

        self.restricciones = restricciones_input

        if st.button("Resolver", key="minlp_resolver"):
            self.construir_modelo()

        if st.button("Salir", key="minlp_salir"):
            st.write("Has salido de la sección MINLP.")
            st.stop()