# =============================================================
#  ATRAPA MONEDAS
#  Mueve la bolita con las flechas, corre con Shift (gasta stamina)
#  y atrapa todas las monedas que puedas antes de que se acabe el tiempo.
#  Version 1.0, 2026-11-16
# =============================================================

import pygame  # librería para hacer juegos (ventana, dibujos, teclado...)
import random  # para números al azar (posición de la moneda)
import math  # para calcular distancias (math.hypot)

pygame.init()  # arranca pygame (y su cronómetro interno)

# -------------------------------------------------------------
#  CONSTANTES (en MAYÚSCULAS porque nunca cambian, como "final" en Java)
# -------------------------------------------------------------
ANCHO, ALTO = 800, 600  # tamaño de la ventana en píxeles
RADIO = 20  # tamaño (radio) del jugador
MONEDA_COLOR = (255, 215, 0)  # dorado, en formato (rojo, verde, azul)
RADIO_MONEDA = 10  # tamaño (radio) de la moneda
STAMINA_MAX = 100  # stamina máxima del jugador
TIEMPO_LIMITE = 30  # segundos que dura cada partida
ALTO_HUD = 100  # alto de la franja de arriba (textos y barra)
BARRA_STAMINA_ANCHO = 200  # ancho de la barra de stamina cuando está llena
BARRA_STAMINA_ALTO = 15  # alto de la barra de stamina
BARRA_FONDO_COLOR = (80, 80, 80)  # gris: el "fondo" de la barra
DESCRIPCION = [
    "Flechas: mover",
    "Shift: correr (gasta stamina)",
    "Atrapa todas las monedas antes de que se acabe el tiempo",
]
YDESC_TEXTO = 380
# Colores del jugador y de la barra según la stamina (tipo semáforo)
COLOR_STAMINA_ALTA = (0, 255, 0)  # verde
COLOR_STAMINA_MEDIA = (255, 255, 0)  # amarillo
COLOR_STAMINA_BAJA = (255, 0, 0)  # rojo

# -------------------------------------------------------------
#  VARIABLES (en minúsculas porque SÍ cambian durante el juego)
# -------------------------------------------------------------
stamina_jugador = STAMINA_MAX  # empieza con la stamina llena
puntos = 0  # monedas atrapadas

# -------------------------------------------------------------
#  VENTANA Y HERRAMIENTAS (se crean UNA sola vez, antes del while)
# -------------------------------------------------------------
pantalla = pygame.display.set_mode((ANCHO, ALTO))  # crea la ventana
pygame.display.set_caption("Circulo que se mueve con las flechitas")  # título
reloj = pygame.time.Clock()  # controla la velocidad del juego (FPS)
fuente = pygame.font.Font(None, 36)  # letra por defecto, tamaño 36
titulo_fuente = pygame.font.Font(None, 72)  # letra por defecto, tamaño 72


# Posición inicial del jugador: el centro de la pantalla
x, y = ANCHO // 2, ALTO // 2

# Posición inicial de la moneda: al azar, pero DEBAJO del HUD
# y sin salirse de los bordes (por eso se suma/resta el radio)
moneda_x = random.randint(RADIO_MONEDA, ANCHO - RADIO_MONEDA)
moneda_y = random.randint(ALTO_HUD + RADIO_MONEDA, ALTO - RADIO_MONEDA)


# =============================================================
#  BUCLE DEL JUEGO: se repite unas 60 veces por segundo
#  En cada vuelta: 1) eventos  2) lógica  3) dibujo
# =============================================================
corriendo = True
estado = "menu"

