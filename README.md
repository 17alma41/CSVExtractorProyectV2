# CSVExtractorProyect V2

**CSVExtractorProyect V2** es una solución profesional y automatizada para la extracción, filtrado y enmascarado de datos de contacto (emails, redes sociales, teléfonos, etc.) desde archivos CSV y páginas web. El sistema está diseñado para ser robusto, modular y fácil de usar, permitiendo reanudar procesos y controlar errores de forma inteligente.

---

## 🚀 ¿Qué hace este proyecto?
- **Limpia y normaliza** archivos CSV de entrada.
- **Extrae** emails y redes sociales de sitios web usando scraping avanzado y paralelismo automático.
- **Filtra** emails no deseados según listas de exclusión configurables.
- **Genera archivos demo** enmascarados/anónimos para compartir sin exponer datos reales.
- **Registra el estado** de cada archivo y etapa, permitiendo reanudar procesos interrumpidos.
- **Gestiona errores** y logs de forma centralizada y profesional.

---

## 📁 Estructura del proyecto

```
CSVExtractorProyectV2/
├── src/
│   ├── main.py                # Punto de entrada CLI
│   ├── settings.py            # Configuración de rutas y constantes
│   ├── extractor/             # Extracción y limpieza
│   ├── cleaner/               # Filtrado de exclusiones
│   ├── demo/                  # Generación de archivos demo
│   ├── utils/                 # Utilidades y gestión de estado/logs
├── config/                    # Configuración de columnas y exclusiones
├── data/
│   ├── inputs/                # CSV originales
│   ├── clean_inputs/          # CSV normalizados
│   ├── outputs/               # Resultados del scraping
│   ├── exclusions_outputs/    # Resultados tras exclusión
│   └── demo_outputs/          # Archivos demo enmascarados
├── logs/                      # Logs y estado de ejecución
│   ├── procesamiento.log
│   ├── status.json
│   └── error_log.txt
├── requirements.txt           # Dependencias Python
└── README.md                  # Esta documentación
```

---

## ⚙️ Instalación

1. **Clona el repositorio** y entra en la carpeta del proyecto.
2. Instala las dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
   > **Nota:** Asegúrate de tener también `matplotlib` y `Pillow` (se instalan automáticamente con el comando anterior).
3. Asegúrate de tener el driver de Selenium (ej: `chromedriver.exe`) en la carpeta `/drivers`.

---
## ▶️ Instrucciones de uso

1. Agrega los archivos ``.csv`` a la carpeta ``data/inputs``
2. Ejecuta el script principal:
  ```bash
    python src/main.py --all
  ```
4. Seguira el flujo completo ``extracción -> filtrado -> demos``
5. Cada resultado se irá almacenando en su carpeta correspondiente `data/clean_inputs -> data/outputs -> data/exclusions_outputs -> data/demo_outputs`



---

## 🖥️ Uso rápido

### Flujo completo automatizado

```powershell
python src/main.py --all
```

### Opciones principales
- `--all`           Ejecuta todo el flujo: limpieza → scraping → exclusión → demo
- `--extract`       Solo extracción web
- `--filter`        Solo filtrado de exclusiones
- `--demo`          Solo generación de demo
- `--overwrite`     Fuerza reprocesado de archivos ya procesados
- `--test`          Procesa solo 20 filas por archivo (modo prueba)
- `--wait-timeout`  Timeout de espera por página (segundos)
- `--resume`        Reanuda archivos/URLs incompletos o fallidos
- `--clean-logs`    Limpia todos los archivos de la carpeta logs (requiere confirmación)

### Ejemplo de uso avanzado
```powershell
python src/main.py --all --overwrite --test --wait-timeout 15
```

---


## 📝 Sacar información para FicherosDatos

Este script recorre carpetas por país dentro de una ruta en red, localiza archivos Excel, extrae métricas
específicas desde la hoja "statistics" de cada archivo, asocia hasta tres imágenes JPG disponibles, y genera un
archivo resumen en Excel con toda esa información.

- Ejecutalo para aplicar este codigo y obtener los datos en un excel
```bash
  python src/scripts/ficheros_datos.py
```
- Obtendras los resultados en `data/outputs` para poder observarlo.

---

## 🧠 Características avanzadas

- **Reanudación inteligente:** Si el proceso se interrumpe, puedes reanudar exactamente donde quedó con `--resume`.
- **Control de estado:** El progreso de cada archivo y etapa se guarda en `/logs/status.json`.
- **Logs de errores:** Todos los errores se registran en `/logs/error_log.txt` con detalles.
- **Paralelismo automático:** El sistema ajusta el número de hilos según tu hardware.
- **Configuración flexible:** Puedes personalizar columnas, exclusiones y orden en `/config/txt_config/`.

---

## 📝 Personalización y configuración
- Edita los archivos en `/config/txt_config/` para:
  - Eliminar columnas innecesarias
  - Renombrar columnas
  - Definir el orden de columnas
  - Configurar listas de exclusión de emails

---

## 🛠️ Estructura de los módulos principales

- **src/main.py**: CLI principal y orquestador del flujo.
- **src/extractor/**: Extracción web, limpieza y generación de Excel.
- **src/cleaner/**: Filtrado de emails por exclusión.
- **src/demo/**: Enmascarado/anónimo para archivos demo.
- **src/utils/status_manager.py**: Manejo de estado y logs para reanudación y control de errores.

---

## ❓ Preguntas frecuentes

- **¿Puedo reanudar si se corta la luz o hay un error?**
  Sí, ejecuta el mismo comando con `--resume` y el sistema continuará donde se detuvo.
- **¿Cómo limpio los logs y el estado para empezar de cero?**
  Ejecuta: `python src/main.py --clean-logs`
- **¿Puedo personalizar el scraping?**
  Sí, ajusta los parámetros por CLI o edita la configuración en `/config/txt_config/`.

---

## 📄 Licencia
Este proyecto es privado y su uso está restringido a los términos acordados por el propietario.

---







