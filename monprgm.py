#!usr/bin/python3
#-*- coding: utf-8 -*

#Pour les tests et tuto, voir aussi https://www.w3schools.com/python/default.asp

import picamera #Import des librairies
import pygame #pygame sert a l'affichage
import datetime
import time
import os
import PIL.Image
import cups
import RPi.GPIO as GPIO

from threading import Thread #Import d'une fonction dans chacunes des librairies suivantes
from pygame.locals import *
from time import sleep
from PIL import Image, ImageDraw
from datetime import datetime


# Definition des variables
Numeral = ""  # Numeral is the number display
Message = ""  # Message is a fullscreen message
BackgroundColor = ""
CountDownPhoto = ""
CountPhotoOnCart = ""
SmallMessage = ""  # SmallMessage is a lower banner message
TotalImageCount = 0  # Counter for Display and to monitor paper usage
PhotosPerCart = 30  # Selphy takes 16 sheets per tray
imagecounter = 0
imagefolder = 'Photos'
#usbfolder = '/media/pi/YELLOW 15GO/Photobooth'
templatePath = os.path.join('Photos', 'Template', "template.jpg") #Path of template image - Va construire le chemin en joignant les parametres entre quote pour que la variable templatePath soit le document qui sera trouve en suivant le chemin

ImageShowed = False
Printing = False
BUTTON_PIN = 25
#IMAGE_WIDTH = 558
#IMAGE_HEIGHT = 374
#IMAGE_WIDTH = 550
#IMAGE_HEIGHT = 360
IMAGE_WIDTH = 1024 # Base d'un ratio 16/9 ; utilise pour un resize en ligne 318
IMAGE_HEIGHT = 600


# Load the background template
bgimage = PIL.Image.open(templatePath) #La variable bgimage ouvre l'image ayant pour nom templatePath

#Setup GPIO
GPIO.setmode(GPIO.BCM) # Cela signifie que le comptage des PIN se fera selon l'approche de numerotation electronique de la carte RPI. Voir https://deusyss.developpez.com/tutoriels/RaspberryPi/PythonEtLeGpio/#LIII-A
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) #BUTTON_PIN est une variable = 25 definie en ligne.35. Ici on set le pin 25 en entree

# initialise pygame
#Pour info, pygame est un truc qui donne la possibilite d'afficher des elements a l'ecran
pygame.init()  # Initialise pygame - https://devdocs.io/pygame/
myfont = pygame.font.SysFont("monospace", 15) # Je definis mon element texte
pygame.mouse.set_visible(False) #hide the mouse cursor
infoObject = pygame.display.Info() #pygame.display.Info sert a creer un objet d'information video destine a l'affichage. Il prend pour proprietes ce qu'il trouvera dans current-h et current_y qui sont des attributs de .display.info.  Voir https://devdocs.io/pygame/ref/display#pygame.display.Info
screen = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN) 
# Full screen ; display.set_mode initialise une fenetre ou ecran pour un affichage. Par exemple ici :

#Screen est la variable
#qui est egal a
#ecran cree par la fonction pygame.display.set_mode
#Et avec comme propriete les tailles suivantes :
#En x : infoObject.current_w
#En y : infoObject.current_y

#infoObject est egal a display.info qui permet l'affichage et qui dispose de plusieurs attributs dont current_w et current_y. Par defaut, quelles sont les valeurs prises par ces attributs ?

#pygame.FULLSCREEN correspond a un attribut de fenetre permettant de retirer les bordures.
#

background = pygame.Surface(screen.get_size())  # Create the background object ; pygame.Surface va creer un nouvel objet image avec la taille pour arguments. Screen est une variable-
background = background.convert()  # Convert it to a background - Pour que le format de pixel soit identique entre le fond et le background

screenPicture = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen - Idem c la variable screen
backgroundPicture = pygame.Surface(screenPicture.get_size())  # Create the background object
backgroundPicture = background.convert()  # Convert it to a background - Pour que le format de pixel soit identique entre le fond et le background

