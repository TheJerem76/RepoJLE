#!usr/bin/python3
#-*- coding: utf-8 -*

#Pour les tests et tuto, voir aussi https://www.w3schools.com/python/default.asp

#-----------------------------------#
#-----! Import des librairies !-----#
import picamera
import pygame
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
#-----------------------------------#



#--------------------------------------#
#-----! Définition des variables !-----#
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
#--------------------------------------#


#---------------------------------------------------------#
#-----! On charge le template de fond pour la photo !-----#
bgimage = PIL.Image.open(templatePath) #La variable bgimage ouvre l'image ayant pour nom templatePath
#---------------------------------------------------------#

#---------------------------------#
#-----! On définit les GPIO !-----#
GPIO.setmode(GPIO.BCM) # Cela signifie que le comptage des PIN se fera selon l'approche de numerotation electronique de la carte RPI. Voir https://deusyss.developpez.com/tutoriels/RaspberryPi/PythonEtLeGpio/#LIII-A
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) #BUTTON_PIN est une variable = 25 definie en ligne.35. Ici on set le pin 25 en entree
#---------------------------------#


#--------------------------------------#
#-----! Initialisation de PyGame !-----#
#Pour info, pygame est un truc qui donne la possibilite d'afficher des elements a l'ecran
pygame.init()  # Initialise pygame - https://devdocs.io/pygame/
myfont = pygame.font.SysFont("monospace", 15) # Je definis mon element texte
pygame.mouse.set_visible(False) #hide the mouse cursor
videoObject = pygame.display.Info() #pygame.display.Info sert a creer un objet d'information video destine a l'affichage. Il prend pour proprietes ce qu'il trouvera dans current_h et current_y qui sont des attributs de .display.info.  Voir https://devdocs.io/pygame/ref/display#pygame.display.Info
screen = pygame.display.set_mode((videoObject.current_w,videoObject.current_h), pygame.FULLSCREEN) 
# Full screen ; display.set_mode initialise une fenetre ou ecran pour un affichage. Par exemple ici :

#Screen est la variable
#qui est egal a
#ecran cree par la fonction pygame.display.set_mode
#Et avec comme propriete les tailles suivantes :
#Size en x : videoObject.current_w
#Size en y : videoObject.current_y

#videoObject est egal a display.info qui permet l'affichage et qui dispose de plusieurs attributs dont current_w et current_y.

#pygame.FULLSCREEN correspond a un attribut de fenetre permettant de retirer les bordures.

background = pygame.Surface(screen.get_size())  # Create the background object ; pygame.Surface va creer un nouvel objet image avec la taille pour arguments. Screen est une variable-
background = background.convert()  # Convert it to a background - Pour que le format de pixel soit identique entre le fond et le background

screenPicture = pygame.display.set_mode((videoObject.current_w,videoObject.current_h), pygame.FULLSCREEN)  # Full screen - Idem c la variable screen
backgroundPicture = pygame.Surface(screenPicture.get_size())  # Create the background object
backgroundPicture = background.convert()  # Convert it to a background - Pour que le format de pixel soit identique entre le fond et le background

transform_x = videoObject.current_w # how wide to scale the jpg when replaying
transfrom_y = videoObject.current_h # how high to scale the jpg when replaying
#--------------------------------------#

#-----! Initialisation de la camera !-----#
#-----------------------------------------#
camera = picamera.PiCamera() #https://picamera.readthedocs.io/en/release-1.12/api_camera.html#picamera
# Initialise the camera object
#camera.resolution = (videoObject.current_w, videoObject.current_h) #la resolution de la camera prendra heigh and width de l'ecran
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
#--------------------------------------#


