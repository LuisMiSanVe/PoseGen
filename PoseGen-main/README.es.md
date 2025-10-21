> [Ver en ingles/See in english](https://github.com/LuisMiSanVe/PoseGen/blob/main/README.md)
# 🧎 PoseGen
[![image](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://aistudio.google.com/app/apikey)
[![image](https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)](https://code.visualstudio.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![image](https://img.shields.io/badge/json-5E5C5C?style=for-the-badge&logo=json&logoColor=white)](https://docs.python.org/es/3/library/json.html)

Generador de poses aleatorias para inspiración de poses de figuras articulables.

## 📝 Explicación de Tecnología
El programa se divide en dos:
- El visor 3D: Usando pyBullet para generar los gráficos en 3D y renderizandolos en un vídeo.
- Menú de Controles: Usando Tkinter para mostrar varias opciones y botones.

Desde el programa puedes indicar el número de articulaciones y este establece unos límites lógicos en los que se pueden mover para dar como resultado poses replicables en figuras articuladas reales.

Para la generación de poses con IA, esta revisa la imagen de referencia e intenta replicar la pose.

## 📋 Prerequisitos
Necesitarás instalar la librería de [Python](https://www.python.org/) que genera los gráficos y los procesa con arrays para convertirlos en video:
```
pip install pybullet numpy pillow google-genai
```
En el caso que este comando falle, pruebe con:
```
py -m pip install pybullet numpy pillow google-genai
```
En caso de usar la generación por IA, tendrás que obtener tu clave de la API de Gemini yendo aqui: [Google AI Studio](https://aistudio.google.com/app/apikey). Asegurate de tener tu sesión de Google abierta, y encontes dale al botón que dice 'Crear clave de API' y sigue los pasos para crear tu proyecto de Google Cloud y conseguir tu clave de API. **Guardala en algún sitio seguro**.
Google permite el uso gratuito de esta API sin añadir ninguna forma de pago, pero con algunas limitaciones.

En Google AI Studio, puedes monitorizar el uso de la IA haciendo clic en 'Ver datos de uso' en la columna de 'Plan' en la tabla con todos tus proyectos. Recomiendo monitorizarla desde la pestaña de 'Cuota y límites del sistema' y ordenando por 'Porcentaje de uso actual', ya que es donde más información obtienes.

## ⚙️ Explicación de uso del proyecto
Para depurar el programa usa `PoseGen.py` del repositorio, ya que este se abre con una consola de depuración.
Puedes activar un contador de FPS para depurar en esta [línea](https://github.com/LuisMiSanVe/PoseGen/blob/main/PoseGen.py#L151)

Para su uso normal, obten `PoseGen.pyw` (solo para Windows) en los [Lanzamientos de Github](https://github.com/LuisMiSanVe/PoseGen/releases).

En el menú superior, puedes guardar o cargar una pose en formato `PoseGen (.psgn)`, usar algunos ajustes del menú de controles y poner la API Key de Gemini.

Desde el visor 3D puedes usar el raton para mover la camara alrededor del modelo y acercar o alejar la cámara.

> [!TIP]
> Debes presionar `Ctrl` + mover/rueda del ratón para modificar la cámara.

Desde los controles, podremos tocar algunos ajustes como cambiar la resolución, límites de FPS, ademas de restaurar la pose inicial, generar una nueva pose o acceder al menu de posiciones personalizadas, en la que manualmente podrás poner la pose que quieras.

Dentro de dicho menú podrás añadir al fondo una imagen de referencia y generar la pose con IA usando la imagen de referencia. 

## 📂 Archivos
Para poder iniciar el programa, deberás tener en la misma capeta que el ejecutable Python, las siguientes carpetas:
- `models/`: Debe tener el modelo 3D base `models/humanoid.urdf`.
- `config/`: Dene tener el archivo de configuración de la clave de la API `config/apikey.env` con dicha clave dentro para usar la función de posar con IA.
- `saves/`: Guarda en un archivo las poses guardadas, de esta manera: `saves/pose1.psgn`.

> [!NOTE]
> El modelo 3D pertenece a los modelos base de pyBullet y todos los créditos son a sus creadores.

## 🎨 Opciones de Personalización
En el menú de controles, puedes personalizar varios ajustes del programa con estas opciones:
- Start/Stop simulation: Deja de mostrar los cambios en la ventana del vídeo*.
- Show/Hide 3D Display: Elije si quieres que se muestre o no la ventana del vídeo 3D.
- Resolution Scale: Cambia la resolución interna del vídeo, por defecto está a la mitad de la nativa, esta opción afecta drásticamente al rendimiento del programa.
- 60 FPS: El refresco del vídeo está capado a 60 FPS, más fluidos, pero necesitan más recursos para mantener la frecuencia.
- 30 FPS: El refresco del vídeo está capado a 30 FPS, menos fluido y menos demandante.

> [!IMPORTANT]
> *: Las modificaciones aplicadas mientras la simulación esta detenida se irán acumulando y se mostrarán una vez de reanude la simulación, esto puede causar cambios no deseados.

## 🚀 Lanzamientos
Una versión será lanzada solo cuando se cumplan los siguientes puntos:\
Nuevas funciones importantes y arreglos de fallos criticos causarán la salida inmediata de una nueva versión, mientras que otros cambios/arreglos menores deberán esperar una semana desde que se incluyeron en el repositorio antes de ser incluidos en la nueva versión, para que otros posibles cambios puedan ser añadidos tambien.
>[!NOTE]
>Estos posibles nuevos cambios no alargarán la espera de la salida de la nueva versión a más de una semana.

El número de la versión seguirá este formato: \
\[Añadido Importante\].\[Añadido Menor\].\[Arreglos de Errores\]

## 💻 Tecnologías usadas
- Lenguaje de programación: [Python](https://www.python.org/)
- Librerías:
  - [pyBullet](https://pypi.org/project/pybullet/) (3.2.7)
  - [numpy](https://pypi.org/project/numpy/) (2.3.3)
  - [PIL](https://pypi.org/project/pillow/) (11.3.0)
  - [Tkinter](https://docs.python.org/es/3.13/library/tkinter.html)
  - [VerticalScrolledFrame class](https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame) (de [Gonzo](https://stackexchange.com/users/294742/gonzo))
- Otros:
  - Google Gemini AI (2.0)
  - [Modelo Humanoide](https://github.com/bulletphysics/bullet3/blob/master/examples/pybullet/gym/pybullet_data/humanoid/humanoid.urdf) (de pyBullet)
- IDE Recomendado: [VS Code](https://code.visualstudio.com/)