transform_x = infoObject.current_w # how wide to scale the jpg when replaying
transfrom_y = infoObject.current_h # how high to scale the jpg when replaying

camera = picamera.PiCamera() #https://picamera.readthedocs.io/en/release-1.12/api_camera.html#picamera
# Initialise the camera object
#camera.resolution = (infoObject.current_w, infoObject.current_h) #la resolution de la camera prendra heigh and width de l'ecran
camera.resolution = (1200,720)
camera.rotation              = 0
camera.hflip                 = True
camera.vflip                 = False
camera.brightness            = 50
camera.preview_alpha = 120
camera.preview_fullscreen = True
#camera.framerate             = 24
#camera.sharpness             = 0
#camera.contrast              = 8
#camera.saturation            = 0
#camera.ISO                   = 0
#camera.video_stabilization   = False
#camera.exposure_compensation = 0
#camera.exposure_mode         = 'auto'
#camera.meter_mode            = 'average'
#camera.awb_mode              = 'auto'
#camera.image_effect          = 'none'
#camera.color_effects         = None
#camera.crop                  = (0.0, 0.0, 1.0, 1.0)


    
def WaitForEvent(): #Est charge de retourner TRUE ou FALSE
    global pygame
    NotEvent = True #initialisation de la variable NotEvent a TRUE. Il n'y a pas d'evenement.
    while NotEvent: #tant qu'il n'y a pas d'evenement.... Tant que NotEvent est au statut defini au-dessus
            input_state = GPIO.input(BUTTON_PIN) #...alors on va lire le PIN. Correspond a TRUE. La variable input_state correspond a le lecture de l'entree BUTTON_PIN (25). Voir https://deusyss.developpez.com/tutoriels/RaspberryPi/PythonEtLeGpio/#LIII-A
            if input_state == False: #Si l'etat change (appui sur le bouton)...
                    NotEvent = False #Alors on indique cette variable change.           
                    return #On retourne l'etat
            for event in pygame.event.get(): #pygame.event.get() va lire les evenements en attente dans la queue ainsi que les y retirer.           
                    if event.type == pygame.KEYDOWN: #Si dans la queue il y a un appui sur la fleche du bas sur le clavier alors on attends 0.2s (fin de la fonction)
                        if event.key == pygame.K_ESCAPE: #Mais si il y a un appui sur la touche echap https://www.pygame.org/docs/ref/key.html#comment_pygame_key_name
                            pygame.quit() #Alors on quitte le programme
                        if event.key == pygame.K_DOWN: #Toutefois s'il y a un appuisur la fleche du bas
                            NotEvent = False #Alors on change l'etat et donc on attend 0.2s
                            return #On retourne l'etat
            time.sleep(0.2)

def main(threadName, *args): # *args correspond a un tuple qui peut donc contenir plusieurs arguments quels qu'ils soient, var, string, float, etc.
    while True: #Tant que WaitForEvent renvoie TRUE

            pygame.init() #Initialisation de pygame, cela va charger tous les modules
            ecran = pygame.display.set_mode((0,0), pygame.FULLSCREEN) #On créé une fenêtre avec le module display, on met 0,0 en argument avec le flag fullscreen pour que le plein écran fonctionne. (https://zestedesavoir.com/tutoriels/846/pygame-pour-les-zesteurs/1381_a-la-decouverte-de-pygame/creer-une-simple-fenetre-personnalisable/)
            image = pygame.image.load("images/appuyezbouton.jpg").convert_alpha()
            image = pygame.transform.scale(picture, (160, 90))
            continuer = True
            while continuer:
                ecran.blit(image, (0,50))
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        continuer = False
                pygame.display.flip()
            pygame.quit()
            WaitForEvent() #Puis on lance (arriere plan) la fonction qui bloque la fonction tant qu'il n'y a pas d'appui
            time.sleep(0.2) #Puis on attends 0.2s
            TakePictures() #Puis on lance la fonction TakePictures
    GPIO.cleanup()


# launch the main thread
Thread(target=main, args=('Main', 1)).start() # Cela represente la fonction principale du programme. C'est une activite de fil d'execution qui va lancer la fonction main.
