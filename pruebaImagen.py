import cv2

# Variables donde guardaremos los dos puntos
punto1 = None
punto2 = None

# Leer la imagen
imagen = cv2.imread('imagenes/hammer.jpg')

# Función que se ejecuta cuando usamos el ratón sobre la imagen
def onMouse(event, x, y, flags, param):

    global punto1, punto2

    # Si soltamos el botón izquierdo del ratón
    if event == cv2.EVENT_LBUTTONUP:

        # Si todavía no hemos guardado el primer punto
        if punto1 is None:
            punto1 = (x, y)

        # Si ya tenemos el primer punto, guardamos el segundo
        elif punto2 is None:
            punto2 = (x, y)

            # Separar las coordenadas de los dos puntos
            x1 = punto1[0]
            y1 = punto1[1]

            x2 = punto2[0]
            y2 = punto2[1]

            # Dibujar la línea superior
            cv2.line(imagen, (x1, y1), (x2, y1), (0, 0, 255), 2)

            # Dibujar la línea derecha
            cv2.line(imagen, (x2, y1), (x2, y2), (0, 0, 255), 2)

            # Dibujar la línea inferior
            cv2.line(imagen, (x2, y2), (x1, y2), (0, 0, 255), 2)

            # Dibujar la línea izquierda
            cv2.line(imagen, (x1, y2), (x1, y1), (0, 0, 255), 2)
            
            # Actualizar la imagen mostrada
            cv2.imshow('Hammer', imagen)

            # Reiniciar los puntos para poder dibujar otro rectángulo
            punto1 = None
            punto2 = None


# Crear una ventana para mostrar la imagen
cv2.namedWindow('Hammer')

# Detectar los eventos del ratón en la ventana
cv2.setMouseCallback('Hammer', onMouse)

# Mostrar la imagen
cv2.imshow('Hammer', imagen)

# Esperar a que pulsemos una tecla
cv2.waitKey(0)

# Cerrar la ventana
cv2.destroyWindow('Hammer')

# Guardar la imagen con el rectángulo dibujado
cv2.imwrite('imagenes/hammer_rectangulo.jpg', imagen)