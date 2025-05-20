
import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from collections import deque
Tamaño_celda = 30
Virus = 1
Barrera = 2
Libre = 0

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
    """clase donde se genera todo el funcionamiento del juego 
    """
    def __init__(self, root, nivel=1, cargar=False):
        """Inicializa la interfaz y el estado del juego Virus.

        Args:
            root (tk.Tk): Ventana principal de la interfaz gráfica donde se dibuja el juego.
    nivel (int, optional): Nivel del juego que se va a iniciar. Defaults to 1.
    cargar (bool, optional): Si es True, se prepara el canvas para cargar una partida existente. Si es False, se inicia una nueva partida.
        """
        self.root = root
        self.root.title("Virus Spread Challenge")
        self.nivel = nivel
        self.root.config(bg="#373737")

        self.tamaño = self.definir_tamano_por_nivel(nivel) if not cargar else None

        if not cargar:
            self.tamaño = self.definir_tamano_por_nivel(nivel)
            self.canvas = tk.Canvas(root, width=self.tamaño * Tamaño_celda, height=self.tamaño * Tamaño_celda)
            self.canvas.pack()
            self.inicializar_juego()
        else:
            self.canvas = tk.Canvas(root)  
            self.canvas.pack()

        botones = tk.Frame(self.root)
        botones.pack()

        self.entrada_nombre_archivo = tk.Entry(self.root)
        self.entrada_nombre_archivo.pack()
        self.entrada_nombre_archivo.config(bg="#919191")

        self.lista_partidas = tk.Listbox(self.root, height=5)
        self.lista_partidas.pack()

        self.actualizar_lista_partidas()
        self.lista_partidas.bind("<<ListboxSelect>>", self.seleccionar_partida_lista)
        self.lista_partidas.config(bg="#919191")
        self.lista_partidas.pack(pady=10)

        tk.Button(botones, text="Guardar", command=self.guardar_partida,bg="#838282").pack(side="left")
        tk.Button(botones, text="Cargar", command=self.cargar_partida,bg="#838282").pack(side="left")

        self.boton_nivel = tk.Button(root, text="Siguiente Nivel", command=self.subir_nivel, state="disabled")
        self.boton_nivel.pack()

        self.boton_salir = tk.Button(self.root, text="Salir al menú", command=self.salir_al_menu,bg="#838282")
        self.boton_salir.pack(pady=10)


        self.canvas.bind("<Button-1>", self.colocar_barrera)
        self.archivo_actual = None
            
    def inicializar_juego(self):
        """Crea una matriz cuadrada de tamaño x llena de celdas libres, 
            y luego selecciona aleatoriamente una cantidad limitada de posiciones 
            para colocar celdas infectadas, según el nivel
        """
        self.matriz = [[Libre for _ in range(self.tamaño)] for _ in range(self.tamaño)]
        self.infectadas = []

        cantidad_inicial = min(self.nivel, 5)
        intentos = 0
        while len(self.infectadas) < cantidad_inicial and intentos < 100:
            fila = random.randint(0, self.tamaño - 1)
            columna = random.randint(0, self.tamaño - 1)
            if self.matriz[fila][columna] == Libre:
                self.matriz[fila][columna] = Virus
                self.infectadas.append((fila, columna))
            intentos += 1

        self.turno_actual = "virus"
        self.dibujar_matriz()
        self.root.after(1000, self.ejecutar_turno)

    def salir_al_menu(self):
        """funcion que elimina la venta del menu
        """
        self.root.destroy()
        mostrar_partidas_menu()

    def definir_tamano_por_nivel(self, nivel):
        """funcion que define el tamaño del uego dependiendo del nivel

        Args:
            nivel (_type_): nivel de juego por donde va el jugador

        Returns:
            _type_: retorna la casilla del juego segun su nivel
        """
        return min(6 + 4 * (nivel - 1), 12)

    def subir_nivel(self):
        """se sube nibel cada vez que el jugador pasa el juego
        """
        self.nivel += 1
        self.root.destroy()
        nuevo_root = tk.Tk()
        VirusSpreadGame(nuevo_root, self.nivel)
        nuevo_root.mainloop()

    def dibujar_matriz(self):
        """crea la matriz en donde se va a jugar, dependiendo del nivel del jugador
        """
        self.canvas.delete("all")
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                x1 = j * Tamaño_celda
                y1 = i * Tamaño_celda
                x2 = x1 + Tamaño_celda
                y2 = y1 + Tamaño_celda

                color = "#808080"
                if self.matriz[i][j] == Virus:
                    color = "#DA0000"
                elif self.matriz[i][j] == Barrera:
                    color = "#0E2134"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#373737")

        self.canvas.create_text(10, 10, anchor="nw", font=("Arial", 12),
                                text=f"Turno: {self.turno_actual.capitalize()}")

    def colocar_barrera(self, event):
        """_summaryColoca una barrera en la celda seleccionada por el jugador si es válida._

        Args:
            event (_type_): Evento del clic que indica la posición del mouse
        """
        if self.turno_actual != "jugador":
            return
        fila = event.y // Tamaño_celda
        columna = event.x // Tamaño_celda
        if 0 <= fila < self.tamaño and 0 <= columna < self.tamaño:
            if self.matriz[fila][columna] == Libre:
                self.matriz[fila][columna] = Barrera
                if self.crea_isla_invalida():
                    self.matriz[fila][columna] = Libre
                    messagebox.showwarning("Movimiento inválido", "No puedes aislar zonas inaccesibles.")
                else:
                    self.turno_actual = "virus"
                    self.dibujar_matriz()
                    self.guardar_progreso_actual()
                    if not self.verificar_fin_juego():
                        self.root.after(1000, self.ejecutar_turno)

    def ejecutar_turno(self):
        """Ejecuta el turno del virus, propagando la infección a celdas vecinas libres o del jugador.
        """
        if self.turno_actual == "virus":
            for fila, columna in self.infectadas:
                for despla_x, despla_y in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nueva_fila, nueva_colu = fila + despla_x, columna + despla_y
                    if 0 <= nueva_fila < self.tamaño and 0 <= nueva_colu < self.tamaño:
                        if self.matriz[nueva_fila][nueva_colu] == Libre:
                            self.matriz[nueva_fila][nueva_colu] = Virus
                            self.infectadas.append((nueva_fila, nueva_colu))
                            self.turno_actual = "jugador"
                            self.dibujar_matriz()
                            if not self.verificar_fin_juego():
                                pass
                            return  
            self.turno_actual = "jugador"
            self.dibujar_matriz()
            if not self.verificar_fin_juego():
                pass

    def verificar_fin_juego(self):
        """verifica si ya el juego se termino, sea victoria o una derrota.

        Returns:
            _type_: _descrTrue si el juego ha terminado, False si aún continúa.iption_
        """
        libres = any(Libre in fila for fila in self.matriz)
        if not libres:
            self.canvas.create_text(self.tamaño * Tamaño_celda // 2, self.tamaño * Tamaño_celda // 2,
                                    
                                    text="¡Perdiste!", font=("Arial", 24), fill="red")
            self.root.after(2000, self.reiniciar)
            return True

        puede_propagarse = False
        for fila, columna in self.infectadas:
            for despla_x, despla_y in [(-1,0), (1,0), (0,-1), (0,1)]:
                nueva_fila, nueva_colu = fila + despla_x, columna + despla_y
                if 0 <= nueva_fila < self.tamaño and 0 <= nueva_colu < self.tamaño:
                    if self.matriz[nueva_fila][nueva_colu] == Libre:
                        puede_propagarse = True
                        break
            if puede_propagarse:
                break

        if not puede_propagarse:
            self.canvas.create_text(self.tamaño * Tamaño_celda // 2, self.tamaño * Tamaño_celda // 2,
                                    text="¡Ganaste!", font=("Arial", 24), fill="green")
            messagebox.showinfo("Nivel completado", "¡Felicidades! Has ganado. Puedes avanzar al siguiente nivel.")
            self.boton_nivel.config(state="normal")
            return True

        return False

    def reiniciar(self):
        """reinicia el juego en el mismo nivel en donde se esta jugando
        """
        self.root.destroy()
        nuevo_root = tk.Tk()
        VirusSpreadGame(nuevo_root, self.nivel)
        nuevo_root.mainloop()

    def crea_isla_invalida(self):
        """verifica si el jugador intenta crear una isla, osea una zona inaccesible.

        Returns:
            _type_: True si existe una zona libre aislada , False si todo está conectado correctamente.
        """
        visitado = [[False for _ in range(self.tamaño)] for _ in range(self.tamaño)]
        isla = deque(self.infectadas)

        for f, c in self.infectadas:
            visitado[f][c] = True

        while isla:
            fila, columna = isla.popleft()
            for despla_x, despla_y in [(-1,0), (1,0), (0,-1), (0,1)]:
                nueva_fila, nueva_colu = fila + despla_x, columna + despla_y
                if 0 <= nueva_fila < self.tamaño and 0 <= nueva_colu < self.tamaño:
                    if not visitado[nueva_fila][nueva_colu] and self.matriz[nueva_fila][nueva_colu] == Libre:
                        visitado[nueva_fila][nueva_colu] = True
                        isla.append((nueva_fila, nueva_colu))

        for i in range(self.tamaño):
            for j in range(self.tamaño):
                if self.matriz[i][j] == Libre and not visitado[i][j]:
                    
                    for f, c in self.infectadas:
                        for despla_x, despla_y in [(-1,0), (1,0), (0,-1), (0,1)]:
                            nueva_fila, nueva_colu = f + despla_x, c + despla_y
                            if 0 <= nueva_fila < self.tamaño and 0 <= nueva_colu < self.tamaño:
                                if self.matriz[nueva_fila][nueva_colu] == Libre:
                                    return True  
                    return False  

        return False  
    
    def guardar_partida(self):
        """se guarda cada partida en archivos binarios, en una carpeta llamada "partidas"
        """
        nombre_ingresado = self.entrada_nombre_archivo.get().strip()
        if not nombre_ingresado:
            messagebox.showwarning("Nombre requerido", "Por favor, escribe un nombre para guardar la partida.")
            return

        if self.tamaño is None or not hasattr(self, "matriz"):
            messagebox.showerror("Error", "Debes iniciar o cargar una partida antes de poder guardar.")
            return
        carpeta = "partidas"
        nombre_archivo_binario = f"{nombre_ingresado}.bin"
        ruta = os.path.join(carpeta, nombre_archivo_binario)
        if os.path.exists(ruta):
            messagebox.showwarning("Nombre ya existente", f"Ya existe una partida llamada '{nombre_ingresado}'. Usa otro nombre.")
            return
        try:
            if not os.path.exists(carpeta):
                os.makedirs(carpeta)

            ruta = os.path.join(carpeta, nombre_archivo_binario)
            with open(ruta, "wb") as archivo_bin:
                archivo_bin.write(self.tamaño.to_bytes(2, "big"))
                archivo_bin.write(self.nivel.to_bytes(1, "big"))

                bytes_por_fila = (self.tamaño + 1) // 2

                for fila in self.matriz:
                    numero_base_3 = fila_a_base3(fila)
                    hex_str = hex(numero_base_3)[2:].zfill(bytes_por_fila * 2) 
                    archivo_bin.write(bytes.fromhex(hex_str))

            self.actualizar_lista_partidas()
            messagebox.showinfo("Partida guardada", f"Partida '{nombre_ingresado}' guardada exitosamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la partida:\n{str(e)}")


    def cargar_partida(self):
        """se cargan las partidas guardadas en la carpeta de "partidas, con el nombre de este"
        """
        nombre_ingresado = self.entrada_nombre_archivo.get().strip()
        if not nombre_ingresado:
            messagebox.showwarning("Nombre requerido", "Por favor, escribe el nombre de la partida a cargar.")
            return

        nombre_archivo_binario = f"{nombre_ingresado}.bin"
        ruta = os.path.join("partidas", nombre_archivo_binario)
        try:
            with open(ruta, "rb") as archivo_bin:
                tamaño = int.from_bytes(archivo_bin.read(2), "big")
                nivel = int.from_bytes(archivo_bin.read(1), "big")

                self.matriz = []
                self.infectadas = []

                for i in range(tamaño):
                    bytes_por_fila = (tamaño + 1) // 2
                    datos_hex = archivo_bin.read(bytes_por_fila)
                    numero_base_3 = int(datos_hex.hex(), 16)
                    fila = base3_a_fila(numero_base_3, tamaño)
                    self.matriz.append(fila)
                    for j, celda in enumerate(fila):
                        if celda == Virus:
                            self.infectadas.append((i, j))

                self.turno_actual = "virus"
                self.dibujar_matriz()
                self.root.after(1000, self.ejecutar_turno)

        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró la partida llamada '{nombre_ingresado}'.")
    
    def guardar_progreso_actual(self):
        """guarda y actualiza el progreso que haya tenido cada persona en cada partida
        """
        if not self.archivo_actual:
            return  

        ruta = os.path.join("partidas", self.archivo_actual)

        with open(ruta, "wb") as archivo_bin:
            archivo_bin.write(self.tamaño.to_bytes(2, "big"))
            archivo_bin.write(self.nivel.to_bytes(1, "big"))

            bytes_por_fila = (self.tamaño + 1) // 2
            for fila in self.matriz:
                numero_base_3 = fila_a_base3(fila)
                hex_str = hex(numero_base_3)[2:].zfill(bytes_por_fila * 2)
                archivo_bin.write(bytes.fromhex(hex_str))

    def cargar_partida_desde_archivo(self, nombre_archivo):
        """Carga una partida desde un archivo binario y restaura el estado del juego.


        Args:
            nombre_archivo (_type_): Nombre del archivo binario que contiene la partida guardada.

        Raises:
            ValueError: posibles dificultades a la hora de guardarlo
        """
        try:

            ruta = os.path.join("partidas", nombre_archivo)
            self.archivo_actual = nombre_archivo
            with open(ruta, "rb") as archivo_bin:
                self.tamaño = int.from_bytes(archivo_bin.read(2), "big")
                self.nivel = int.from_bytes(archivo_bin.read(1), "big")

                self.matriz = []
                self.infectadas = []

                for i in range(self.tamaño):
                    bytes_por_fila = (self.tamaño + 1) // 2
                    datos_hex = archivo_bin.read(bytes_por_fila)
                    
                    if not datos_hex or len(datos_hex) != bytes_por_fila:
                        raise ValueError(f"El archivo está dañado o incompleto en la fila {i + 1}.")

                    numero_base_3 = int(datos_hex.hex(), 16)
                    fila = base3_a_fila(numero_base_3, self.tamaño)
                    self.matriz.append(fila)
                    for j, celda in enumerate(fila):
                        if celda == Virus:
                            self.infectadas.append((i, j))

            self.canvas.config(width=self.tamaño * Tamaño_celda, height=self.tamaño * Tamaño_celda)
            self.canvas.delete("all")

            self.turno_actual = "virus"

            
            self.canvas.bind("<Button-1>", self.colocar_barrera)

            
            self.dibujar_matriz()
            self.root.after(1000, self.ejecutar_turno)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la partida:\n{str(e)}")

    def actualizar_lista_partidas(self):
        """actualiza las partidas guardas, por si se guarda una nueva
        """
        import os 

        carpeta = "partidas"
        self.lista_partidas.delete(0, tk.END)

        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

        for archivo in os.listdir("partidas"):  
            if archivo.endswith(".bin"):
                self.lista_partidas.insert(tk.END, archivo[:-4])

    def seleccionar_partida_lista(self):
        """Selecciona una partida de la lista y la coloca en el campo de entrada.
        """

        seleccion = self.lista_partidas.curselection()
        if seleccion:
            nombre = self.lista_partidas.get(seleccion[0])
            self.entrada_nombre_archivo.delete(0, tk.END)
            self.entrada_nombre_archivo.insert(0, nombre)

