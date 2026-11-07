import hashlib
import os
import socket
import stat
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageDraw
import pystray

FIRMAS_MALWARE = {
    "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f": (
        "EICAR-Test-File"
    ),
}

CARPETA_CUARENTENA = "./cuarentena"


def crear_icono_escudo():
    """Dibuja un ícono de escudo ninja verde para la bandeja del sistema."""
    imagen = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.polygon(
        [(32, 4), (58, 14), (54, 42), (32, 60), (10, 42), (6, 14)],
        fill="#00FF88",
        outline="#121212",
    )
    dibujo.rectangle([(14, 22), (50, 34)], fill="#121212")
    dibujo.ellipse([(20, 25), (26, 31)], fill="#FFFFFF")
    dibujo.ellipse([(38, 25), (44, 31)], fill="#FFFFFF")
    return imagen


def calcular_sha256(ruta_archivo):
    sha256 = hashlib.sha256()
    try:
        with open(ruta_archivo, "rb") as f:
            while bloque := f.read(8192):
                sha256.update(bloque)
        return sha256.hexdigest()
    except (PermissionError, OSError):
        return None


def analisis_heuristico(ruta_archivo):
    nombre = os.path.basename(ruta_archivo).lower()
    extensiones_trampa = [".pdf.exe", ".jpg.exe", ".docx.scr", ".txt.bat"]
    if any(nombre.endswith(ext) for ext in extensiones_trampa):
        return "Heurística: Doble extensión sospechosa"

    try:
        if 0 < os.path.getsize(ruta_archivo) < 1024 * 1024:
            with open(ruta_archivo, "rb") as f:
                contenido = f.read()
                patrones = [
                    b"powershell -enc",
                    b"bash -i >& /dev/tcp/",
                    b"eval(base64_decode(",
                ]
                for patron in patrones:
                    if patron in contenido:
                        return "Heurística: Código ofuscado detectado"
    except (PermissionError, OSError):
        pass
    return None


def poner_en_cuarentena(ruta_archivo, registrar_log):
    os.makedirs(CARPETA_CUARENTENA, exist_ok=True)
    nombre_seguro = os.path.basename(ruta_archivo) + ".quarantine"
    ruta_destino = os.path.join(CARPETA_CUARENTENA, nombre_seguro)

    try:
        with open(ruta_archivo, "rb") as origen, open(
            ruta_destino, "wb"
        ) as destino:
            while bloque := origen.read(8192):
                destino.write(bytes(b ^ 0xAA for b in bloque))

        os.remove(ruta_archivo)
        os.chmod(ruta_destino, stat.S_IREAD)
        registrar_log(f"   🥷 [CUARENTENA] Neutralizado en: {ruta_destino}")
    except Exception as e:
        registrar_log(f"   ❌ [ERROR] No se pudo aislar: {e}")