while corriendo:
    # ---------------------------------------------------------
    #  1. EVENTOS
    # ---------------------------------------------------------

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:  # si le dan a la X de la ventana
            corriendo = False  # el while termina y el juego se cierra

    # Qué teclas están apretadas en este momento
    teclas = pygame.key.get_pressed()

    if estado == "menu":
        parpadeo = (pygame.time.get_ticks() // 500) % 2
        pantalla.fill((0, 0, 0))  # fondo negro
        titulo = titulo_fuente.render("CIRCULO QUE SE MUEVE", True, (255, 201, 15))
        texto = fuente.render("PRESIONA ESPACIO PARA JUGAR", True, (255, 255, 255))
        for i, linea in enumerate(DESCRIPCION):
            texto_linea = fuente.render(linea, True, (180, 180, 180))
            pantalla.blit(
                texto_linea,
                (ANCHO // 2 - texto_linea.get_width() // 2, YDESC_TEXTO + i * 40),
            )

        # Título: fuera del for, para que se dibuje UNA vez y no una por cada instrucción
        pantalla.blit(
            titulo,
            (
                ANCHO // 2 - titulo.get_width() // 2,
                ALTO // 4 - titulo.get_height() // 2,
            ),
        )

        # "PRESIONA ESPACIO" parpadea: se dibuja solo cuando parpadeo vale 0
        if parpadeo == 0:
            pantalla.blit(
                texto,
                (
                    ANCHO // 2 - texto.get_width() // 2,
                    ALTO // 2 - texto.get_height() // 2,
                ),
            )
        if teclas[pygame.K_SPACE]:
            estado = "jugando"
            puntos = 0
            stamina_jugador = STAMINA_MAX
            x, y = ANCHO // 2, ALTO // 2
            inicio_tiempo = pygame.time.get_ticks()  # el cronómetro vuelve a empezar

    elif estado == "jugando":

        # ---------------------------------------------------------
        #  2. LÓGICA
        # ---------------------------------------------------------

        # --- Tiempo ---
        # hora de AHORA - hora de INICIO = milisegundos jugados; // 1000 = segundos
        segundos_jugados = (pygame.time.get_ticks() - inicio_tiempo) // 1000
        tiempo_restante = TIEMPO_LIMITE - segundos_jugados

        # --- Stamina ---
        # ¿Está apretando alguna flecha? ("or" es como el || de Java)
        moviendose = (
            teclas[pygame.K_LEFT]
            or teclas[pygame.K_RIGHT]
            or teclas[pygame.K_UP]
            or teclas[pygame.K_DOWN]
        )
        # Solo corre (y gasta stamina) si aprieta Shift, le queda stamina
        # Y se está moviendo. Quieto con Shift no gasta nada.
        if teclas[pygame.K_LSHIFT] and stamina_jugador > 0 and moviendose:
            velocidad = 10  # corriendo
            # Gasta stamina, pero max(..., 0) evita que baje de 0
            stamina_jugador = max(stamina_jugador - 1, 0)
        else:
            velocidad = 3  # caminando
            # Recupera stamina poco a poco, pero min(..., MAX) evita que pase del máximo
            stamina_jugador = min(stamina_jugador + 0.3, STAMINA_MAX)

        # --- Color según la stamina (semáforo) ---
        # El orden importa: primero se pregunta por el número más alto
        if stamina_jugador >= 50:
            color_stamina = COLOR_STAMINA_ALTA
        elif stamina_jugador >= 25:
            color_stamina = COLOR_STAMINA_MEDIA
        else:
            color_stamina = COLOR_STAMINA_BAJA

        # --- Movimiento (solo mientras quede tiempo) ---
        # Ojo: en pygame la "y" crece hacia ABAJO, por eso arriba es "y -="
        if tiempo_restante > 0:
            if teclas[pygame.K_LEFT]:
                x -= velocidad
            if teclas[pygame.K_RIGHT]:
                x += velocidad
            if teclas[pygame.K_UP]:
                y -= velocidad
            if teclas[pygame.K_DOWN]:
                y += velocidad

        # --- Choque con la moneda ---
        # Distancia entre los centros del jugador y la moneda (Pitágoras)
        distancia = math.hypot(x - moneda_x, y - moneda_y)
        # Si están más cerca que la suma de los radios, se están tocando
        if distancia < RADIO + RADIO_MONEDA:
            # La moneda aparece en otro lugar al azar (debajo del HUD)
            moneda_x = random.randint(RADIO_MONEDA, ANCHO - RADIO_MONEDA)
            moneda_y = random.randint(ALTO_HUD + RADIO_MONEDA, ALTO - RADIO_MONEDA)
            puntos += 1
            # Premio: cada moneda devuelve 10 de stamina (sin pasar del máximo)
            stamina_jugador = min(stamina_jugador + 10, STAMINA_MAX)

        # --- Bordes ---
        # Que el jugador no se salga de la pantalla ni se meta en el HUD
        x = max(RADIO, min(ANCHO - RADIO, x))
        y = max(ALTO_HUD + RADIO, min(ALTO - RADIO, y))

        # ---------------------------------------------------------
        #  3. DIBUJO (el orden importa: lo último se dibuja ENCIMA)
        # ---------------------------------------------------------
        pantalla.fill((0, 128, 64))  # fondo verde: borra todo lo de la vuelta anterior

        # Franja negra del HUD: (x, y, ancho, alto)
        pygame.draw.rect(pantalla, (0, 0, 0), (0, 0, ANCHO, ALTO_HUD))

        # Barra de stamina: primero el fondo gris (siempre completo)...
        pygame.draw.rect(
            pantalla,
            BARRA_FONDO_COLOR,
            (10, 80, BARRA_STAMINA_ANCHO, BARRA_STAMINA_ALTO),
        )
        # ...y encima la parte de color. Su ancho es proporcional a la stamina:
        # (stamina / máximo) da un número entre 0 y 1, y eso por el ancho total
        ancho_stamina = (stamina_jugador / STAMINA_MAX) * BARRA_STAMINA_ANCHO
        pygame.draw.rect(
            pantalla, color_stamina, (10, 80, ancho_stamina, BARRA_STAMINA_ALTO)
        )

        # Moneda y jugador
        pygame.draw.circle(pantalla, MONEDA_COLOR, (moneda_x, moneda_y), RADIO_MONEDA)
        pygame.draw.circle(pantalla, color_stamina, (x, y), RADIO)

        # cambio de estado cuando se acaba el tiempo
        if tiempo_restante <= 0:
            estado = "fin"

        # Textos: render convierte el texto en imagen; blit la pega en la pantalla.
        # str() convierte el número en texto para poder unirlo con "Puntos: "
        texto = fuente.render("Puntos: " + str(puntos), True, (255, 255, 255))
        texto_tiempo = fuente.render(
            "Tiempo: " + str(tiempo_restante), True, (255, 255, 255)
        )
        pantalla.blit(texto, (10, 10))
        pantalla.blit(texto_tiempo, (10, 50))

    # --- Pantalla de fin (cuando se acaba el tiempo) ---
    elif estado == "fin":
        texto_final = fuente.render(
            "¡Tiempo terminado! Puntos: " + str(puntos), True, (255, 0, 0)
        )
        pantalla.fill((0, 0, 0))  # tapa todo el juego con negro
        # Centrar: mitad de la pantalla MENOS la mitad del tamaño del texto
        pantalla.blit(
            texto_final,
            (
                ANCHO // 2 - texto_final.get_width() // 2,
                ALTO // 2 - texto_final.get_height() // 2,
            ),
        )

        texto_continuar = fuente.render(
            "Presiona la tecla R para reiniciar", True, (255, 255, 255)
        )
        # Centrado en horizontal y 50 píxeles más abajo que el texto final
        pantalla.blit(
            texto_continuar,
            (ANCHO // 2 - texto_continuar.get_width() // 2, ALTO // 2 + 50),
        )

        # Reiniciar: todo vuelve a como estaba al empezar
        if teclas[pygame.K_r]:
            estado = "menu"

    pygame.display.flip()  # muestra en la ventana todo lo que se dibujó
    reloj.tick(60)  # espera lo necesario para ir a 60 vueltas por segundo


pygame.quit()  # cierra pygame al salir del while
