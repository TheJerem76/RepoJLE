#!/usr/bin/python3
# -*- coding: utf-8 -*

# Pour info, la taille de l'écran 7 pouces est de 640x480.

import RPi.GPIO as GPIO
import time #Utile pour le sime.sleep pour mettre en pause le programme
from datetime import datetime #Utile pour générer le nom de la photo selon la date du jour. Voir ligne 106. Doc : https://docs.python.org/fr/3.6/library/datetime.html
from PIL import Image #PIL sert à ouvrir, manipuler, sauveguarder des images
import pygame
from pygame.locals import *
import os

GPIO.setmode(GPIO.BCM) #Attention au choix du port ; référez-vous au site https://fr.pinout.xyz/
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pygame.init()
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
background = pygame.Surface(screen.get_size())  # Create the background object ; pygame.Surface va creer un nouvel objet image avec la taille pour arguments. Screen est une variable-
background = background.convert()  # Convert it to a background - Pour que le format de pixel soit identique entre le fond et le background

screenPicture = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen - Idem c la variable screen
backgroundPicture = pygame.Surface(screenPicture.get_size())  # Create the background object
backgroundPicture = background.convert()  # Convert it to a background - Pour que le format de pixel soit identique entre le fond et le background
#screen = pygame.display.set_mode((0,0),pygame.RESIZABLE)
width, height = screen.get_size()
rectScreen = screen.get_rect()
pygame.mouse.set_visible (False)
BUTTON_PIN = 25

#Ppygame.mixer.init()
#son = pygame.mixer.Sound('/home/pi/Photomaton/son.wav')
#canal = son.play()


def PrisePhoto(NomPhoto): #prendre une photo avec Raspistill
    command = "sudo raspistill -t 2000 -w 1200 -h 675 -o "+ NomPhoto +" -q 100" #prend une photo après 5sec de largeur 1200 et hauteur 675 de qualité 100
    os.system(command)

def AfficherPhoto(NomPhoto): # affiche NomPhoto
    print("loading image: " + NomPhoto)
    background = pygame.image.load(NomPhoto);
    background.convert_alpha()
    background = pygame.transform.scale(background,(width,height))
    screen.blit(background,(0,0),(0,0,width,height))
    pygame.display.flip()


def decompte():
  AfficherTexte("Attention")
  time.sleep(1)
  AfficherTexte("--> Photo dans 5 secondes")
  time.sleep(1)


def AfficherTexte(message): # pour pouvoir afficher des messages sur un fond noir 
    screen.fill(pygame.Color(0,0,0))
    font = pygame.font.SysFont("verdana", 30, bold=1)
    textsurface = font.render(message, 1, pygame.Color(255,255,255))
  #  textpos = text.get_rect()
  #  textpos.centerx = background.get_rect().centerx
  #  textpos.centery = background.get_rect().centery
    
  #  if(ImageShowed):
  #      backgroundPicture.blit(text, textpos)
  #  else:
  #      background.blit(text, textpos)
                    
    #screen.blit(textsurface,(240,240)) # Position x et y du texte
    #pygame.display.update()


def AfficherTexteTransparent(message): # pour pouvoir afficher des messages en conservant le fond
    font = pygame.font.SysFont("verdana", 30, bold=1)
    textsurface = font.render(message, 1, pygame.Color(255,255,255))
    screen.blit(textsurface,(35,40))
    pygame.display.update()


def AfficherTexteAccueil(message): # Afficher un Texte sur l'image d'accueil (ou à la place) 
    font = pygame.font.SysFont("verdana", 30, bold=1)
    textsurface = font.render(message, 1, pygame.Color(100,150,200))
    screen.blit(textsurface,(35,40))
    pygame.display.update()


    
