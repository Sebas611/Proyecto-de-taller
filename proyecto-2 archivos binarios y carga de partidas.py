
import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from collections import deque
TAM_CELDA = 30
VIRUS = 1
BARRERA = 2
LIBRE = 0

usuarios = []
data = []
usuario_actual = None

USUARIOS_FILE = "usuarios_virus.json"

def fila_a_base3(fila):
    texto = "".join(str(num) for num in fila)
    return int(texto, 3)


def base3_a_fila(numero, largo):
    base3 = ""
    while numero > 0:
        base3 = str(numero % 3) + base3
        numero = numero // 3
    base3 = base3.zfill(largo)
    return [int(digito) for digito in base3]

class VirusSpreadGame:
    def __init__(self, root, nivel=1, cargar=False):
        self.root = root
        self.root.title("Virus Spread Challenge")
        self.nivel = nivel

        
        self.tam = self.definir_tamano_por_nivel(nivel) if not cargar else None

        
        if not cargar:
            self.tam = self.definir_tamano_por_nivel(nivel)
            self.canvas = tk.Canvas(root, width=self.tam * TAM_CELDA, height=self.tam * TAM_CELDA)
            self.canvas.pack()
            self.inicializar_juego()
        else:
            self.canvas = tk.Canvas(root)  # sin tamaño aún
            self.canvas.pack()


        
        botones = tk.Frame(self.root)
        botones.pack()

        self.entrada_nombre_archivo = tk.Entry(self.root)
        self.entrada_nombre_archivo.pack()

        self.lista_partidas = tk.Listbox(self.root, height=5)
        self.lista_partidas.pack()
        self.actualizar_lista_partidas()
        self.lista_partidas.bind("<<ListboxSelect>>", self.seleccionar_partida_lista)

        tk.Button(botones, text="Guardar", command=self.guardar_partida).pack(side="left")
        tk.Button(botones, text="Cargar", command=self.cargar_partida).pack(side="left")

        self.boton_nivel = tk.Button(root, text="Siguiente Nivel", command=self.subir_nivel, state="disabled")
        self.boton_nivel.pack()

        self.boton_salir = tk.Button(self.root, text="Salir al menú", command=self.salir_al_menu)
        self.boton_salir.pack(pady=10)


        self.canvas.bind("<Button-1>", self.colocar_barrera)

            
    def inicializar_juego(self):
        self.matriz = [[LIBRE for _ in range(self.tam)] for _ in range(self.tam)]
        self.infectadas = []

        cantidad_inicial = min(self.nivel, 5)
        intentos = 0
        while len(self.infectadas) < cantidad_inicial and intentos < 100:
            fila = random.randint(0, self.tam - 1)
            col = random.randint(0, self.tam - 1)
            if self.matriz[fila][col] == LIBRE:
                self.matriz[fila][col] = VIRUS
                self.infectadas.append((fila, col))
            intentos += 1

        self.turno_actual = "virus"
        self.dibujar_matriz()
        self.root.after(1000, self.ejecutar_turno)




    def salir_al_menu(self):
        self.root.destroy()
        mostrar_menu_principal()

    def definir_tamano_por_nivel(self, nivel):
        return min(6 + 2 * (nivel - 1), 20)

    def subir_nivel(self):
        self.nivel += 1
        self.root.destroy()
        nuevo_root = tk.Tk()
        VirusSpreadGame(nuevo_root, self.nivel)
        nuevo_root.mainloop()

    def dibujar_matriz(self):
        self.canvas.delete("all")
        for i in range(self.tam):
            for j in range(self.tam):
                x1 = j * TAM_CELDA
                y1 = i * TAM_CELDA
                x2 = x1 + TAM_CELDA
                y2 = y1 + TAM_CELDA

                color = "white"
                if self.matriz[i][j] == VIRUS:
                    color = "red"
                elif self.matriz[i][j] == BARRERA:
                    color = "black"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

        self.canvas.create_text(10, 10, anchor="nw", font=("Arial", 12),
                                text=f"Turno: {self.turno_actual.capitalize()}")

    def colocar_barrera(self, event):
        if self.turno_actual != "jugador":
            return
        fila = event.y // TAM_CELDA
        col = event.x // TAM_CELDA
        if 0 <= fila < self.tam and 0 <= col < self.tam:
            if self.matriz[fila][col] == LIBRE:
                self.matriz[fila][col] = BARRERA
                if self.crea_isla_valida():
                    self.matriz[fila][col] = LIBRE
                    messagebox.showwarning("Movimiento inválido", "No puedes aislar zonas inaccesibles.")
                else:
                    self.turno_actual = "virus"
                    self.dibujar_matriz()
                    if not self.verificar_fin_juego():
                        self.root.after(1000, self.ejecutar_turno)

    def ejecutar_turno(self):
        if self.turno_actual == "virus":
            for fila, col in self.infectadas:
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nf, nc = fila + dx, col + dy
                    if 0 <= nf < self.tam and 0 <= nc < self.tam:
                        if self.matriz[nf][nc] == LIBRE:
                            self.matriz[nf][nc] = VIRUS
                            self.infectadas.append((nf, nc))
                            self.turno_actual = "jugador"
                            self.dibujar_matriz()
                            if not self.verificar_fin_juego():
                                pass
                            return  # Propaga solo una casilla y termina
            self.turno_actual = "jugador"
            self.dibujar_matriz()
            if not self.verificar_fin_juego():
                pass

    def verificar_fin_juego(self):
        libres = any(LIBRE in fila for fila in self.matriz)
        if not libres:
            self.canvas.create_text(self.tam * TAM_CELDA // 2, self.tam * TAM_CELDA // 2,
                                    
                                    text="¡Perdiste!", font=("Arial", 24), fill="red")
            self.root.after(2000, self.reiniciar_nivel)
            return True

        puede_propagarse = False
        for fila, col in self.infectadas:
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nf, nc = fila + dx, col + dy
                if 0 <= nf < self.tam and 0 <= nc < self.tam:
                    if self.matriz[nf][nc] == LIBRE:
                        puede_propagarse = True
                        break
            if puede_propagarse:
                break

        if not puede_propagarse:
            self.canvas.create_text(self.tam * TAM_CELDA // 2, self.tam * TAM_CELDA // 2,
                                    text="¡Ganaste!", font=("Arial", 24), fill="green")
            messagebox.showinfo("Nivel completado", "¡Felicidades! Has ganado. Puedes avanzar al siguiente nivel.")
            self.boton_nivel.config(state="normal")
            return True

        return False

    def reiniciar_nivel(self):
        self.root.destroy()
        nuevo_root = tk.Tk()
        VirusSpreadGame(nuevo_root, self.nivel)
        nuevo_root.mainloop()





    def crea_isla_valida(self):
        visitado = [[False for _ in range(self.tam)] for _ in range(self.tam)]
        queue = deque(self.infectadas)

        
        for f, c in self.infectadas:
            visitado[f][c] = True

        
        while queue:
            fila, col = queue.popleft()
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nf, nc = fila + dx, col + dy
                if 0 <= nf < self.tam and 0 <= nc < self.tam:
                    if not visitado[nf][nc] and self.matriz[nf][nc] == LIBRE:
                        visitado[nf][nc] = True
                        queue.append((nf, nc))

        
        for i in range(self.tam):
            for j in range(self.tam):
                if self.matriz[i][j] == LIBRE and not visitado[i][j]:
                    
                    for f, c in self.infectadas:
                        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                            nf, nc = f + dx, c + dy
                            if 0 <= nf < self.tam and 0 <= nc < self.tam:
                                if self.matriz[nf][nc] == LIBRE:
                                    return True  
                    return False  

        return False  
    
    def guardar_partida(self):
        nombre_ingresado = self.entrada_nombre_archivo.get().strip()
        if not nombre_ingresado:
            messagebox.showwarning("Nombre requerido", "Por favor, escribe un nombre para guardar la partida.")
            return

        if self.tam is None or not hasattr(self, "matriz"):
            messagebox.showerror("Error", "Debes iniciar o cargar una partida antes de poder guardar.")
            return

        nombre_archivo_binario = f"{nombre_ingresado}.bin"

        try:
            with open(nombre_archivo_binario, "wb") as archivo_bin:
                archivo_bin.write(self.tam.to_bytes(2, "big"))
                archivo_bin.write(self.nivel.to_bytes(1, "big"))

                bytes_por_fila = (self.tam + 1) // 2

                for fila in self.matriz:
                    numero_base3 = fila_a_base3(fila)
                    hex_str = hex(numero_base3)[2:].zfill(bytes_por_fila * 2)  # << Asegura longitud exacta
                    archivo_bin.write(bytes.fromhex(hex_str))

            self.actualizar_lista_partidas()
            messagebox.showinfo("Partida guardada", f"Partida '{nombre_ingresado}' guardada exitosamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la partida:\n{str(e)}")


    def cargar_partida(self):
        nombre_ingresado = self.entrada_nombre_archivo.get().strip()
        if not nombre_ingresado:
            messagebox.showwarning("Nombre requerido", "Por favor, escribe el nombre de la partida a cargar.")
            return

        nombre_archivo_binario = f"{nombre_ingresado}.bin"

        try:
            with open(nombre_archivo_binario, "rb") as archivo_bin:
                tam = int.from_bytes(archivo_bin.read(2), "big")
                nivel = int.from_bytes(archivo_bin.read(1), "big")

                self.matriz = []
                self.infectadas = []

                for i in range(tam):
                    bytes_por_fila = (tam + 1) // 2
                    datos_hex = archivo_bin.read(bytes_por_fila)
                    numero_base3 = int(datos_hex.hex(), 16)
                    fila = base3_a_fila(numero_base3, tam)
                    self.matriz.append(fila)
                    for j, celda in enumerate(fila):
                        if celda == VIRUS:
                            self.infectadas.append((i, j))

                self.turno_actual = "virus"
                self.dibujar_matriz()
                self.root.after(1000, self.ejecutar_turno)

        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró la partida llamada '{nombre_ingresado}'.")
    def cargar_partida_desde_archivo(self, nombre_archivo):
        try:
            with open(nombre_archivo, "rb") as archivo_bin:
                self.tam = int.from_bytes(archivo_bin.read(2), "big")
                self.nivel = int.from_bytes(archivo_bin.read(1), "big")

                self.matriz = []
                self.infectadas = []

                for i in range(self.tam):
                    bytes_por_fila = (self.tam + 1) // 2
                    datos_hex = archivo_bin.read(bytes_por_fila)
                    
                    if not datos_hex or len(datos_hex) != bytes_por_fila:
                        raise ValueError(f"El archivo está dañado o incompleto en la fila {i + 1}.")

                    numero_base3 = int(datos_hex.hex(), 16)
                    fila = base3_a_fila(numero_base3, self.tam)
                    self.matriz.append(fila)
                    for j, celda in enumerate(fila):
                        if celda == VIRUS:
                            self.infectadas.append((i, j))

            self.canvas.config(width=self.tam * TAM_CELDA, height=self.tam * TAM_CELDA)
            self.canvas.delete("all")

            self.turno_actual = "virus"

            
            self.canvas.bind("<Button-1>", self.colocar_barrera)

            
            self.dibujar_matriz()
            self.root.after(1000, self.ejecutar_turno)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la partida:\n{str(e)}")

    def actualizar_lista_partidas(self):
        self.lista_partidas.delete(0, tk.END)
        for archivo in os.listdir():
            if archivo.endswith(".bin"):
                self.lista_partidas.insert(tk.END, archivo[:-4])  

    def seleccionar_partida_lista(self, event):
        seleccion = self.lista_partidas.curselection()
        if seleccion:
            nombre = self.lista_partidas.get(seleccion[0])
            self.entrada_nombre_archivo.delete(0, tk.END)
            self.entrada_nombre_archivo.insert(0, nombre)




    
