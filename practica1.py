import cv2
import numpy as np

VIDEO_ENTRADA = 'Video Práctica.mp4'
VIDEO_SALIDA = 'video_regiones.mp4'
VIDEO_OCULTO = 'video_regiones_ocultas.mp4'

CADA_N_FRAMES = 20

punto1 = None
regiones = []
tamanos = []
formas = []
formaActual = 'rectangulo'

indiceRegion = 0
editando = False
primeraSeleccion = True
raton = None
frame = None
videosRegiones = []


# Copiar imagen
def copiarImagen(imagen):

    nueva = np.zeros(
        (size[1], size[0], 3),
        dtype=np.uint8
    )

    nueva[:, :] = imagen[:, :]

    return nueva


# Dibujar rectangulo
def dibujarRectangulo(imagen, p1, p2):

    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    cv2.line(imagen, (x1, y1), (x2, y1), (0, 0, 255), 2)
    cv2.line(imagen, (x2, y1), (x2, y2), (0, 0, 255), 2)
    cv2.line(imagen, (x2, y2), (x1, y2), (0, 0, 255), 2)
    cv2.line(imagen, (x1, y2), (x1, y1), (0, 0, 255), 2)


# Dibujar regiones
def dibujarRegiones(imagen):

    for i in range(len(regiones)):

        if formas[i] == 'rectangulo':

            dibujarRectangulo(
                imagen,
                regiones[i][0],
                regiones[i][1]
            )

        else:

            cv2.circle(
                imagen,
                regiones[i][0],
                regiones[i][1],
                (0, 0, 255),
                2
            )


# Colocar rectangulo desde el centro
def rectanguloCentro(x, y, ancho, alto):

    x1 = x - ancho // 2
    y1 = y - alto // 2
    x2 = x1 + ancho
    y2 = y1 + alto

    if x1 < 0:
        x1 = 0
        x2 = ancho

    if y1 < 0:
        y1 = 0
        y2 = alto

    if x2 > size[0]:
        x2 = size[0]
        x1 = x2 - ancho

    if y2 > size[1]:
        y2 = size[1]
        y1 = y2 - alto

    return ((x1, y1), (x2, y2))


# Colocar circulo desde el centro
def circuloCentro(x, y, radio):

    if x - radio < 0:
        x = radio

    if y - radio < 0:
        y = radio

    if x + radio > size[0]:
        x = size[0] - radio

    if y + radio > size[1]:
        y = size[1] - radio

    return ((x, y), radio)


# Mostrar seleccion
def mostrarSeleccion():

    imagen = copiarImagen(frame)
    dibujarRegiones(imagen)

    if punto1 is not None:

        cv2.circle(
            imagen,
            punto1,
            3,
            (0, 0, 255),
            -1
        )

    if primeraSeleccion:

        if punto1 is not None and raton is not None:

            if formaActual == 'rectangulo':

                p1 = (
                    min(punto1[0], raton[0]),
                    min(punto1[1], raton[1])
                )

                p2 = (
                    max(punto1[0], raton[0]),
                    max(punto1[1], raton[1])
                )

                dibujarRectangulo(imagen, p1, p2)

            else:

                dx = raton[0] - punto1[0]
                dy = raton[1] - punto1[1]

                radio = int(
                    (dx * dx + dy * dy) ** 0.5
                )

                cv2.circle(
                    imagen,
                    punto1,
                    radio,
                    (0, 0, 255),
                    2
                )

    else:

        if raton is not None and indiceRegion < len(tamanos):

            if formas[indiceRegion] == 'rectangulo':

                ancho = tamanos[indiceRegion][0]
                alto = tamanos[indiceRegion][1]

                region = rectanguloCentro(
                    raton[0],
                    raton[1],
                    ancho,
                    alto
                )

                dibujarRectangulo(
                    imagen,
                    region[0],
                    region[1]
                )

            else:

                radio = tamanos[indiceRegion][0]

                region = circuloCentro(
                    raton[0],
                    raton[1],
                    radio
                )

                cv2.circle(
                    imagen,
                    region[0],
                    radio,
                    (0, 0, 255),
                    2
                )

    cv2.imshow('Video', imagen)


