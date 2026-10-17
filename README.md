# Práctica 1 — Visión por computador

## Descripción

Esta práctica consiste en procesar un vídeo mediante **Python, OpenCV y NumPy**, permitiendo seleccionar manualmente distintas regiones de interés y generar nuevos vídeos a partir de ellas.

El programa admite **regiones rectangulares y circulares**. Cada 20 fotogramas, el vídeo se detiene para que el usuario actualice la posición de las regiones seleccionadas. De esta manera, es posible seguir visualmente elementos que se desplazan por el vídeo, sin utilizar técnicas de seguimiento automático.

## Funcionalidades

### 1. Selección de regiones

En la primera parada del vídeo, el usuario puede definir una o varias regiones mediante el ratón:

- **Rectángulo:** se seleccionan dos esquinas opuestas con dos clics.
- **Círculo:** se selecciona el centro con el primer clic y el radio con el segundo.

El tamaño y la forma de cada región quedan fijados después de la primera selección. En las siguientes paradas, el usuario solo tiene que recolocar cada región haciendo clic en su nueva posición. Se conserva el orden de las regiones para asociar cada una con el mismo elemento a lo largo del vídeo.

### 2. Vídeo con las regiones dibujadas

Se genera **`video_regiones.mp4`**, que contiene los fotogramas originales con los contornos de las regiones seleccionadas dibujados en rojo.

### 3. Vídeo con las regiones ocultas

Se genera **`video_regiones_ocultas.mp4`**, en el que los píxeles pertenecientes a las regiones seleccionadas se sustituyen por negro. El resto de la imagen se mantiene.

### 4. Extracción de regiones

Se genera un vídeo independiente para cada región: **`region_1.mp4`**, **`region_2.mp4`**, etc.

Cada vídeo contiene los recortes correspondientes a una misma región a lo largo de los fotogramas procesados. Aunque la región cambie de posición, sus recortes se siguen guardando en el mismo archivo.

- En las regiones rectangulares, se guarda el recorte delimitado por el rectángulo.
- En las regiones circulares, se guarda un recorte cuadrado que contiene el círculo, con los píxeles exteriores al círculo en negro.

## Controles

Durante las pausas del vídeo se pueden utilizar los siguientes controles:

- **Clic izquierdo:** seleccionar los puntos de una región o colocarla en una nueva posición.
- **Mover el ratón:** previsualizar la región que se está definiendo o recolocando.
- **`r`:** seleccionar una región rectangular durante la primera selección.
- **`o`:** seleccionar una región circular durante la primera selección.
- **`z`:** deshacer la última selección.
- **`m`:** volver a definir o recolocar la última región.
- **`c`:** borrar las selecciones de la parada actual.
- **`Espacio`:** confirmar las regiones y continuar el vídeo.
- **`q`:** finalizar el procesamiento.

En las paradas posteriores a la primera, es necesario volver a colocar todas las regiones definidas inicialmente para continuar.

## Requisitos

- Python 3
- OpenCV (`opencv-python`)
- NumPy

Para instalar las dependencias:

```bash
python -m pip install opencv-python numpy
```

## Ejecución

1. Situar el archivo **`Video Práctica.mp4`** en el directorio de trabajo desde el que se ejecutará el programa, o ajustar la variable `VIDEO_ENTRADA`.
2. Ejecutar el script:

   ```bash
   python practica1.py
   ```

3. En la primera parada, seleccionar las regiones y confirmar con la barra espaciadora.
4. Cada 20 fotogramas, actualizar manualmente la posición de las regiones y continuar.
5. Al terminar el vídeo, se cierran los archivos de salida.

## Archivos de salida

El programa genera los siguientes archivos:

- **`video_regiones.mp4`:** vídeo original con los contornos de las regiones seleccionadas dibujados en rojo.
- **`video_regiones_ocultas.mp4`:** vídeo en el que las regiones seleccionadas aparecen ocultas en negro.
- **`region_1.mp4`, `region_2.mp4`, etc.:** vídeos independientes con los recortes de cada región a lo largo del procesamiento.

Los archivos se guardan en el directorio de trabajo desde el que se ejecuta el programa.

## Consideraciones

- La actualización de las regiones es **manual**: el programa no detecta ni sigue automáticamente los objetos.
- El intervalo entre paradas está configurado mediante `CADA_N_FRAMES = 20`.
- La forma y el tamaño de las regiones se establecen durante la primera selección y se mantienen en las siguientes.
- La correspondencia entre una región y su vídeo de salida depende del **orden de selección**: la primera región se guarda en `region_1.mp4`, la segunda en `region_2.mp4`, etc.
- Si se pulsa `q` antes de llegar al final, el programa termina el procesamiento y cierra los vídeos con los fotogramas procesados hasta ese momento.