def login():
    global usuario_actual
    NombreUsuario = entry_usuario.get()
    for user in usuarios:
        if user["user"] == NombreUsuario:
            usuario_actual = user["id"]
            ventana_login.destroy()
            mostrar_menu_principal()  # Aquí en lugar de crear el juego directamente
            return
    messagebox.showerror("Error", "Usuario no encontrado")

def mostrar_menu_principal():
    ventana_menu = tk.Tk()
    ventana_menu.title("Menú Principal")

    def nueva_partida():
        ventana_menu.destroy()
        root = tk.Tk()
        VirusSpreadGame(root)
        root.mainloop()

    def cargar_partida_menu():
        ventana_menu.destroy()
        mostrar_menu_partidas()

    def salir():
        ventana_menu.destroy()

    tk.Label(ventana_menu, text="Bienvenido", font=("Arial", 14)).pack(pady=10)
    tk.Button(ventana_menu, text="Nueva Partida", width=20, command=nueva_partida).pack(pady=5)
    tk.Button(ventana_menu, text="Cargar Partida", width=20, command=cargar_partida_menu).pack(pady=5)
    tk.Button(ventana_menu, text="Salir", width=20, command=salir).pack(pady=5)

    ventana_menu.mainloop()

def mostrar_menu_partidas():
    menu = tk.Tk()
    menu.title("Partidas guardadas")

    tk.Label(menu, text="Selecciona una partida para continuar:").pack()

    lista = tk.Listbox(menu, width=40)
    lista.pack(padx=10, pady=10)

    # Cargar partidas disponibles
    archivos_bin = [f for f in os.listdir() if f.endswith(".bin")]
    for archivo in archivos_bin:
        lista.insert(tk.END, archivo)

    def obtener_seleccion():
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Debes seleccionar una partida.")
            return None
        return lista.get(seleccion[0])

    def cargar():
        nombre_archivo = obtener_seleccion()
        if nombre_archivo:
            menu.destroy()
            ventana = tk.Tk()
            juego = VirusSpreadGame(ventana, cargar=True)
            juego.cargar_partida_desde_archivo(nombre_archivo)
            ventana.mainloop()

    def eliminar():
        nombre_archivo = obtener_seleccion()
        if nombre_archivo:
            os.remove(nombre_archivo)
            lista.delete(lista.curselection()[0])
            messagebox.showinfo("Éxito", f"Partida '{nombre_archivo}' eliminada.")

    def volver():
        menu.destroy()
        mostrar_menu_principal()

    tk.Button(menu, text="Cargar partida", command=cargar).pack(pady=5)
    tk.Button(menu, text="Eliminar partida", command=eliminar).pack(pady=5)
    tk.Button(menu, text="Volver al menú principal", command=volver).pack(pady=5)

    menu.mainloop()


    tk.Label(menu, text="Partidas guardadas:").pack()

    lista = tk.Listbox(menu, width=40)
    lista.pack()

    def obtener_nombre_archivo():
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una partida")
            return None
        return lista.get(seleccion[0])

    def cargar():
        nombre_archivo = obtener_nombre_archivo()
        if nombre_archivo:
            menu.destroy()
            ventana_juego = tk.Tk()
            juego = VirusSpreadGame(ventana_juego)
            juego.cargar_partida_desde_archivo(nombre_archivo)
            ventana_juego.mainloop()

    def eliminar():
        nombre_archivo = obtener_nombre_archivo()
        if nombre_archivo:
            os.remove(nombre_archivo)
            lista.delete(lista.curselection()[0])
            messagebox.showinfo("Eliminado", f"Partida '{nombre_archivo}' eliminada.")

    def nuevo():
        menu.destroy()
        ventana_juego = tk.Tk()
        VirusSpreadGame(ventana_juego)
        ventana_juego.mainloop()

    # Cargar lista de archivos
    prefijo = f"partida_usuario_{usuario_actual}_"
    archivos = [f for f in os.listdir() if f.startswith(prefijo) and f.endswith(".bin")]
    for archivo in archivos:
        lista.insert(tk.END, archivo)

    botones = tk.Frame(menu)
    botones.pack(pady=10)
    tk.Button(botones, text="Cargar partida", command=cargar).pack(side="left", padx=5)
    tk.Button(botones, text="Eliminar partida", command=eliminar).pack(side="left", padx=5)
    tk.Button(botones, text="Nueva partida", command=nuevo).pack(side="left", padx=5)