def iniciar_sesion():
    """inicia sesion de usuarios ya registrados
    """
    global usuario_actual
    NombreUsuario = entry_usuario.get()
    for user in usuarios:
        if user["user"] == NombreUsuario:
            usuario_actual = user["id"]
            ventana_login.destroy()
            mostrar_partidas_menu()  # Aquí en lugar de crear el juego directamente
            return
    messagebox.showerror("Error", "Usuario no encontrado")

def mostrar_partidas_menu():
    """muestra las partidas en una ventana llamada "menu"
    """
    ventana_menu = tk.Tk()
    ventana_menu.title("Menú Principal")
    ventana_menu.config(bg="#222222")

    def nueva_partida():
        """Inicia una nueva partida desde cero en la interfaz
        """
        ventana_menu.destroy()
        root = tk.Tk()
        VirusSpreadGame(root)
        root.mainloop()

    def cargar_partida_menu():
        """carga las partidas del menu
        """
        ventana_menu.destroy()
        mostrar_menu_partidas()
        

    def salir():
        """sale de la ventana
        """
        ventana_menu.destroy()

    tk.Label(ventana_menu, text="Bienvenido", font=("Arial", 14),bg="#717171",fg="#000000").pack(pady=10)
    tk.Button(ventana_menu, text="Nueva Partida", width=20, command=nueva_partida,bg="#838282").pack(pady=5)
    tk.Button(ventana_menu, text="Cargar Partida", width=20, command=cargar_partida_menu,bg="#838282").pack(pady=5)
    tk.Button(ventana_menu, text="Salir", width=20, command=salir,bg="#838282").pack(pady=5)

    ventana_menu.mainloop()

