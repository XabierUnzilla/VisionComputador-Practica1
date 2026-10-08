import cv2
import numpy as np

# Vídeo de entrada
VIDEO_ENTRADA = 'Video Práctica.mp4'

# Vídeos de salida
VIDEO_SALIDA = 'video_regiones.mp4'    # regiones dibujadas
VIDEO_OCULTO = 'video_oculto.mp4'      # regiones tapadas con un color sólido
PREFIJO_RECORTE = 'region_'            # un vídeo por región: region_1.mp4, ...

# Nombre de la ventana
VENTANA = 'Video'

# Color y grosor de las regiones
COLOR = (0, 0, 255)
GROSOR = 2

# Color con el que se ocultan las regiones
COLOR_OCULTAR = (0, 0, 0)

# Cada cuántos frames se para el vídeo para modificar las regiones
CADA_N_FRAMES = 20

# Puntos de la región que se está dibujando
puntos = []

# Regiones seleccionadas en el tramo actual: cada región es una lista de
# puntos (x, y). Un rectángulo se guarda como sus cuatro esquinas.
regiones = []

# Forma de la primera región, con los puntos relativos a la esquina superior
# izquierda del rectángulo que la contiene. El resto de regiones se colocan
# con esta misma forma y tamaño.
forma = None

# Tamaño (ancho, alto) del rectángulo que contiene la forma
tamano = None

# Frame en el que se definió la forma (mientras estemos en esa parada
# se puede borrar la región y volver a dibujarla)
frameForma = None

# Si es True, la primera región se dibuja como polígono en vez de rectángulo
modoPoligono = False

# Posición actual del ratón, para mostrar dónde quedaría la región
raton = None

# Indica si el vídeo está parado esperando a que se editen las regiones
editando = False

# Frame actual sin nada dibujado
frame = None
numFrame = 0
total = 0


# Rectángulo que contiene una región: (x1, y1, x2, y2)
def limites(region):

    xs = [p[0] for p in region]
    ys = [p[1] for p in region]

    return min(xs), min(ys), max(xs), max(ys)


# Guarda la forma y el tamaño de la primera región
def fijarForma(region):

    global forma, tamano, frameForma

    x1, y1, x2, y2 = limites(region)

    forma = [(x - x1, y - y1) for (x, y) in region]
    tamano = (x2 - x1, y2 - y1)
    frameForma = numFrame