def signup():
    ventana_signup = tk.Toplevel()
    ventana_signup.title("Registro")

    tk.Label(ventana_signup, text="Nuevo Usuario:").pack()
    entry_nuevo = tk.Entry(ventana_signup)
    entry_nuevo.pack()

    def registrar():
        NombreUsuario = entry_nuevo.get()
        if not NombreUsuario:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return
        for user in usuarios:
            if user["user"] == NombreUsuario:
                messagebox.showerror("Error", "El usuario ya existe")
                return
        Nuevoid = len(usuarios) + 1
        usuarios.append({"id": Nuevoid, "user": NombreUsuario})
        data.append({"user_id": Nuevoid, "chats": []})
        guardar_datos()
        messagebox.showinfo("Registro exitoso", "Usuario creado correctamente")
        ventana_signup.destroy()

    tk.Button(ventana_signup, text="Registrar", command=registrar).pack()

def guardar_datos():
    with open(USUARIOS_FILE, "w") as f:
        json.dump(usuarios, f)

def cargar_datos():
    global usuarios
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r") as f:
            usuarios.extend(json.load(f))

def main():
    global ventana_login, entry_usuario
    cargar_datos()
    ventana_login = tk.Tk()
    ventana_login.title("Login")

    tk.Label(ventana_login, text="Usuario:").pack()
    entry_usuario = tk.Entry(ventana_login)
    entry_usuario.pack()

    tk.Button(ventana_login, text="Login", command=login).pack()
    tk.Button(ventana_login, text="Registrarse", command=signup).pack()

    ventana_login.mainloop()

if __name__ == "__main__":
    main()