def mostrar_menu_partidas():
    """muestra las partidas bien actualizadas

    Returns:
        _type_: _description_
    """
    import os
    menu = tk.Tk()
    menu.title("Partidas guardadas")
    menu.config(bg="#222222")

    tk.Label(menu, text="Selecciona una partida para continuar", bg="#717171", fg="#000000").pack()
    lista = tk.Listbox(menu, width=40)
    lista.pack(padx=10, pady=10)
    lista.config(bg="#919191")

    carpeta = "partidas"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    archivos_bin = [f for f in os.listdir(carpeta) if f.endswith(".bin")]
    for archivo in archivos_bin:
        lista.insert(tk.END, archivo[:-4])  # Mostrar sin .bin

    def obtener_seleccion():
        """comprueba la partida que se esta seleccionando

        Returns:
            _type_: la partida seleccionada
        """
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Debes seleccionar una partida.")
            return None
        return lista.get(seleccion[0])

    def cargar():
        """Carga una partida seleccionada desde la interfaz de lista de partidas
        """
        nombre_archivo = obtener_seleccion()
        if nombre_archivo:
            menu.destroy()
            ventana = tk.Tk()
            juego = VirusSpreadGame(ventana, cargar=True)
            juego.cargar_partida_desde_archivo(nombre_archivo + ".bin")  # solo nombre + extensión
            ventana.mainloop()
    def eliminar():
        """elimina una partida guardada
        """
        nombre_archivo = obtener_seleccion()
        if nombre_archivo:
            ruta = os.path.join("partidas", nombre_archivo + ".bin")
            if os.path.exists(ruta):
                os.remove(ruta)
                lista.delete(lista.curselection()[0])
                messagebox.showinfo("Éxito", f"Partida '{nombre_archivo}' eliminada.")
            else:
                messagebox.showerror("Error", f"No se encontró el archivo: {ruta}")


    def volver():
        """Cierra la ventana actual y vuelve al menú principal de partidas.

        """
        menu.destroy()
        mostrar_partidas_menu()

    tk.Button(menu, text="Cargar partida", command=cargar,bg="#838282").pack(pady=5)
    tk.Button(menu, text="Eliminar partida", command=eliminar,bg="#838282").pack(pady=5)
    tk.Button(menu, text="Volver al menú principal", command=volver,bg="#838282").pack(pady=5)

    menu.mainloop()

