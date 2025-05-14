
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
    def __init__(self, root,nivel=1):
        self.root = root
        self.root.title("Virus Spread Challenge")
        self.nivel = nivel

        self.tam = self.definir_tamano_por_nivel(nivel)

        self.canvas = tk.Canvas(root, width=self.tam*TAM_CELDA, height=self.tam*TAM_CELDA)
        self.canvas.pack()

        botones = tk.Frame(self.root)
        botones.pack()
        tk.Button(botones, text="Guardar", command=self.guardar_partida).pack(side="left")
        tk.Button(botones, text="Cargar", command=self.cargar_partida).pack(side="left")

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

        self.canvas.bind("<Button-1>", self.colocar_barrera)
        self.dibujar_matriz()
        self.root.after(1000, self.ejecutar_turno)

        self.boton_nivel = tk.Button(root, text="Siguiente Nivel", command=self.subir_nivel)
        self.boton_nivel.pack()

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
            return True

        return False

    def crea_isla_valida(self):
        visitado = [[False for _ in range(self.tam)] for _ in range(self.tam)]
        queue = deque(self.infectadas)

        # Marcar celdas infectadas como visitadas
        for f, c in self.infectadas:
            visitado[f][c] = True

        # BFS desde las celdas infectadas
        while queue:
            fila, col = queue.popleft()
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nf, nc = fila + dx, col + dy
                if 0 <= nf < self.tam and 0 <= nc < self.tam:
                    if not visitado[nf][nc] and self.matriz[nf][nc] == LIBRE:
                        visitado[nf][nc] = True
                        queue.append((nf, nc))

        # Solo es error si hay celdas vacías inaccesibles Y NO hay virus atrapados completamente
        for i in range(self.tam):
            for j in range(self.tam):
                if self.matriz[i][j] == LIBRE and not visitado[i][j]:
                    # Ahora verificamos si todos los virus están bloqueados
                    for f, c in self.infectadas:
                        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                            nf, nc = f + dx, c + dy
                            if 0 <= nf < self.tam and 0 <= nc < self.tam:
                                if self.matriz[nf][nc] == LIBRE:
                                    return True  # hay al menos un virus que puede avanzar
                    return False  # virus encerrado: se permite la barrera

        return False  # no hay celdas vacías inaccesibles → válid
    def guardar_partida(self):
        if usuario_actual is None:
            return

        nombre = f"partida_usuario_{usuario_actual}.bin"
        with open(nombre, "wb") as archivo:
            archivo.write(self.tam.to_bytes(2, "big"))
            archivo.write((1).to_bytes(1, "big"))
            for fila in self.matriz:
                numero = fila_a_base3(fila)
                hexadecimal = hex(numero)[2:].zfill((self.tam + 1) // 2)
                archivo.write(bytes.fromhex(hexadecimal))

    def cargar_partida(self):
        if usuario_actual is None:
            return

        nombre = f"partida_usuario_{usuario_actual}.bin"
        try:
            with open(nombre, "rb") as archivo:
                tam = int.from_bytes(archivo.read(2), "big")
                nivel = int.from_bytes(archivo.read(1), "big")

                self.matriz = []
                self.infectadas = []

                for i in range(tam):
                    bytes_por_fila = (tam + 1) // 2
                    hexbytes = archivo.read(bytes_por_fila)
                    numero = int(hexbytes.hex(), 16)
                    fila = base3_a_fila(numero, tam)
                    self.matriz.append(fila)
                    for j, celda in enumerate(fila):
                        if celda == VIRUS:
                            self.infectadas.append((i, j))

                self.turno_actual = "virus"
                self.dibujar_matriz()
                self.root.after(1000, self.ejecutar_turno)

        except FileNotFoundError:
            messagebox.showerror("Error", "No hay partida guardada para este usuario.")

def login():
    global usuario_actual
    NombreUsuario = entry_usuario.get()
    for user in usuarios:
        if user["user"] == NombreUsuario:
            usuario_actual = user["id"]
            ventana_login.destroy()
            ventana_juego = tk.Tk()
            VirusSpreadGame(ventana_juego)
            ventana_juego.mainloop()
            return
    messagebox.showerror("Error", "Usuario no encontrado")

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