class VirusBlockerNinjaApp:

    def __init__(self, root):
        self.root = root
        self.root.title("🥷 Virus Blocker Ninja - Protección Activa")
        self.root.geometry("640x480")
        self.root.configure(bg="#121212")

        self.root.protocol("WM_DELETE_WINDOW", self.minimizar_a_bandeja)

        titulo = tk.Label(
            root,
            text="🥷 VIRUS BLOCKER NINJA",
            font=("Segoe UI", 18, "bold"),
            fg="#00FF88",
            bg="#121212",
        )
        titulo.pack(pady=(15, 5))

        subtitulo = tk.Label(
            root,
            text="🛡️ Estás protegido | Escáner activo en segundo plano",
            font=("Segoe UI", 10, "bold"),
            fg="#00FF88",
            bg="#121212",
        )
        subtitulo.pack(pady=(0, 15))

        frame_botones = tk.Frame(root, bg="#121212")
        frame_botones.pack(pady=5)

        btn_escanear = tk.Button(
            frame_botones,
            text="🔍 Escanear Carpeta",
            font=("Segoe UI", 11, "bold"),
            bg="#00FF88",
            fg="#121212",
            activebackground="#00CC6A",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.iniciar_escaneo,
        )
        btn_escanear.pack(side=tk.LEFT, padx=8)

        btn_restaurar = tk.Button(
            frame_botones,
            text="♻️ Restaurar de Cuarentena",
            font=("Segoe UI", 10, "bold"),
            bg="#2B2B2B",
            fg="#FFFFFF",
            activebackground="#444444",
            relief="flat",
            padx=15,
            pady=9,
            cursor="hand2",
            command=self.restaurar_archivo,
        )
        btn_restaurar.pack(side=tk.LEFT, padx=8)

        self.area_log = scrolledtext.ScrolledText(
            root,
            width=72,
            height=16,
            bg="#1E1E1E",
            fg="#E0E0E0",
            font=("Consolas", 9),
            relief="flat",
        )
        self.area_log.pack(padx=20, pady=15)
        self.escribir_log(
            "🛡️ Estás protegido. Si cierras esta ventana, Virus Blocker Ninja"
            " seguirá vigilando en la barra de tareas."
        )

        self.iniciar_tray()

    def iniciar_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("🛡️ Estado: Estás protegido", None, enabled=False),
            pystray.MenuItem(
                "🥷 Abrir Virus Blocker Ninja", self.mostrar_ventana, default=True
            ),
            pystray.MenuItem("❌ Salir completamente", self.salir_app),
        )
        self.tray_icon = pystray.Icon(
            "VirusBlockerNinja",
            crear_icono_escudo(),
            "Virus Blocker Ninja - Estás protegido",
            menu,
        )
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def minimizar_a_bandeja(self):
        self.root.withdraw()
        self.tray_icon.notify(
            "Virus Blocker Ninja sigue activo en segundo plano.",
            "🛡️ Estás protegido",
        )

    def mostrar_ventana(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)

    def salir_app(self, icon=None, item=None):
        self.tray_icon.stop()
        self.root.after(0, self.root.destroy)

    def escribir_log(self, mensaje):
        self.area_log.insert(tk.END, mensaje + "\n")
        self.area_log.see(tk.END)
        self.root.update()

    def iniciar_escaneo(self):
        carpeta = filedialog.askdirectory(
            title="Selecciona la carpeta a escanear"
        )
        if not carpeta:
            return

        self.escribir_log(f"\n🔎 Analizando: {carpeta}...")
        amenazas = 0

        for raiz, _, archivos in os.walk(carpeta):
            if os.path.abspath(CARPETA_CUARENTENA) in os.path.abspath(raiz):
                continue

            for archivo in archivos:
                ruta_completa = os.path.join(raiz, archivo)

                hash_archivo = calcular_sha256(ruta_completa)
                if hash_archivo in FIRMAS_MALWARE:
                    amenazas += 1
                    self.escribir_log(
                        f"⚠️ AMENAZA (Firma): {FIRMAS_MALWARE[hash_archivo]} ->"
                        f" {archivo}"
                    )
                    poner_en_cuarentena(ruta_completa, self.escribir_log)
                    continue

                alerta = analisis_heuristico(ruta_completa)
                if alerta:
                    amenazas += 1
                    self.escribir_log(f"⚠️ AMENAZA ({alerta}) -> {archivo}")
                    poner_en_cuarentena(ruta_completa, self.escribir_log)

        self.escribir_log(
            f"✅ Escaneo completado. Amenazas bloqueadas: {amenazas}"
        )
        if amenazas > 0:
            messagebox.showwarning(
                "Virus Blocker Ninja",
                f"¡Se neutralizaron {amenazas} amenaza(s) en cuarentena!",
            )
        else:
            messagebox.showinfo(
                "Virus Blocker Ninja",
                "Tu carpeta está limpia. No se encontraron amenazas.",
            )

    def restaurar_archivo(self):
        os.makedirs(CARPETA_CUARENTENA, exist_ok=True)
        archivo_cuarentena = filedialog.askopenfilename(
            initialdir=CARPETA_CUARENTENA,
            title="Selecciona el archivo .quarantine a restaurar",
            filetypes=[("Archivos en cuarentena", "*.quarantine")],
        )
        if not archivo_cuarentena:
            return

        carpeta_destino = filedialog.askdirectory(
            title="¿Dónde quieres devolver el archivo restaurado?"
        )
        if not carpeta_destino:
            return

        nombre_original = os.path.basename(archivo_cuarentena).replace(
            ".quarantine", ""
        )
        ruta_final = os.path.join(carpeta_destino, nombre_original)

        try:
            os.chmod(archivo_cuarentena, stat.S_IWRITE | stat.S_IREAD)
            with open(archivo_cuarentena, "rb") as origen, open(
                ruta_final, "wb"
            ) as destino:
                while bloque := origen.read(8192):
                    destino.write(bytes(b ^ 0xAA for b in bloque))

            os.remove(archivo_cuarentena)
            self.escribir_log(
                f"♻️ [RESTAURADO] Archivo devuelto intacto a: {ruta_final}"
            )
            messagebox.showinfo(
                "Restauración exitosa",
                f"El archivo '{nombre_original}' fue restaurado correctamente.",
            )
        except Exception as e:
            self.escribir_log(f"❌ [ERROR] No se pudo restaurar: {e}")


if __name__ == "__main__":
    # Evita que se abran múltiples copias de Virus Blocker Ninja al mismo tiempo
    try:
        candado_instancia = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        candado_instancia.bind(("127.0.0.1", 49152))
    except socket.error:
        sys.exit(0)

    ventana = tk.Tk()
    app = VirusBlockerNinjaApp(ventana)
    ventana.mainloop()
