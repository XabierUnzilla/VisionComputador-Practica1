import cv2

# Vídeo de entrada y vídeo de salida
VIDEO_ENTRADA = 'Video Práctica.mp4'
VIDEO_SALIDA = 'video_regiones.mp4'

# Nombre de la ventana
VENTANA = 'Video'

# Color y grosor de los rectángulos
COLOR = (0, 0, 255)
GROSOR = 2

# Cada cuántos frames se para el vídeo para modificar las regiones
CADA_N_FRAMES = 20

# Primer punto del rectángulo que se está seleccionando
punto1 = None

# Regiones seleccionadas en el tramo actual: lista de ((x1, y1), (x2, y2))
regiones = []

# Tamaño (ancho, alto) del primer rectángulo; el resto de regiones se
# colocan con este mismo tamaño
tamano = None

# Frame en el que se definió el tamaño (mientras estemos en esa parada
# se puede borrar el rectángulo y volver a dibujarlo con otro tamaño)
frameTamano = None

# Posición actual del ratón, para mostrar dónde quedaría el rectángulo
raton = None

# Indica si el vídeo está parado esperando a que se editen las regiones
editando = False

# Frame actual sin nada dibujado
frame = None


# Rectángulo del tamaño fijado centrado en (x, y), sin salirse del frame
def rectanguloEn(x, y):

    w, h = tamano
    x1 = min(max(x - w // 2, 0), frame.shape[1] - 1 - w)
    y1 = min(max(y - h // 2, 0), frame.shape[0] - 1 - h)

    return ((x1, y1), (x1 + w, y1 + h))


# Dibuja un rectángulo con cuatro líneas a partir de dos esquinas opuestas
def dibujarRectangulo(imagen, p1, p2, grosor):

    # Separar las coordenadas de los dos puntos
    x1 = p1[0]
    y1 = p1[1]

    x2 = p2[0]
    y2 = p2[1]

    # Dibujar la línea superior
    cv2.line(imagen, (x1, y1), (x2, y1), COLOR, grosor)

    # Dibujar la línea derecha
    cv2.line(imagen, (x2, y1), (x2, y2), COLOR, grosor)

    # Dibujar la línea inferior
    cv2.line(imagen, (x2, y2), (x1, y2), COLOR, grosor)

    # Dibujar la línea izquierda
    cv2.line(imagen, (x1, y2), (x1, y1), COLOR, grosor)


# Dibuja sobre una copia del frame las regiones seleccionadas
def dibujarRegiones(imagen):

    resultado = imagen.copy()

    for (p1, p2) in regiones:
        dibujarRectangulo(resultado, p1, p2, GROSOR)

    return resultado


# Muestra el frame con las regiones y, si existe, el primer punto marcado
# o el rectángulo que se colocaría en la posición del ratón
def mostrar():

    imagen = dibujarRegiones(frame)

    if punto1 is not None:
        cv2.circle(imagen, punto1, 3, COLOR, -1)

    if editando and tamano is not None and raton is not None:
        p1, p2 = rectanguloEn(raton[0], raton[1])
        dibujarRectangulo(imagen, p1, p2, 1)

    cv2.imshow(VENTANA, imagen)


# Función que se ejecuta cuando usamos el ratón sobre la ventana
def onMouse(event, x, y, flags, param):

    global punto1, tamano, frameTamano, raton

    if not editando:
        return

    # Al mover el ratón, el rectángulo de tamaño fijo le sigue
    if event == cv2.EVENT_MOUSEMOVE:
        raton = (x, y)
        if tamano is not None:
            mostrar()

    # Si soltamos el botón izquierdo del ratón
    elif event == cv2.EVENT_LBUTTONUP:

        # Si ya hay tamaño, un clic coloca el rectángulo centrado en el ratón
        if tamano is not None:
            regiones.append(rectanguloEn(x, y))

        # Si todavía no hemos guardado el primer punto
        elif punto1 is None:
            punto1 = (x, y)

        # Con el segundo punto se guarda la región y se fija el tamaño
        else:
            x1, x2 = min(punto1[0], x), max(punto1[0], x)
            y1, y2 = min(punto1[1], y), max(punto1[1], y)
            regiones.append(((x1, y1), (x2, y2)))
            tamano = (x2 - x1, y2 - y1)
            frameTamano = numFrame
            punto1 = None

        mostrar()


# Si se borran todas las regiones en la parada donde se definió el tamaño,
# se olvida el tamaño para poder dibujar el rectángulo otra vez
def comprobarTamano():

    global tamano, frameTamano

    if not regiones and frameTamano == numFrame:
        tamano = None
        frameTamano = None


# Abrir el vídeo de entrada
captura = cv2.VideoCapture(VIDEO_ENTRADA)

if not captura.isOpened():
    print('No se ha podido abrir el vídeo', VIDEO_ENTRADA)
    exit()

# Propiedades del vídeo de entrada
ancho = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
alto = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = captura.get(cv2.CAP_PROP_FPS)
total = int(captura.get(cv2.CAP_PROP_FRAME_COUNT))

# Crear el vídeo de salida con el mismo tamaño y velocidad
# (códec H.264 para que se pueda reproducir en QuickTime y VS Code)
fourcc = cv2.VideoWriter_fourcc(*'avc1')
salida = cv2.VideoWriter(VIDEO_SALIDA, fourcc, fps, (ancho, alto))

# Crear la ventana y detectar los eventos del ratón
cv2.namedWindow(VENTANA)
cv2.setMouseCallback(VENTANA, onMouse)

print('Instrucciones (el vídeo se para cada', CADA_N_FRAMES, 'frames):')
print('  - Primer rectángulo: dos clics (esquinas); su tamaño queda fijado')
print('  - Después: el rectángulo sigue al ratón y un clic lo coloca')
print('  - z: borrar la última región')
print('  - c: borrar todas las regiones')
print('  - Espacio o n: seguir; las regiones se mantienen los siguientes', CADA_N_FRAMES, 'frames')
print('    (en cada parada se empieza sin regiones)')
print('  - q o Esc: terminar (el resto de frames se guardan sin regiones)')

numFrame = 0
terminar = False

while True:

    # Leer el siguiente frame
    ok, frame = captura.read()
    if not ok:
        break

    numFrame += 1

    # Si el usuario ha terminado, copiamos el frame tal cual
    if terminar:
        salida.write(frame)
        continue

    # Cada CADA_N_FRAMES frames paramos para que el usuario seleccione
    # las regiones del tramo, empezando sin ninguna
    if (numFrame - 1) % CADA_N_FRAMES == 0:

        regiones = []
        punto1 = None
        editando = True

        cv2.setWindowTitle(VENTANA, 'Frame ' + str(numFrame) + ' / ' + str(total) + ' - editar regiones')
        mostrar()

        # Esperar a que el usuario pulse una tecla válida
        while True:
            tecla = cv2.waitKey(0) & 0xFF

            # Borrar la última región
            if tecla == ord('z'):
                if punto1 is not None:
                    punto1 = None
                elif regiones:
                    regiones.pop()
                comprobarTamano()
                mostrar()

            # Borrar todas las regiones
            elif tecla == ord('c'):
                regiones = []
                punto1 = None
                comprobarTamano()
                mostrar()

            elif tecla in (ord(' '), ord('n')):
                break

            elif tecla in (ord('q'), 27):
                terminar = True
                break

        editando = False

        if terminar:
            salida.write(frame)
            continue

        # Registrar los puntos seleccionados para este tramo
        fin = min(numFrame + CADA_N_FRAMES - 1, total)
        print('Frames', numFrame, 'a', fin, '->', regiones)

    # En el resto de frames solo mostramos el vídeo con las regiones
    else:
        cv2.setWindowTitle(VENTANA, 'Frame ' + str(numFrame) + ' / ' + str(total))
        mostrar()
        cv2.waitKey(1)

    # Guardar el frame con las regiones dibujadas
    salida.write(dibujarRegiones(frame))

# Liberar recursos
captura.release()
salida.release()
cv2.destroyAllWindows()

print('Vídeo guardado en', VIDEO_SALIDA)
