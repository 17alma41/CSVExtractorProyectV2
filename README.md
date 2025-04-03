
# 📬 Email & Social Media Extractor

Este proyecto permite **extraer emails y redes sociales** desde sitios web listados en archivos `.csv`. Es ideal para obtener información de contacto de empresas de forma automática.

---

## 🚀 Funcionalidades principales

- ✅ Extracción de **emails** desde el contenido de las webs.
- ✅ Extracción de **redes sociales esenciales**:
  - Facebook
  - Instagram
  - LinkedIn
  - Twitter/X
- ✅ Soporte para **múltiples archivos CSV** de entrada.
- ✅ Modo **demo** para pruebas rápidas.
- ✅ **Paralelización** con `ThreadPoolExecutor` para acelerar el scraping.
- ✅ Estructura modular lista para escalar y mantener.

---

## 🧱 Estructura del proyecto

```
EmailExtractorProyect_Modular/
├── main.py                        # Script principal
├── extractor/
│   ├── email_extractor.py        # Función de extracción de emails con Selenium
│   ├── social_extractor.py       # Extracción de redes sociales esenciales
├── inputs/                       # Archivos CSV con webs a procesar
├── outputs/                      # Resultados generados
└── requirements.txt              # Dependencias del proyecto
```

---

## ⚙️ Requisitos

1. **Python 3.8+**
2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

3. Tener **Google Chrome instalado**.
4. Descargar el **ChromeDriver** que coincida con tu versión de Chrome:
   👉 [https://sites.google.com/chromium.org/driver/](https://sites.google.com/chromium.org/driver/)
5. Añadir `chromedriver.exe` al **PATH de Windows** o dejarlo en la raíz del proyecto.

6. Aqui tienes un video de ejemplo -> https://www.youtube.com/watch?v=jrNZQyhtBM0
---

## 🧪 Modo demo vs completo

Dentro de `main.py` puedes cambiar esta línea:

```python
DEMO_MODE = True
```

- `True` → toma 20 filas.
- `False` → procesa **todos los archivos CSV** completos.

---

## 🛠 Cómo usar

1. Coloca tus archivos `.csv` dentro de la carpeta `inputs/`.
   - El archivo debe tener una columna llamada `website`.

2. Ejecuta el script:

```bash
python main.py
```

3. Se generarán archivos en la carpeta `outputs/`, con nombre como:
```
emails_NombreDelArchivo.csv
```

---

## 📌 Ejemplo de columnas generadas

| website        | emails                 | facebook       | instagram     | linkedin      | twitter       |
|----------------|-------------------------|----------------|---------------|---------------|----------------|
| empresa.com    | contacto@empresa.com    | fb.com/empresa | insta.com/... | linkedin/...  | twitter.com/...|
