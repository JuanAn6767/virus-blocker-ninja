# 🥷 Virus Blocker Ninja

![Plataformas](https://shields.io)
![Versión](https://shields.io)
![Python](https://shields.io)

**Virus Blocker Ninja** es un antivirus ligero y sigiloso diseñado para detectar, aislar y neutralizar amenazas mediante análisis de firmas digitales y detección heurística.

🌐 **Página Web Oficial de Descarga:** `https://github.io`

---

## 🛡️ Características Principales
* **🔍 Escaneo por Firmas (SHA-256):** Identifica archivos maliciosos conocidos sin saturar la memoria RAM.
* **🧠 Análisis Heurístico:** Detecta técnicas de engaño comunes como dobles extensiones (`.pdf.exe`, `.jpg.exe`) y código ofuscado en scripts.
* **♻️ Cuarentena Reversible:** Neutraliza las amenazas aplicando cifrado XOR y permite restaurar archivos intactos con un solo clic.
* **🥷 Protección en Segundo Plano:** Se minimiza en la bandeja del sistema con notificaciones nativas de estado (*"Estás protegido"*).

---

## 📥 Instalación y Uso

### 🪟 Windows (Instalador Oficial)
1. Ve a la sección **Releases** a la derecha de este repositorio y descarga **`Instalar_VirusBlockerNinja.exe`**.
2. Ejecuta el asistente, elige tu idioma (**Español** o **Inglés**) y la carpeta de destino.
3. *(Nota: Al ser un proyecto independiente, Windows SmartScreen puede mostrar una advertencia; haz clic en **Más información > Ejecutar de todas formas**).*

### 🍎 macOS y 🐧 Linux
1. Descarga el archivo **`antivirus.py`** desde la sección **Releases**.
2. Abre tu terminal en la carpeta de descargas e instala las dependencias visuales:
   ```bash
   pip3 install pystray pillow
   ```
3. Ejecuta el programa:
   ```bash
   python3 antivirus.py
   ```

---
*Desarrollado por **Juan Andrés** © 2026*
