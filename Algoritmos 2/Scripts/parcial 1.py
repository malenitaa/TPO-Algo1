import pygame
from os.path import join

pygame.init()
pygame.display.set_caption("Game")

# Constantes
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5
JUMP_HEIGHT = 10
GRAVITY = 0.5

# Atributos del jugador
player_x = 50
player_y = HEIGHT - 60  # Ajuste para iniciar en el suelo
player_width = 40
player_height = 60

# Variables de salto
is_jumping = False
jump_count = JUMP_HEIGHT

# Rutas de los sprites
sprite_sheet_path = join("assets", "main_characters", "ninja_frog")
run_sprite_files = [f"{i:02d}_Run.png" for i in range(12)]
idle_sprite_files = [f"{i:02d}_Idle.png" for i in range(11)]
jump_sprite_files = ["Jump.png", "Fall.png"]

# Cargar las imágenes de los sprites para la animación de correr
run_sprites = [pygame.image.load(join(sprite_sheet_path, file)) for file in run_sprite_files]
# Cargar las imágenes de los sprites para la animación de idle
idle_sprites = [pygame.image.load(join(sprite_sheet_path, file)) for file in idle_sprite_files]
# Cargar las imágenes de los sprites para la animación de salto
jump_sprites = [pygame.image.load(join(sprite_sheet_path, file)) for file in jump_sprite_files]

window = pygame.display.set_mode((WIDTH, HEIGHT))  # Configuración de la ventana

def get_background(name):
    """Carga y divide el fondo en mosaicos."""
    image = pygame.image.load(join("assets", "Background", name))
    width, height = image.get_size()  # Obtiene el ancho y alto de la imagen
    tiles = []

    # Crea una lista de posiciones para los mosaicos del fondo
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    return tiles, image

def draw(window, background, bg_image, current_sprite, flip_sprite):
    """Dibuja el fondo y el jugador en la ventana."""
    
    for tile in background:
        window.blit(bg_image, tile)
    
    # Dibuja al jugador en la ventana usando la imagen actual del sprite
    if flip_sprite:
        current_sprite = pygame.transform.flip(current_sprite, True, False)
    
    window.blit(current_sprite, (player_x, player_y))
    pygame.display.update()

def movement():
    """Maneja el movimiento del jugador y el salto."""
    
    global player_x, player_y, is_jumping, jump_count  # Declarar las variables globales

    keys = pygame.key.get_pressed()

    # Movimiento horizontal
    if keys[pygame.K_LEFT] and player_x - PLAYER_VEL >= 0:
        player_x -= PLAYER_VEL
        return True, None  # Indica que el jugador se está moviendo a la izquierda

    if keys[pygame.K_RIGHT] and player_x + player_width + PLAYER_VEL <= WIDTH:
        player_x += PLAYER_VEL
        return False, None  # Indica que el jugador se está moviendo a la derecha

    # Lógica del salto
    if is_jumping:
        if jump_count >= -JUMP_HEIGHT:
            neg = 1
            if jump_count < 0:
                neg = -1
            player_y -= (jump_count ** 2) * GRAVITY * neg
            jump_count -= 1
        else:
            is_jumping = False
            jump_count = JUMP_HEIGHT
        # Determina si mostrar el sprite de salto
        return None, True

    else:
        # Solo permitir el salto si el jugador está en el suelo
        if player_y >= HEIGHT - player_height and keys[pygame.K_SPACE]:
            is_jumping = True
            return None, True

    return None, False  # Por defecto, no hay necesidad de voltear el sprite y no está saltando

def main(window):
    """Función principal del juego."""
    clock = pygame.time.Clock()
    background, bg_image = get_background("Purple.png")

    # Variables para la animación
    run_sprite_index = 0
    idle_sprite_index = 0
    jump_sprite_index = 0
    sprite_timer = 0
    sprite_delay = 100  # Tiempo en milisegundos entre cambios de sprite
    run_animation = False
    jump_animation = False

    run = True
    while run:
        clock.tick(FPS)
        
        sprite_timer += clock.get_time()
        if sprite_timer >= sprite_delay:
            sprite_timer = 0
            if run_animation:
                run_sprite_index = (run_sprite_index + 1) % len(run_sprites)
            elif jump_animation:
                jump_sprite_index = (jump_sprite_index + 1) % len(jump_sprites)
            else:
                idle_sprite_index = (idle_sprite_index + 1) % len(idle_sprites)

        moving, jumping = movement()

        if jumping:
            # Jugador está saltando, usa la animación de salto
            current_sprite = jump_sprites[jump_sprite_index]
            jump_animation = True
            run_animation = False
            flip_sprite = moving if moving is not None else False
        elif moving is not None:
            # Jugador se está moviendo, usa la animación de correr
            current_sprite = run_sprites[run_sprite_index]
            run_animation = True
            jump_animation = False
            flip_sprite = moving
        else:
            # Jugador no se está moviendo, usa la animación de idle
            current_sprite = idle_sprites[idle_sprite_index]
            run_animation = False
            jump_animation = False
            flip_sprite = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        draw(window, background, bg_image, current_sprite, flip_sprite)

    pygame.quit()

if __name__ == "__main__":
    main(window)