def Evenement(): #Est en charge de retourner TRUE ou FALSE
    global pygame
    
    RienNeSePasse = True #initialisation de la variable RienNeSePasse a TRUE. Il n'y a pas d'evenement, rien ne se passe.
    while RienNeSePasse: #tant qu'il n'y a pas d'evenement.... Tant que RienNeSePasse est au statut defini au-dessus
            input_state = GPIO.input(BUTTON_PIN) #...alors on va lire (GPIO.input()) le PIN (variable BUTTON_PIN initialisé à 25 au début). Correspond a TRUE. La variable input_state correspond a le lecture de l'entree BUTTON_PIN (25). Voir https://deusyss.developpez.com/tutoriels/RaspberryPi/PythonEtLeGpio/#LIII-A
            if input_state == False: #Si l'etat change (appui sur le bouton)...
                    RienNeSePasse = False #Alors on indique cette variable change.           
                    return #On retourne l'etat
            for event in pygame.event.get(): #pygame.event.get() va lire les evenements en attente dans la queue ainsi que les y retirer.           
                    if event.type == pygame.KEYDOWN: #Si dans la queue il y a un appui sur une touche du clavier...
                        if event.key == pygame.K_ESCAPE: #...et qu'il s'agit de la touche echap...
                            pygame.quit() #...alors on quitte le programme https://www.pygame.org/docs/ref/key.html#comment_pygame_key_name
                        if event.key == pygame.K_DOWN: #Toutefois s'il y a un appuisur la fleche du bas
                            RienNeSePasse = False #Alors on change l'etat et donc on attend 0.2s
                            return #On retourne l'etat
            time.sleep(0.2)

            
# Début du programme #

if (os.path.isdir("/home/pi/Desktop/photos") == False): # si le dossier pour stocker les photos n'existe pas       
    os.mkdir("/home/pi/Desktop/photos")                  # alors on crée le dossier (sur le bureau)
    os.chmod("/home/pi/Desktop/photos",0o777)            # et on change les droits pour pouvoir effacer des photos

#AfficherTexteAccueil("Installez-vous et appuyez sur le bouton pour prendre une photo")


while True : #boucle jusqu'a interruption
    print ("\n attente boucle \n ")
    screensize = screen.get_rect() #Je veux récupérer la taille de l'écran...
    print ("L'écran fait", screensize) #...afin de l'afficher dans la console
     
     #On affiche la photo d'accueil
    AfficherPhoto("/home/pi/Photobooth/images/appuyezbouton.jpg")
    
     #on attend que le bouton soit pressé
    Evenement()
     # on a appuyé sur le bouton...
     #on lance le décompte
    decompte()
     #on génère le nom de la photo avec heure_min_sec
    date_today = datetime.now()
    nom_image = date_today.strftime('%d-%m-%Y_%Hh-%Mm-%Ss') #Voir strftime de la doc https://docs.python.org/fr/3.6/library/datetime.html#strftime-strptime-behavior
     #on déclenche la prise de photo
    chemin_photo = '/home/pi/Desktop/photos/'+nom_image+'.jpeg'
    PrisePhoto(chemin_photo) #Déclenchement de la prise de photo
    AfficherTexte("--> Merci ! <--")
    time.sleep(1)
     #On affiche la photo...
    AfficherPhoto(chemin_photo)
     #...et par dessus on affiche un message
    AfficherTexteTransparent("OK ; voici ce qui est dans la boite ...")
    time.sleep(2) #Ajout d'un temps d'affichage afin de repartir sur l'accueil ensuite
    pygame.display.flip()
     #on recommence en rechargeant l'écran d'accueil
    #AfficherPhoto("/home/pi/Photobooth/images/appuyezbouton.jpg")
    #pygame.mixer.init()
    #son = pygame.mixer.Sound('/home/pi/Photomaton/son.wav')
    #canal = son.play()


    #if (GPIO.input(25) == 0): #si le bouton est encore enfoncé (son etat sera 0)
          #print ("Ho ; bouton  appuyé !!! Je dois sortir ; c'est le chef qui l'a dit !") #Va afficher ça dans la console
          #break # alors on sort du while
          
    #for event in pygame.event.get(): #pygame.event.get() va lire les evenements en attente dans la queue ainsi que les y retirer.
        #if event.type == pygame.KEYDOWN: #Si dans la queue il y a un appui sur la fleche du bas sur le clavier alors on attends 0.2s (fin de la fonction)
            #if event.key == pygame.K_ESCAPE: #Mais si il y a un appui sur la touche echap https://www.pygame.org/docs/ref/key.html#comment_pygame_key_name
                #print("Appui sur Echap, fin du programme")
                #pygame.quit() #Alors on quitte le programme


GPIO.cleanup()           # reinitialisation GPIO lors d'une sortie normale
