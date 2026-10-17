import tkinter as tk
import threading
import queue
import random
import time
from pathlib import Path
 
 
CANTIDAD_VEHICULOS = 10
COLOR_FONDO = "mediumpurple4"
COLOR_PANEL = "purple4"
COLOR_PISTA = "darkorchid4"
COLOR_BOTON = "mediumpurple"
COLOR_BOTON_ACTIVO = "mediumpurple1"
COLORES_VEHICULOS = [
    "red", "deepskyblue", "gold", "limegreen", "orange",
    "hotpink", "cyan", "white", "black", "gray",
]
 
avances = [0.0] * CANTIDAD_VEHICULOS
velocidades = [0.0] * CANTIDAD_VEHICULOS
tiempos = {}
hilos_carrera = []
carrera_en_curso = False
evento_detener = threading.Event()
vehiculo_apostado = 1
factor_velocidad = 1.0
cola_eventos = queue.Queue()
tiempo_inicio = 0.0
 
ventana = tk.Tk()
ventana.title("Carrera de 10 vehículos")
ventana.geometry("1100x750")
ventana.configure(bg=COLOR_FONDO)
 
 
# Genera la imagen de un vehículo.
def crear_vehiculo(color):
    imagen = tk.PhotoImage(width=50, height=25)
    imagen.put(color, to=(5, 8, 45, 18))
    imagen.put(color, to=(15, 3, 35, 10))
    imagen.put("lightblue", to=(18, 4, 24, 9))
    imagen.put("lightblue", to=(26, 4, 32, 9))
    imagen.put("black", to=(10, 17, 18, 24))
    imagen.put("black", to=(34, 17, 42, 24))
    return imagen
 
 
imagenes_vehiculos = [crear_vehiculo(color) for color in COLORES_VEHICULOS]
 
encabezado = tk.Frame(ventana, bg=COLOR_FONDO)
encabezado.pack(fill="x", padx=12, pady=10)
encabezado.grid_columnconfigure(0, weight=1)
encabezado.grid_columnconfigure(2, weight=1)
 
titulo = tk.Label(
    encabezado,
    text="CARRERA DE 10 VEHÍCULOS",
    font=("Arial", 20, "bold"),
    bg=COLOR_FONDO,
    fg="white",
)
titulo.grid(row=0, column=1)
 
icono_umnges = tk.PhotoImage(file=str(Path(__file__).with_name("umnges.png")))
tk.Label(encabezado, image=icono_umnges, bg=COLOR_FONDO).grid(
    row=0, column=2, sticky="e", padx=5
)
 
opciones = tk.Frame(ventana, bg=COLOR_FONDO)
opciones.pack(pady=5)
 
for texto, columna in (("Apuesta:", 0), ("Velocidad:", 2), ("Rondas:", 4)):
    tk.Label(
        opciones, text=texto, bg=COLOR_FONDO, fg="white"
    ).grid(row=0, column=columna, padx=5)
 
selector_apuesta = tk.Spinbox(
    opciones, from_=1, to=10, width=5, bg=COLOR_PANEL, fg="white",
    buttonbackground=COLOR_BOTON, insertbackground="white",
)
selector_apuesta.grid(row=0, column=1, padx=5)
 
 
# Actualiza el factor de velocidad de la carrera.
def cambiar_velocidad(valor):
    global factor_velocidad
    factor_velocidad = float(valor)
 
 
slider_velocidad = tk.Scale(
    opciones,
    from_=1,
    to=5,
    orient="horizontal",
    length=150,
    command=cambiar_velocidad,
    bg=COLOR_FONDO,
    fg="white",
    troughcolor=COLOR_BOTON,
    activebackground=COLOR_BOTON_ACTIVO,
    highlightthickness=0,
)
slider_velocidad.set(1)
slider_velocidad.grid(row=0, column=3, padx=5)

selector_rondas = tk.Spinbox(
    opciones, from_=1, to=20, width=5, bg=COLOR_PANEL, fg="white",
    buttonbackground=COLOR_BOTON, insertbackground="white",
)
selector_rondas.grid(row=0, column=5, padx=5)