#---------------------------------------------------------------------#
#-----! A function to handle keyboard/mouse/device input events !-----#
def input(events):
    for event in events:  # Hit the ESC key to quit the slideshow.
        if (event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
            pygame.quit()
#---------------------------------------------------------------------#

#----------------------------------------------------------------------------------#
#-----! set variables to properly display the image on screen at right ratio !-----#
def set_demensions(img_w, img_h): #Fonction utile que dans la fonction show_image pour que la dimention d'afficahge soit correcte.
    # Note this only works when in booting in desktop mode. 
    # When running in terminal, the size is not correct (it displays small). Why?

    # connect to global vars
    global transform_y, transform_x, offset_y, offset_x

    # based on output screen resolution, calculate how to display
    ratio_h = (videoObject.current_w * img_h) / img_w 

    if (ratio_h < videoObject.current_h):
        #Use horizontal black bars
        #print "horizontal black bars"
        transform_y = ratio_h
        transform_x = videoObject.current_w
        offset_y = (videoObject.current_h - ratio_h) / 2
        offset_x = 0
    elif (ratio_h > videoObject.current_h):
        #Use vertical black bars
        #print "vertical black bars"
        transform_x = (videoObject.current_h * img_w) / img_h
        transform_y = videoObject.current_h
        offset_x = (videoObject.current_w - transform_x) / 2
        offset_y = 0
    else:
        #No need for black bars as photo ratio equals screen ratio
        #print "no black bars"
        transform_x = videoObject.current_w
        transform_y = videoObject.current_h
        offset_y = offset_x = 0
#----------------------------------------------------------------------------------#

#-------------------------------------------------------------------#
#-----! Definir le dossier "images" afin de stoker les photos !-----#
def InitFolder():
    global imagefolder
    global Message
 
    Message = 'Folder Check...'
    UpdateDisplay()
    Message = ''

    #check image folder existing, create if not exists
    if not os.path.isdir(imagefolder):  #Si la fonction os.path.isdir se verifie, elle renverra TRUE. Donc si le path "Photos" n'existe pas...
        os.makedirs(imagefolder)    #...alors il est cree. En effet, la variable imagefolder correspond au dossier 'Photos' defini en debut de programme.
            
    imagefolder2 = os.path.join(imagefolder, 'images') #Construction du path /images (on ajoute /image au path contenu dans imagefolder)
    if not os.path.isdir(imagefolder2): #Si la fonction ne se verifie pas...
        os.makedirs(imagefolder2) #Alors on cree le chemin contenu dans la variable imagefolder2
#-------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------#
#-----! Initialiser la variable Message, Numeral ou CountDownPhoto dans la fonction UpdateDisplay !-----#
def DisplayText(fontSize, textToDisplay): # Comme ca, a l'appel de UpdateDisplay qui vient toujours apres l'initialisation de l'une des trois variable, ce qui soit s'afficher s'affichera selon le type de message choisi a travers la variable utilise.

    global Numeral
    global Message
    global screen
    global background
    global pygame
    global ImageShowed
    global screenPicture
    global backgroundPicture
    global CountDownPhoto

    if (BackgroundColor != ""):
            #print(BackgroundColor)
            background.fill(pygame.Color("black"))
    if (textToDisplay != ""):
            #print(displaytext)
            font = pygame.font.Font(None, fontSize) #pygame.font.Font va charger la font d'un fichier defini en attribu. Si le fichier est None, alors la font sera prise par defaut. L'autre attribu correspond a la taille de la font.
            text = font.render(textToDisplay, 1, (227, 157, 200)) #Render creer une nouvelle surface sur laquelle dessiner l'ecriture. Impossible d'ecrire sur plus qu'une ligne. La surface creee sera de dimentions appropriee a contenir le text. Les atributs sont : Le texte a ecrire, un antialias en booleen qui correspond a des bords lisses si c'est a TRUE, la couleur (ici rose car 227 157 200) ainsi qu'en optionnel la couleur de fond du texte (surlignage je pense). La variable text va donc contenir les propriete de choisies. Voir https://devdocs.io/pygame/ref/font#pygame.font.Font.render
            textpos = text.get_rect() #Recuperation du rectangle necessaire a l'afficahge de la variable text http://www.frederic-junier.org/ISN/Cours/tutoriel-pygame.html
            textpos.centerx = background.get_rect().centerx #Positionnement du rectangle http://www.frederic-junier.org/ISN/Cours/tutoriel-pygame.html
            textpos.centery = background.get_rect().centery #Positionnement du rectangle http://www.frederic-junier.org/ISN/Cours/tutoriel-pygame.html
            if(ImageShowed):
                    backgroundPicture.blit(text, textpos) #blit est une fonction de pygame qui superpose text avec textpos
            else:
                    background.blit(text, textpos)
#--------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------------------------------#
#-----! Initialiser les variables BackgroundColor, Message, Numeral et CountDownPhoto selon des proprietes de couleurs et taille !-----#
def UpdateDisplay():
    # init global variables from main thread
    global Numeral
    global Message
    global screen
    global background
    global pygame
    global ImageShowed
    global screenPicture
    global backgroundPicture
    global CountDownPhoto
   
    background.fill(pygame.Color("white"))  # White background
    #DisplayText(120, Message)
    #DisplayText(800, Numeral)
    #DisplayText(500, CountDownPhoto)

    if (BackgroundColor != ""):
            #print(BackgroundColor)
            background.fill(pygame.Color("black"))
    if (Message != ""):
            #print(displaytext)
            font = pygame.font.Font(None, 120) # Modif taille texte
            text = font.render(Message, 1, (227, 157, 200)) #Modif couleur texte ; font.render va ecrire du texte sur une nouvelle "surface"
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            textpos.centery = background.get_rect().centery
            if(ImageShowed):
                    backgroundPicture.blit(text, textpos)
            else:
                    background.blit(text, textpos)

    if (Numeral != ""):
            #print(displaytext)
            font = pygame.font.Font(None, 800)
            text = font.render(Numeral, 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            textpos.centery = background.get_rect().centery
            if(ImageShowed):
                    backgroundPicture.blit(text, textpos)
            else:
                    background.blit(text, textpos)

    if (CountDownPhoto != ""):
            #print(displaytext)
            font = pygame.font.Font(None, 500)
            text = font.render(CountDownPhoto, 1, (227, 157, 200))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            textpos.centery = background.get_rect().centery
            if(ImageShowed):
                    backgroundPicture.blit(text, textpos)
            else:
                    background.blit(text, textpos)
    
    if(ImageShowed == True):
        screenPicture.blit(backgroundPicture, (0, 0))       
    else:
        screen.blit(background, (0, 0))
   
    pygame.display.flip() #MaJ pour voir ce qui a ete blitte (colle) sur l'ecran.
    return
#--------------------------------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
#-----! Montrer le cliche pris dans CapturePicture (pas de template ici) !-----#
def ShowPicture(file, delay):
    global pygame
    global screenPicture
    global backgroundPicture
    global ImageShowed
    backgroundPicture.fill((0, 0, 0)) #Qu'est ce que le .fill ?
    img = pygame.image.load(file)
    img = pygame.transform.scale(img, screenPicture.get_size())  # Make the image full screen
    #backgroundPicture.set_alpha(200)
    backgroundPicture.blit(img, (0,0))
    screen.blit(backgroundPicture, (0, 0))
    pygame.display.flip()  # update the display - MaJ pour voir ce qui a ete blitte (colle) sur l'ecran.
    ImageShowed = True
    time.sleep(delay)
#------------------------------------------------------------------------------#

#-----------------------------------------#
#-----! Display one image on screen !-----#
def show_image(image_path): #Fonction chargee d'afficher une image. Elle attend en entree la variable image_path (path d'un fichier photo) afin de savoir quoi afficher
    screen.fill(pygame.Color("white")) # clear the screen   
    img = pygame.image.load(image_path) # load the image
    img = img.convert() # On converti le format des pixel du fond au meme format que celui de l'ecran http://www.frederic-junier.org/ISN/Cours/tutoriel-pygame.html
    set_demensions(img.get_width(), img.get_height()) # set pixel dimensions based on image 
    x = (videoObject.current_w / 2) - (img.get_width() / 2)
    y = (videoObject.current_h / 2) - (img.get_height() / 2)
    screen.blit(img,(x,y)) #Va dessiner au sein d'une surface le contenu de img en fonction des positions definies en x et y.
    pygame.display.flip() #MaJ pour voir ce qui a ete blitte (colle) sur l'ecran.
#-----------------------------------------#

#---------------------------------------------------------#
#-----! Prendre une cliche et retourner son nom. !-----#
def CapturePicture():
    global imagecounter
    global imagefolder
    global Numeral
    global Message
    global screen
    global background
    global screenPicture
    global backgroundPicture
    global pygame
    global ImageShowed
    global CountDownPhoto
    global BackgroundColor

    BackgroundColor = ""
    Numeral = ""
    Message = ""
    UpdateDisplay()
    time.sleep(1)
    CountDownPhoto = ""
    UpdateDisplay()
    background.fill(pygame.Color("black"))
    screen.blit(background, (0, 0))
    pygame.display.flip() #MaJ pour voir ce qui a ete blitte (colle) sur l'ecran.
    camera.start_preview() # Lancement de l'apercu
    BackgroundColor = "black"

    countDown = 6 #On place un temps en secondes dans la variable countDown
    while countDown > 0:      
            BackgroundColor = ""
            Numeral = ""
            Message = "Souriez ! Photo dans " + str(countDown) #On affiche le message + le compteur
            UpdateDisplay()        
            countDown = countDown - 1
            time.sleep(1) 


    for x in range(4, -1, -1): # Pour x compris dans un ecart qui commence a 4(optionnal), s'arrete a -1 (required), avec un ecart de -1 (optionnal) https://www.w3schools.com/python/ref_func_range.asp
        if x == 0:                        
            Numeral = ""
            Message = "PRENEZ LA POSE !!"
        else:                        
                        #Numeral = str(x)
                        Message = ""                
                        UpdateDisplay()
                        time.sleep(1)

        BackgroundColor = ""
        Numeral = ""
        Message = ""
        UpdateDisplay()
        imagecounter = imagecounter + 1
        ts = datetime.now()
        filename = os.path.join(imagefolder, 'images', str(imagecounter)+"_"+str(ts.strftime("%d-%m-%Y %H:%M:%S")) + '.jpg')
        camera.capture(filename, resize=(IMAGE_WIDTH, IMAGE_HEIGHT)) # Le resize est non mandatory pour cette fonction
        camera.stop_preview() # Fin de l'apercu
        ShowPicture(filename, 2)
        ImageShowed = False
        return filename
#---------------------------------------------------------#

#-----------------------------------------------------------#
#-----! Grosse fonction qui va faire plusieurs choses !-----#
def PrisePhoto():
    global imagecounter
    global imagefolder
    #global usbfolder
    global Numeral
    global Message
    global screen
    global background
    global pygame
    global ImageShowed
    global CountDownPhoto
    global BackgroundColor
    global Printing
    global PhotosPerCart
    global TotalImageCount    
    
    input(pygame.event.get()) #On vient regarder dans la liste des evenements qu'il n'y ait pas de touche Echap appuyé auquel cas on quitte le programme
    show_image('images/faitesbeausourire.jpg')
    time.sleep(3) #Temps d'affichage de l'image
    filename1 = CapturePicture() # La variable filename1 sera egale au resultat obtenu suite au lancement de la fonction CapturePicture, c'est a dire au nom de la photo.

#A la suite de cette ligne, les operatons de placement de la photo sur le template + renommage  + enregistrement de la photo vont se lancer. La partie impression de la photo est egalement proposee.

        #CountDownPhoto = "2/3"
        #filename2 = CapturePicture()

        #CountDownPhoto = "3/3"
        #filename3 = CapturePicture()

    CountDownPhoto = ""
    Message = "Attendez"
    UpdateDisplay()
        

    image1 = PIL.Image.open(filename1) # On ouvre la photo
        #image2 = PIL.Image.open(filename2)
        #image3 = PIL.Image.open(filename3)   
    TotalImageCount = TotalImageCount + 1
    
    bgimage.paste(image1, (40, 40))  # Puis on place la photo image1 sur le template thematique (1 an Sam). Plus x est petit, plus l'image est sur la gauche ; y petit = image en haut
        #bgimage.paste(image1, (625, 30))
        #bgimage.paste(image2, (625, 410))
        #bgimage.paste(image3, (55, 410))
        # Create the final filename
    ts = time.time()
    Final_Image_Name = os.path.join(imagefolder, "Final_" + str(TotalImageCount)+"_"+str(ts) + ".jpg")
        # Save it to the usb drive
    bgimage.save(Final_Image_Name)
        #Final_Image_Name = os.path.join(usbfolder, "Final_" + str(TotalImageCount)+"_"+str(ts) + ".jpg")
        # Save it to the usb drive
    bgimage.save(Final_Image_Name)
        # Save a temp file, its faster to print from the pi than usb
    bgimage.save('/home/pi/Desktop/tempprint.jpg')
    ShowPicture('/home/pi/Desktop/tempprint.jpg',5)
    bgimage2 = bgimage.rotate(0)
    bgimage2.save('/home/pi/Desktop/tempprint.jpg')
    ImageShowed = False #Apres le "Appuyez pour imprimer", le compteur apparait sur fond blanc. Si "True", ca ne va pas
    label = myfont.render("Some text!", 10, (255,255,0))
        
        #Boucle
        #countDown = 15 #On place un temps en secondes dans la variable countDown
        #while countDown > 0:
            #BackgroundColor = ""
            #Numeral = ""
            #Message = "Appuyez sur le bouton pour imprimer... " + str(countDown) #On affiche impression en cours + le compteur countDown
            #countDown = countDown - 1
            #UpdateDisplay() 
            #time.sleep(1)
        #Fin Boucle
        
        #Message = "Appuyez sur le bouton pour imprimer..."
    Message = "Vous souhaitez imprimer ? Appuyez..."    
    UpdateDisplay()
    time.sleep(3)
    UpdateDisplay()
    Message = ""
        #UpdateDisplay()
    Printing = False
    WaitForPrintingEvent() #On lance la fonction. Soit le compte a rebours va jusqu'a la fin, soit un appui est detecte et donc on imprime.
    Numeral = ""
    Message = ""
    print(Printing)
    if Printing: #Si Printing = TRUE
            if (TotalImageCount <= PhotosPerCart): #Si le total d'images prises est inferieur ou egal au total d'image prevues par photos
                    if os.path.isfile('/home/pi/Desktop/tempprint.jpg'): #Si le fichier existe
                                # Open a connection to cups
                            conn = cups.Connection()
                                # get a list of printers
                            printers = conn.getPrinters()
                                # select printer 0
                            printer_name = printers.keys()[0]
                                #Message = "Impression en cours..."
                            UpdateDisplay()
                            time.sleep(1)
                                # print the buffer file
                            printqueuelength = len(conn.getJobs()) #len() va retourner le nombre d'item dans un objet
                            if printqueuelength > 1: #S'il y a + qu'un seul element dans la file d'attente
                                    ShowPicture('/home/pi/Desktop/tempprint.jpg',5) #Alors on montre la photo
                                    conn.enablePrinter(printer_name)
                                    Message = "Impression impossible" #Et on afficbhe un message   
                                    UpdateDisplay()
                                    time.sleep(1) #Et on attend une seconde
                            else: #Sinon
                                    conn.printFile(printer_name, '/home/pi/Desktop/tempprint.jpg', "PhotoBooth", {})
                                    countDown = 55 #On place un temps en secondes dans la variable countDown le temps que l'impression se termine
                                    while countDown > 0:      
                                        BackgroundColor = ""
                                        Numeral = ""
                                        Message = "Impression en cours... " + str(countDown) #On affiche impression en cours + le compteur
                                        UpdateDisplay()        
                                        countDown = countDown - 1
                                        time.sleep(1)          
            else: #Sinon, donc si le total d'images prises est superieur au total d'image prevues par photos
                    Message = "Nous vous enverrons vos photos"
                    Numeral = ""
                    UpdateDisplay()
                    time.sleep(1)
                
    Message = ""
    Numeral = ""
    ImageShowed = False
    UpdateDisplay()
    time.sleep(1)
#-----------------------------------------------------------#

#-------------------------------------------------------------------------------------------------------------#
#-----! Ne plus detecter d'evenements sur le pin BUTTON_PIN (25 donc) avant de repasser Printing a TRUE !-----#
def MyCallback(channel):
    global Printing
    GPIO.remove_event_detect(BUTTON_PIN)
    Printing=True
#-------------------------------------------------------------------------------------------------------------#

#-------------------------------------#
#-----! Retourner TRUE ou FALSE !-----#
def WaitForPrintingEvent():
    global BackgroundColor
    global Numeral
    global Message
    global Printing #Set a FALSE dans la fonction TakePictures mais sera modifie lors de l'appel a MyCallback
    global pygame
    countDown = 5
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING) #On bloque l'execution jusqu'a ce que l'evenement (appui sur une touche) se produise (sur pin 25). Voir https://deusyss.developpez.com/tutoriels/RaspberryPi/PythonEtLeGpio/
    GPIO.add_event_callback(BUTTON_PIN, MyCallback) #On ajoute l'evenement de retrait d'ecoute d'evenement
    
    while Printing == False and countDown > 0: #Tant que Printing = False et que countDown > 0, on execute la boucle
        if(Printing == True): #Mais si Printing = True...
            return #...alors on retourne TRUE
        for event in pygame.event.get(): #Pour les evenements dans la queue...           
            if event.type == pygame.KEYDOWN: #On lit la queue, s'il y a la fleche du bas...                
                if event.key == pygame.K_DOWN: 
                    GPIO.remove_event_detect(BUTTON_PIN) #Alors on retire cet evenement de la queue...
                    Printing = True #...Et on passe Printing a TRUE
                    return #Puis en renvoie TRUE       
        BackgroundColor = "" 
        Numeral = str(countDown) #Sinon on affiche le compte a rebours
        Message = ""
        UpdateDisplay() #On met a jour       
        countDown = countDown - 1 #On decremente
        time.sleep(1) #on attends 1s
        
    GPIO.remove_event_detect(BUTTON_PIN) #On nettoie la queue d'evenements
#-------------------------------------#

#------------------------------------------------------------------------------------------------------------#
#-----! EVENEMENT va renvoyer si un appui a été effectué ou non sur le bouton pour lancer le programme !-----#
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
#------------------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------#
#-----! Fonction principale du programme, c'est la porte d'entrée !-----#
def main(threadName, *args): # *args correspond a un tuple qui peut donc contenir plusieurs arguments quels qu'ils soient, var, string, float, etc.
    Initfolder():
    while True: #Tant que Evenement renvoie TRUE
            pygame.init() #Initialisation de pygame, cela va charger tous les modules
            ecran = pygame.display.set_mode((0,0), pygame.FULLSCREEN) #On créé une fenêtre avec le module display, on met 0,0 en argument avec le flag fullscreen pour que le plein écran fonctionne. (https://zestedesavoir.com/tutoriels/846/pygame-pour-les-zesteurs/1381_a-la-decouverte-de-pygame/creer-une-simple-fenetre-personnalisable/)
            image = pygame.image.load("images/appuyezbouton.jpg").convert_alpha()
            image = pygame.transform.scale(image, (pygame.display.get_surface().get_size()))
            continuer = True
            while continuer:
                ecran.blit(image, (0,0))
                for event in pygame.event.get():
                    if event.type == pygame.KEYUP:
                        continuer = False
                pygame.display.flip()
            pygame.quit()
            Evenement() #Puis on lance (arriere plan) la fonction qui bloque la fonction tant qu'il n'y a pas d'appui
            time.sleep(0.2) #Puis on attends 0.2s
            PrisePhoto() #Puis on lance la fonction TakePictures
    GPIO.cleanup()
#-----------------------------------------------------------------------#

#------------------------------------#
#-----! launch the main thread !-----#
Thread(target=main, args=('Main', 1)).start() # Cela represente la fonction principale du programme. C'est une activite de fil d'execution qui va lancer la fonction main.
#------------------------------------#
