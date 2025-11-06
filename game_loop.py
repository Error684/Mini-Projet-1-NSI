import pygame, random
from main import *


pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700

CARD_WIDTH = 100
CARD_HEIGHT = 144
CARD_SPACING = 10

ammount_to_call = 0
minimum_raise = 0

"""
Etat_du_jeu = 0 : Flop
Etat_du_jeu = 1 : Turn
Etat_du_jeu = 2 : River
Etat_du_jeu = 3 : Showdown
"""
etat_du_jeu = 0

couleur_du_font = ((30, 250, 30))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

try:
     spritesheet = pygame.image.load('spritesheet.png').convert_alpha()
except pygame.error as e:
    print(f"Erreur pendant le chargement de la spritesheet : {e}")
    pygame.quit()
    exit()

def obtenir_image_carte(carte):
    index_ligne = carte[0] - 1
    index_colonne = carte[1] - 2
    x = index_colonne * CARD_WIDTH
    y = index_ligne * CARD_HEIGHT
    rect_carte = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    img_carte = spritesheet.subsurface(rect_carte)
    return img_carte

def dessiner_cartes(surface, liste_de_cartes, x_depart, y_depart):
    for i, carte in enumerate(liste_de_cartes):
        position_x = x_depart + i * (CARD_WIDTH + CARD_SPACING)
        image_de_la_carte = obtenir_image_carte(carte)
        surface.blit(image_de_la_carte, (position_x, y_depart))

main_joueur_cartes = [deck[index] for index in Joueur1.Main]

total_board_width = (5 * CARD_WIDTH) + (4 * CARD_SPACING)

start_x_board = (SCREEN_WIDTH - total_board_width) / 2
start_y_board = 50

total_hand_width = (2 * CARD_WIDTH) + (1 * CARD_SPACING)
start_x_hand = (SCREEN_WIDTH - total_hand_width) / 2
start_y_hand = 220

running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            running = False
            
    screen.fill(couleur_du_font)
    #dessiner_cartes(screen, board, (SCREEN_WIDTH / 2) - ( total_board_width / 2) , (SCREEN_HEIGHT / 2) - CARD_HEIGHT*2 )
    dessiner_cartes(screen, main_joueur_cartes, (SCREEN_WIDTH / 2) - 100, 450)
    pygame.display.flip()


pygame.quit()