def registrar():
    """registra nuevos usuarios en la interfaz
    """
    ventana_signup = tk.Toplevel()
    ventana_signup.title("Registro")
    ventana_signup.config(bg="#474747")

    tk.Label(ventana_signup, text="Nuevo Usuario:",bg="#919191").pack()
    entry_nuevo = tk.Entry(ventana_signup)
    entry_nuevo.pack()
    entry_nuevo.config(bg="#919191")

    def registrar():
        """registra nuevos usarios que no estaban antes
        """
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

    tk.Button(ventana_signup, text="Registrar", command=registrar,bg="#919191").pack()

def guardar_datos():
    """Guarda la lista de usuarios en un archivo JSON.
    """
    with open(USUARIOS_FILE, "w") as f:
        json.dump(usuarios, f)

def cargar_datos():
    """Carga la lista de usuarios desde un archivo JSON si existe.
    """
    global usuarios
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r") as f:
            usuarios.extend(json.load(f))

def main():
    """ventana principal del juego
    """
    global ventana_login, entry_usuario
    cargar_datos()
    ventana_login = tk.Tk()
    ventana_login.title("Login")
    ventana_login.config(bg="#474747")

    tk.Label(ventana_login, text="Usuario:", font=("Arial", 10),bg="#919191",fg="#000000").pack()
    entry_usuario = tk.Entry(ventana_login)
    entry_usuario.pack()
    entry_usuario.config(bg="#919191")

    tk.Button(ventana_login, text="Login", command=iniciar_sesion,bg="#9E9E9E").pack()
    tk.Button(ventana_login, text="Registrarse", command=registrar,bg="#9E9E9E").pack()

    ventana_login.mainloop()

if __name__ == "__main__":
    main()