# Región con la forma fijada centrada en (x, y), sin salirse del frame
def regionEn(x, y):

    w, h = tamano
    x1 = min(max(x - w // 2, 0), frame.shape[1] - 1 - w)
    y1 = min(max(y - h // 2, 0), frame.shape[0] - 1 - h)

    return [(x1 + px, y1 + py) for (px, py) in forma]


# Dibuja una región uniendo cada punto con el siguiente mediante líneas
# (el último se une con el primero para cerrarla)
def dibujarRegion(imagen, region, grosor):

    for i in range(len(region)):
        inicio = region[i]
        fin = region[(i + 1) % len(region)]
        cv2.line(imagen, inicio, fin, COLOR, grosor)


# Dibuja sobre una copia del frame las regiones seleccionadas
def dibujarRegiones(imagen):

    resultado = imagen.copy()

    for region in regiones:
        dibujarRegion(resultado, region, GROSOR)

    return resultado


# Devuelve una copia del frame con las regiones rellenas de un color sólido
def ocultarRegiones(imagen):

    resultado = imagen.copy()

    for region in regiones:
        cv2.fillPoly(resultado, [np.array(region, np.int32)], COLOR_OCULTAR)

    return resultado


# Tamaño de los vídeos de recorte (H.264 necesita ancho y alto pares)
def tamanoRecorte():

    return (tamano[0] // 2 * 2, tamano[1] // 2 * 2)


# Recorta del frame el rectángulo que contiene la región y deja en negro
# lo que queda fuera de ella (en un rectángulo no se pierde nada)
def recortarRegion(imagen, region):

    x1, y1, _, _ = limites(region)
    w, h = tamanoRecorte()

    recorte = imagen[y1:y1 + h, x1:x1 + w]

    # Máscara con la región en blanco y el resto en negro
    mascara = np.zeros((h, w), np.uint8)
    relativa = np.array([(x - x1, y - y1) for (x, y) in region], np.int32)
    cv2.fillPoly(mascara, [relativa], 255)

    return cv2.bitwise_and(recorte, recorte, mask=mascara)


# Muestra el frame con las regiones, la región que se está dibujando,
# y la región que se colocaría en la posición del ratón
def mostrar():

    imagen = dibujarRegiones(frame)

    if editando:

        # Puntos de la región que se está dibujando, unidos con líneas
        for i in range(len(puntos)):
            cv2.circle(imagen, puntos[i], 3, COLOR, -1)
            if i > 0:
                cv2.line(imagen, puntos[i - 1], puntos[i], COLOR, 1)

        # En modo polígono, línea desde el último punto hasta el ratón
        if modoPoligono and puntos and raton is not None:
            cv2.line(imagen, puntos[-1], raton, COLOR, 1)

        # Región de forma fija que sigue al ratón
        if forma is not None and raton is not None:
            dibujarRegion(imagen, regionEn(raton[0], raton[1]), 1)

    cv2.imshow(VENTANA, imagen)


# Cierra el polígono que se está dibujando si tiene al menos tres puntos
def cerrarPoligono():

    global puntos

    if len(puntos) >= 3:
        regiones.append(puntos)
        fijarForma(puntos)

    puntos = []


# Función que se ejecuta cuando usamos el ratón sobre la ventana
def onMouse(event, x, y, flags, param):

    global puntos, raton

    if not editando:
        return

    # Al mover el ratón actualizamos la vista previa
    if event == cv2.EVENT_MOUSEMOVE:
        raton = (x, y)
        if forma is not None or puntos:
            mostrar()
        return

    # Clic derecho: borrar la última región que contenga el punto
    if event == cv2.EVENT_RBUTTONUP:
        for i in range(len(regiones) - 1, -1, -1):
            x1, y1, x2, y2 = limites(regiones[i])
            if x1 <= x <= x2 and y1 <= y <= y2:
                regiones.pop(i)
                comprobarForma()
                break

    # Clic izquierdo
    elif event == cv2.EVENT_LBUTTONUP:

        # Si ya hay forma, un clic coloca la región centrada en el ratón
        if forma is not None:
            regiones.append(regionEn(x, y))

        # Modo polígono: cada clic añade un punto
        elif modoPoligono:
            puntos.append((x, y))

        # Modo rectángulo: con el segundo clic se guarda la región
        else:
            puntos.append((x, y))

            if len(puntos) == 2:
                x1, x2 = min(puntos[0][0], x), max(puntos[0][0], x)
                y1, y2 = min(puntos[0][1], y), max(puntos[0][1], y)
                region = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                regiones.append(region)
                fijarForma(region)
                puntos = []

    else:
        return

    mostrar()


# Si se borran todas las regiones en la parada donde se definió la forma,
# se olvida la forma para poder dibujarla otra vez
def comprobarForma():

    global forma, tamano, frameForma

    if not regiones and frameForma == numFrame:
        forma = None
        tamano = None
        frameForma = None


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

# Crear los vídeos de salida con el mismo tamaño y velocidad
# (códec H.264 para que se puedan reproducir en QuickTime y VS Code)
fourcc = cv2.VideoWriter_fourcc(*'avc1')
salida = cv2.VideoWriter(VIDEO_SALIDA, fourcc, fps, (ancho, alto))
oculto = cv2.VideoWriter(VIDEO_OCULTO, fourcc, fps, (ancho, alto))

# Vídeos de recorte, uno por región; se crean cuando aparece la región
# (la región 1 es la primera que se coloca en cada parada, la 2 la segunda...)
recortes = []

# Crear la ventana y detectar los eventos del ratón
cv2.namedWindow(VENTANA)
cv2.setMouseCallback(VENTANA, onMouse)

print('Instrucciones (el vídeo se para cada', CADA_N_FRAMES, 'frames):')
print('  - Primera región: rectángulo con dos clics (esquinas), o pulsa p para')
print('    dibujar un polígono (un clic por punto, Enter para cerrarlo)')
print('  - Su forma y tamaño quedan fijados; después la región sigue al ratón')
print('    y un clic la coloca')
print('  - Clic derecho sobre una región: borrarla')
print('  - z: deshacer el último punto o la última región')
print('  - c: borrar todas las regiones')
print('  - Espacio o n: seguir; las regiones se mantienen los siguientes', CADA_N_FRAMES, 'frames')
print('    (en cada parada se empieza sin regiones)')
print('  - q o Esc: terminar (el resto de frames se guardan sin regiones)')

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
        oculto.write(frame)
        continue

    # Cada CADA_N_FRAMES frames paramos para que el usuario seleccione
    # las regiones del tramo, empezando sin ninguna
    if (numFrame - 1) % CADA_N_FRAMES == 0:

        regiones = []
        puntos = []
        editando = True

        cv2.setWindowTitle(VENTANA, 'Frame ' + str(numFrame) + ' / ' + str(total) + ' - editar regiones')
        mostrar()

        # Esperar a que el usuario pulse una tecla válida
        while True:
            tecla = cv2.waitKey(0) & 0xFF

            # Cambiar entre rectángulo y polígono (antes de fijar la forma)
            if tecla == ord('p'):
                if forma is None:
                    modoPoligono = not modoPoligono
                    puntos = []
                    print('Modo', 'polígono' if modoPoligono else 'rectángulo')
                mostrar()

            # Cerrar el polígono
            elif tecla in (13, 10):
                if modoPoligono and forma is None:
                    cerrarPoligono()
                mostrar()

            # Deshacer el último punto o, si no hay, la última región
            elif tecla == ord('z'):
                if puntos:
                    puntos.pop()
                elif regiones:
                    regiones.pop()
                comprobarForma()
                mostrar()

            # Borrar todas las regiones
            elif tecla == ord('c'):
                regiones = []
                puntos = []
                comprobarForma()
                mostrar()

            elif tecla in (ord(' '), ord('n')):
                # Si se ha quedado un polígono sin cerrar, lo cerramos
                if modoPoligono and forma is None:
                    cerrarPoligono()
                puntos = []
                break

            elif tecla in (ord('q'), 27):
                terminar = True
                break

        editando = False

        if terminar:
            salida.write(frame)
            oculto.write(frame)
            continue

        # Registrar los puntos seleccionados para este tramo
        fin = min(numFrame + CADA_N_FRAMES - 1, total)
        print('Frames', numFrame, 'a', fin, '->', regiones)

    # En el resto de frames solo mostramos el vídeo con las regiones
    else:
        cv2.setWindowTitle(VENTANA, 'Frame ' + str(numFrame) + ' / ' + str(total))
        mostrar()
        cv2.waitKey(1)

    # Guardar el frame con las regiones dibujadas y con las regiones ocultas
    salida.write(dibujarRegiones(frame))
    oculto.write(ocultarRegiones(frame))

    # Guardar el recorte de cada región en su vídeo
    for i in range(len(regiones)):
        if i == len(recortes):
            nombre = PREFIJO_RECORTE + str(i + 1) + '.mp4'
            recortes.append(cv2.VideoWriter(nombre, fourcc, fps, tamanoRecorte()))
        recortes[i].write(recortarRegion(frame, regiones[i]))

# Liberar recursos
captura.release()
salida.release()
oculto.release()
for r in recortes:
    r.release()
cv2.destroyAllWindows()

print('Vídeos guardados:')
print('  -', VIDEO_SALIDA)
print('  -', VIDEO_OCULTO)
for i in range(len(recortes)):
    print('  -', PREFIJO_RECORTE + str(i + 1) + '.mp4')