contenido = tk.Frame(ventana, bg=COLOR_FONDO)
contenido.pack(fill="both", expand=True, padx=10, pady=10)
 
canvas_pista = tk.Canvas(
    contenido,
    width=740,
    height=430,
    bg=COLOR_PISTA,
    highlightthickness=0,
)
canvas_pista.grid(row=0, column=0, padx=(0, 10), sticky="n")
 
panel_lateral = tk.Frame(contenido, bg=COLOR_FONDO, width=320)
panel_lateral.grid(row=0, column=1, sticky="n")
panel_lateral.grid_propagate(False)
 
panel_resultados = tk.Frame(panel_lateral, bg=COLOR_FONDO)
panel_resultados.pack(pady=5)
 
 
# Dibuja la pista y los vehículos en sus posiciones actuales.
def dibujar_pista():
    canvas_pista.delete("all")
    inicio = 70
    meta = 675
    canvas_pista.create_line(inicio, 20, inicio, 400, fill="white", width=4)
    canvas_pista.create_line(meta, 20, meta, 400, fill="white", width=4)
    canvas_pista.create_text(inicio, 10, text="SALIDA", fill="white")
    canvas_pista.create_text(meta, 10, text="META", fill="white")
 
    for indice in range(CANTIDAD_VEHICULOS):
        posicion_y = 40 + indice * 35
        canvas_pista.create_line(
            inicio, posicion_y + 20, meta, posicion_y + 20,
            fill="thistle",
        )
        canvas_pista.create_text(
            30, posicion_y + 10, text=str(indice + 1), fill="white"
        )
        posicion_x = inicio + avances[indice] * (meta - inicio)
        canvas_pista.create_image(
            posicion_x, posicion_y + 10, image=imagenes_vehiculos[indice]
        )
 
 
# Simula las idas y vueltas de un vehículo y registra su tiempo.
def correr_vehiculo(numero, rondas):
    aleatorio = random.Random()
    distancia = 0.0
    distancia_total = rondas * 2
    velocidad = aleatorio.uniform(0.5, 1.2)
    tiempo_anterior = time.perf_counter()
    tramo_actual = 0
 
    while distancia < distancia_total and not evento_detener.is_set():
        if evento_detener.wait(0.03):
            return
        tiempo_actual = time.perf_counter()
        tiempo_pasado = tiempo_actual - tiempo_anterior
        tiempo_anterior = tiempo_actual
        distancia += velocidad * tiempo_pasado * factor_velocidad
 
        if distancia >= tramo_actual + 1:
            tramo_actual += 1
            velocidad = aleatorio.uniform(0.5, 1.2)
 
        tramo = distancia % 2
        avance = tramo if tramo <= 1 else 2 - tramo
        cola_eventos.put(("avance", numero, avance, velocidad))
 
    if not evento_detener.is_set():
        tiempo_final = time.perf_counter() - tiempo_inicio
        cola_eventos.put(("terminado", numero, tiempo_final))
 
 
# Procesa los avances enviados por los hilos y actualiza la interfaz.
def procesar_cola():
    global carrera_en_curso
    try:
        while True:
            dato = cola_eventos.get_nowait()
            if dato[0] == "avance":
                _, numero, avance, velocidad = dato
                avances[numero - 1] = avance
                velocidades[numero - 1] = velocidad
            elif dato[0] == "terminado":
                _, numero, tiempo_final = dato
                tiempos[numero] = tiempo_final
                avances[numero - 1] = 0.0
                if len(tiempos) == CANTIDAD_VEHICULOS:
                    carrera_en_curso = False
                    mostrar_resultados()
    except queue.Empty:
        pass
 
    dibujar_pista()
    ventana.after(30, procesar_cola)
 
 