# Ocultar regiones
def ocultarRegiones(imagen):

    for i in range(len(regiones)):

        if formas[i] == 'rectangulo':

            x1 = regiones[i][0][0]
            y1 = regiones[i][0][1]
            x2 = regiones[i][1][0]
            y2 = regiones[i][1][1]

            imagen[y1:y2, x1:x2] = (0, 0, 0)

        else:

            centro = regiones[i][0]
            radio = regiones[i][1]

            for y in range(
                centro[1] - radio,
                centro[1] + radio
            ):

                for x in range(
                    centro[0] - radio,
                    centro[0] + radio
                ):

                    dx = x - centro[0]
                    dy = y - centro[1]

                    if dx * dx + dy * dy <= radio * radio:
                        imagen[y][x] = (0, 0, 0)


# Raton
def onMouse(event, x, y, flags, param):

    global punto1, indiceRegion, raton

    if editando:

        if event == cv2.EVENT_MOUSEMOVE:

            raton = (x, y)
            mostrarSeleccion()

        elif event == cv2.EVENT_LBUTTONUP:

            if primeraSeleccion:

                if punto1 is None:

                    punto1 = (x, y)
                    raton = (x, y)

                else:

                    if formaActual == 'rectangulo':

                        x1 = min(punto1[0], x)
                        y1 = min(punto1[1], y)
                        x2 = max(punto1[0], x)
                        y2 = max(punto1[1], y)

                        ancho = x2 - x1
                        alto = y2 - y1

                        if ancho % 2 != 0:
                            x2 = x2 - 1
                            ancho = ancho - 1

                        if alto % 2 != 0:
                            y2 = y2 - 1
                            alto = alto - 1

                        if ancho > 0 and alto > 0:

                            regiones.append(
                                ((x1, y1), (x2, y2))
                            )

                            tamanos.append(
                                (ancho, alto)
                            )

                            formas.append(
                                'rectangulo'
                            )

                    else:

                        dx = x - punto1[0]
                        dy = y - punto1[1]

                        radio = int(
                            (dx * dx + dy * dy) ** 0.5
                        )

                        maxRadio = min(
                            punto1[0],
                            punto1[1],
                            size[0] - punto1[0],
                            size[1] - punto1[1]
                        )

                        if radio > maxRadio:
                            radio = maxRadio

                        if radio > 0:

                            regiones.append(
                                (punto1, radio)
                            )

                            tamanos.append(
                                (radio, radio)
                            )

                            formas.append(
                                'circulo'
                            )

                    punto1 = None
                    raton = None

            else:

                if indiceRegion < len(tamanos):

                    if formas[indiceRegion] == 'rectangulo':

                        ancho = tamanos[indiceRegion][0]
                        alto = tamanos[indiceRegion][1]

                        regiones.append(
                            rectanguloCentro(
                                x,
                                y,
                                ancho,
                                alto
                            )
                        )

                    else:

                        radio = tamanos[indiceRegion][0]

                        regiones.append(
                            circuloCentro(
                                x,
                                y,
                                radio
                            )
                        )

                    indiceRegion = indiceRegion + 1
                    raton = None

            mostrarSeleccion()


# Abrir video
videoCapture = cv2.VideoCapture(VIDEO_ENTRADA)

fps = videoCapture.get(cv2.CAP_PROP_FPS)

size = (
    int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
    int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
)

videoWriter = cv2.VideoWriter(
    VIDEO_SALIDA,
    cv2.VideoWriter_fourcc('M', 'P', '4', 'V'),
    fps,
    size
)

videoWriterOculto = cv2.VideoWriter(
    VIDEO_OCULTO,
    cv2.VideoWriter_fourcc('M', 'P', '4', 'V'),
    fps,
    size
)

cv2.namedWindow('Video')
cv2.setMouseCallback('Video', onMouse)


print('r: rectangulo')
print('o: circulo')
print('z: borrar ultima')
print('m: modificar ultima')
print('c: borrar todas')
print('Espacio: continuar')
print('q: salir')


success, frame = videoCapture.read()

numeroFrame = 0
terminar = False


