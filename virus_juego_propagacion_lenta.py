
import tkinter as tk
from tkinter import messagebox
import random
import json
import os

os.makedirs("partidas", exist_ok=True)
ruta = os.path.join("partidas", "guardado1.txt")


TAM = 6
TAM_CELDA = 50
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
    def __init__(self, root):
        self.root = root
        self.root.title("Virus Spread Challenge")

        self.canvas = tk.Canvas(root, width=TAM*TAM_CELDA, height=TAM*TAM_CELDA)
        self.canvas.pack()

        botones = tk.Frame(self.root)
        botones.pack()
        tk.Button(botones, text="Guardar", command=self.guardar_partida).pack(side="left")
        tk.Button(botones, text="Cargar", command=self.cargar_partida).pack(side="left")

        self.matriz = [[LIBRE for _ in range(TAM)] for _ in range(TAM)]
        fila = random.randint(0, TAM-1)
        col = random.randint(0, TAM-1)
        self.matriz[fila][col] = VIRUS
        self.infectadas = [(fila, col)]

        self.turno_actual = "virus"

        self.canvas.bind("<Button-1>", self.colocar_barrera)
        self.dibujar_matriz()
        self.root.after(1000, self.ejecutar_turno)

    def dibujar_matriz(self):
        self.canvas.delete("all")
        for i in range(TAM):
            for j in range(TAM):
                x1 = j * TAM_CELDA
                y1 = i * TAM_CELDA
                x2 = x1 + TAM_CELDA
                y2 = y1 + TAM_CELDA

                if self.matriz[i][j] == VIRUS:
                    color = "red"
                elif self.matriz[i][j] == BARRERA:
                    color = "black"
                else:
                    color = "white"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

        self.canvas.create_text(10, 10, anchor="nw", font=("Arial", 12),
                                text=f"Turno: {self.turno_actual.capitalize()}")

    def ejecutar_turno(self):
        if self.turno_actual == "virus":
            for fila, col in self.infectadas:
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nf, nc = fila + dx, col + dy
                    if 0 <= nf < TAM and 0 <= nc < TAM:
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

    def colocar_barrera(self, event):
        if self.turno_actual != "jugador":
            return

        fila = event.y // TAM_CELDA
        col = event.x // TAM_CELDA

        if self.matriz[fila][col] == LIBRE:
            self.matriz[fila][col] = BARRERA
            self.turno_actual = "virus"
            self.dibujar_matriz()

            if not self.verificar_fin_juego():
                self.root.after(1000, self.ejecutar_turno)

    def verificar_fin_juego(self):
        libres = any(LIBRE in fila for fila in self.matriz)
        if not libres:
            self.canvas.create_text(TAM*TAM_CELDA//2, TAM*TAM_CELDA//2,
                                    text="¡Perdiste!", font=("Arial", 24), fill="red")
            return True

        puede_propagarse = False
        for fila, col in self.infectadas:
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nf, nc = fila + dx, col + dy
                if 0 <= nf < TAM and 0 <= nc < TAM:
                    if self.matriz[nf][nc] == LIBRE:
                        puede_propagarse = True
                        break
            if puede_propagarse:
                break

        if not puede_propagarse:
            self.canvas.create_text(TAM*TAM_CELDA//2, TAM*TAM_CELDA//2,
                                    text="¡Ganaste!", font=("Arial", 24), fill="green")
            return True

        return False

    def guardar_partida(self):
        if usuario_actual is None:
            return

        nombre = tk.simpledialog.askstring("Guardar partida", "Nombre de la partida:")
        if not nombre:
            return

        dir_usuario = f"partidas_usuario_{usuario_actual}"
        os.makedirs(dir_usuario, exist_ok=True)
        archivo_path = os.path.join(dir_usuario, f"{nombre}.bin")

        with open(archivo_path, "wb") as archivo:
            archivo.write(TAM.to_bytes(2, "big"))
            archivo.write((1).to_bytes(1, "big"))
            for fila in self.matriz:
                numero = fila_a_base3(fila)
                hexadecimal = hex(numero)[2:].zfill((TAM + 1) // 2)
                archivo.write(bytes.fromhex(hexadecimal))

        messagebox.showinfo("Guardado", f"Partida '{nombre}' guardada exitosamente.")

    def cargar_partida(self, nombre_partida):
        dir_usuario = f"partidas_usuario_{usuario_actual}"
        archivo_path = os.path.join(dir_usuario, f"{nombre_partida}.bin")

        try:
            with open(archivo_path, "rb") as archivo:
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
            messagebox.showerror("Error", "No se pudo cargar la partida.")


def login():
    global usuario_actual
    NombreUsuario = entry_usuario.get()
    for user in usuarios:
        if user["user"] == NombreUsuario:
            usuario_actual = user["id"]
            ventana_login.destroy()
            menu_principal()
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

def menu_principal():
    menu = tk.Tk()
    menu.title("Menú Principal")

    tk.Label(menu, text=f"Bienvenido, {usuario_actual}", font=("Arial", 14)).pack(pady=10)

    def nueva_partida():
        menu.destroy()
        ventana_juego = tk.Tk()
        VirusSpreadGame(ventana_juego)
        ventana_juego.mainloop()

    def cargar_partida():
        menu.destroy()
        ventana_cargar_partida()

    tk.Button(menu, text="Nueva Partida", command=nueva_partida, width=20).pack(pady=5)
    tk.Button(menu, text="Cargar Partida", command=cargar_partida, width=20).pack(pady=5)
    tk.Button(menu, text="Salir", command=menu.destroy, width=20).pack(pady=5)

    menu.mainloop()

def ventana_cargar_partida():
    if usuario_actual is None:
        return

    ventana = tk.Toplevel()
    ventana.title("Cargar Partida")

    dir_usuario = f"partidas_usuario_{usuario_actual}"
    os.makedirs(dir_usuario, exist_ok=True)
    archivos = [f[:-4] for f in os.listdir(dir_usuario) if f.endswith(".bin")]

    lista = tk.Listbox(ventana, width=40)
    lista.pack(padx=10, pady=10)

    for partida in archivos:
        lista.insert(tk.END, partida)

    def abrir():
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona una partida.")
            return
        nombre_partida = lista.get(seleccion[0])
        ventana.destroy()
        ventana_juego = tk.Tk()
        juego = VirusSpreadGame(ventana_juego)
        juego.cargar_partida(nombre_partida)
        ventana_juego.mainloop()

    def eliminar():
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona una partida.")
            return
        nombre_partida = lista.get(seleccion[0])
        confirmacion = messagebox.askyesno("Eliminar", f"¿Eliminar partida '{nombre_partida}'?")
        if confirmacion:
            os.remove(os.path.join(dir_usuario, f"{nombre_partida}.bin"))
            lista.delete(seleccion[0])

    tk.Button(ventana, text="Abrir Partida", command=abrir).pack(pady=5)
    tk.Button(ventana, text="Eliminar Partida", command=eliminar).pack(pady=5)


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