# Valida las opciones e inicia un hilo por vehículo.
def iniciar_carrera():
    global vehiculo_apostado, carrera_en_curso
    global avances, velocidades, tiempos, hilos_carrera, tiempo_inicio
 
    if carrera_en_curso:
        return
    try:
        apuesta_nueva = int(selector_apuesta.get())
    except ValueError:
        etiqueta_estado.config(text="Ingresa un número válido para la apuesta.")
        return
    try:
        rondas_nuevas = int(selector_rondas.get())
    except ValueError:
        etiqueta_estado.config(text="Ingresa un número válido de rondas.")
        return
    if not 1 <= rondas_nuevas <= 20:
        etiqueta_estado.config(text="Las rondas deben estar entre 1 y 20.")
        return
    if not 1 <= apuesta_nueva <= CANTIDAD_VEHICULOS:
        etiqueta_estado.config(text="La apuesta debe estar entre 1 y 10.")
        return
 
    vehiculo_apostado = apuesta_nueva
    avances = [0.0] * CANTIDAD_VEHICULOS
    velocidades = [0.0] * CANTIDAD_VEHICULOS
    tiempos = {}
    evento_detener.clear()
    carrera_en_curso = True
    hilos_carrera = []
    tiempo_inicio = time.perf_counter()
    etiqueta_estado.config(text="¡Carrera en curso!")
 
    for numero in range(1, CANTIDAD_VEHICULOS + 1):
        hilo = threading.Thread(
            target=correr_vehiculo, args=(numero, rondas_nuevas), daemon=True
        )
        hilos_carrera.append(hilo)
        hilo.start()
 
    boton_iniciar.config(state="disabled")
    selector_apuesta.config(state="disabled")
    selector_rondas.config(state="disabled")
 
 
# Muestra los tiempos ordenados y el resultado de la apuesta.
def mostrar_resultados():
    for componente in panel_resultados.winfo_children():
        componente.destroy()
 
    tk.Label(
        panel_resultados,
        text="RESULTADOS",
        font=("Arial", 14, "bold"),
        bg=COLOR_FONDO,
        fg="white",
    ).grid(row=0, column=0, columnspan=3, pady=5)
 
    resultados = sorted(tiempos.items(), key=lambda resultado: resultado[1])
    color_fila = "thistle"
    for columna, texto in enumerate(("Posición", "Vehículo", "Tiempo")):
        tk.Label(
            panel_resultados,
            text=texto,
            font=("Arial", 10, "bold"),
            bg=COLOR_PANEL,
            fg="white",
            width=12,
        ).grid(row=1, column=columna)
 
    for indice, (numero, tiempo_final) in enumerate(resultados):
        valores = (str(indice + 1), f"Vehículo {numero}", f"{tiempo_final:.2f} s")
        for columna, valor in enumerate(valores):
            tk.Label(
                panel_resultados,
                text=valor,
                bg=COLOR_FONDO,
                fg=color_fila,
            ).grid(row=indice + 2, column=columna, pady=1)
 
    ganador = resultados[0][0]
    if ganador == vehiculo_apostado:
        mensaje = f"¡Ganaste! El vehículo {ganador} fue el ganador."
        color_mensaje = "palegreen"
    else:
        mensaje = f"No acertaste. Ganó el vehículo {ganador}."
        color_mensaje = "salmon"
 
    tk.Label(
        panel_resultados,
        text=mensaje,
        font=("Arial", 12, "bold"),
        fg=color_mensaje,
        bg=COLOR_FONDO,
    ).grid(row=len(resultados) + 2, column=0, columnspan=3, pady=10)
 
    etiqueta_estado.config(text=mensaje)
    boton_iniciar.config(state="normal")
    selector_apuesta.config(state="normal")
    selector_rondas.config(state="normal")
 
 
boton_iniciar = tk.Button(
    panel_lateral,
    text="INICIAR CARRERA",
    font=("Arial", 12, "bold"),
    command=iniciar_carrera,
    bg=COLOR_BOTON,
    fg="white",
    activebackground=COLOR_BOTON_ACTIVO,
    activeforeground="white",
    width=20,
    relief="flat",
)
boton_iniciar.pack(pady=5)
 
etiqueta_estado = tk.Label(
    panel_lateral,
    text="Listos en la salida",
    bg=COLOR_FONDO,
    fg="white",
    font=("Arial", 10),
)
etiqueta_estado.pack(pady=3)
 
dibujar_pista()
ventana.after(30, procesar_cola)
 
 
ventana.mainloop()