while success and not terminar:

    # Seleccion cada 20 frames
    if numeroFrame % CADA_N_FRAMES == 0:

        if not primeraSeleccion:
            regiones = []
            indiceRegion = 0

        punto1 = None
        raton = None
        editando = True

        mostrarSeleccion()

    
        # Controles con teclas:
            # r -> rectangulo
            # o -> circulo
            # z -> borrar ultima seleccion
            # m -> modificar ultima region
            # c -> borrar todas las selecciones
            # espacio -> continuar
            # q -> salir

        while True:

            tecla = cv2.waitKey(0)

            if tecla == 114 and primeraSeleccion:

                formaActual = 'rectangulo'
                punto1 = None
                raton = None

                print('Rectangulo')

            elif tecla == 111 and primeraSeleccion:

                formaActual = 'circulo'
                punto1 = None
                raton = None

                print('Circulo')

            elif tecla == 122:

                if punto1 is not None:

                    punto1 = None

                elif primeraSeleccion and len(regiones) > 0:

                    regiones = regiones[:-1]
                    tamanos = tamanos[:-1]
                    formas = formas[:-1]

                elif not primeraSeleccion and len(regiones) > 0:

                    regiones = regiones[:-1]
                    indiceRegion = indiceRegion - 1

                mostrarSeleccion()

            elif tecla == 109:

                if primeraSeleccion:

                    if punto1 is not None:

                        punto1 = None
                        raton = None

                    elif len(regiones) > 0:

                        formaActual = formas[-1]

                        regiones = regiones[:-1]
                        tamanos = tamanos[:-1]
                        formas = formas[:-1]

                elif len(regiones) > 0:

                    regiones = regiones[:-1]
                    indiceRegion = indiceRegion - 1
                    raton = None

                mostrarSeleccion()

            elif tecla == 99:

                regiones = []
                punto1 = None
                raton = None

                if primeraSeleccion:

                    tamanos = []
                    formas = []

                else:

                    indiceRegion = 0

                mostrarSeleccion()

            elif tecla == 32:

                if primeraSeleccion:

                    if punto1 is None and len(regiones) > 0:
                        break

                elif len(regiones) == len(tamanos):
                    break

            elif tecla == 113:

                terminar = True
                break


        editando = False

        if terminar:
            break


        # Crear video para cada region
        if primeraSeleccion:

            for i in range(len(tamanos)):

                if formas[i] == 'rectangulo':

                    ancho = tamanos[i][0]
                    alto = tamanos[i][1]

                else:

                    radio = tamanos[i][0]
                    ancho = radio * 2
                    alto = radio * 2

                videosRegiones.append(
                    cv2.VideoWriter(
                        'region_' + str(i + 1) + '.mp4',
                        cv2.VideoWriter_fourcc(
                            'M',
                            'P',
                            '4',
                            'V'
                        ),
                        fps,
                        (ancho, alto)
                    )
                )

            primeraSeleccion = False


    # Guardar regiones
    for i in range(len(regiones)):

        if formas[i] == 'rectangulo':

            x1 = regiones[i][0][0]
            y1 = regiones[i][0][1]
            x2 = regiones[i][1][0]
            y2 = regiones[i][1][1]

            recorte = frame[y1:y2, x1:x2]

        else:

            centro = regiones[i][0]
            radio = regiones[i][1]

            x1 = centro[0] - radio
            y1 = centro[1] - radio
            x2 = centro[0] + radio
            y2 = centro[1] + radio

            recorte = frame[y1:y2, x1:x2]

            recorteCirculo = np.zeros(
                (radio * 2, radio * 2, 3),
                dtype=np.uint8
            )

            recorteCirculo[:, :] = recorte[:, :]

            for y in range(radio * 2):

                for x in range(radio * 2):

                    dx = x - radio
                    dy = y - radio

                    if dx * dx + dy * dy > radio * radio:
                        recorteCirculo[y][x] = (0, 0, 0)

            recorte = recorteCirculo

        videosRegiones[i].write(recorte)


    # Video con regiones
    frameRegiones = copiarImagen(frame)

    dibujarRegiones(frameRegiones)

    videoWriter.write(frameRegiones)

    cv2.imshow(
        'Video',
        frameRegiones
    )


    # Video oculto
    frameOculto = copiarImagen(frame)

    ocultarRegiones(frameOculto)

    videoWriterOculto.write(frameOculto)


    cv2.waitKey(1)

    success, frame = videoCapture.read()

    numeroFrame = numeroFrame + 1


# Cerrar
videoCapture.release()
videoWriter.release()
videoWriterOculto.release()

for videoRegion in videosRegiones:
    videoRegion.release()

cv2.destroyWindow('Video')