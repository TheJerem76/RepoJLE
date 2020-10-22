#Pour les tests et tuto, voir aussi https://www.w3schools.com/python/default.asp

import picamera #Import des librairies
import pygame #pygame sert à l'affichage
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


# Définition des variables
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
usbfolder = '/media/pi/YELLOW 15GO/Photobooth'
templatePath = os.path.join('Photos', 'Template', "1anSam.jpg") #Path of template image - Va construire le chemin en joignant les paramètres entre quote pour que la variable templatePath soit le document qui sera trouvé en suivant le chemin

ImageShowed = False
Printing = False
BUTTON_PIN = 25
#IMAGE_WIDTH = 558
#IMAGE_HEIGHT = 374
#IMAGE_WIDTH = 550
#IMAGE_HEIGHT = 360
IMAGE_WIDTH = 1100 # Base d'un ratio 16/9 ; utilisé pour un resize en ligne 318
IMAGE_HEIGHT = 619


# Load the background template
bgimage = PIL.Image.open(templatePath) #La variable bgimage ouvre l'image ayant pour nom templatePath

#Setup GPIO
GPIO.setmode(GPIO.BCM) # Cela signifie que le comptage des PIN se fera selon l'approche de numérotation électronique de la carte RPI. Voir https://deusyss.developpez.com/tutoriels/RaspberryPi/PythonEtLeGpio/#LIII-A
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) #BUTTON_PIN est une variable = 25 définie en ligne.35. Ici on set le pin 25 en entrée

# initialise pygame
#Pour info, pygame est un truc qui donne la possibilité d'afficher des éléments à l'écran
pygame.init()  # Initialise pygame - https://devdocs.io/pygame/
myfont = pygame.font.SysFont("monospace", 15) # Je definis mon element texte
pygame.mouse.set_visible(False) #hide the mouse cursor
infoObject = pygame.display.Info() #pygame.display.Info sert à créer un objet d'information video destiné à l'affichage. Il prend pour propriétés ce qu'il trouvera dans current-h et current_y qui sont des attributs de .display.info.  Voir https://devdocs.io/pygame/ref/display#pygame.display.Info
screen = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN) 
''' Full screen ; display.set_mode initialise une fenetre ou écran pour un affichage. Par exemple ici :

Screen est la variable
qui est égal à
écran créé par la fonction pygame.display.set_mode
Et avec comme propriété les tailles suivantes :
En x : infoObject.current_w
En y : infoObject.current_y

infoObject est égal à display.info qui permet l'affichage et qui dispose de plusieurs attributs dont current_w et current_y. Par défaut, quelles sont les valeurs prises par ces attributs ?

pygame.FULLSCREEN correspond à un attribut de fenêtre permettant de retirer les bordures.
'''

background = pygame.Surface(screen.get_size())  # Create the background object ; pygame.Surface va créer un nouvel objet image avec la taille pour arguments. Screen est une variable-
background = background.convert()  # Convert it to a background - Pour que le format de pixel soit identique entre le fond et le background

screenPicture = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen - Idem ç la variable screen
backgroundPicture = pygame.Surface(screenPicture.get_size())  # Create the background object
backgroundPicture = background.convert()  # Convert it to a background - Pour que le format de pixel soit identique entre le fond et le background

transform_x = infoObject.current_w # how wide to scale the jpg when replaying
transfrom_y = infoObject.current_h # how high to scale the jpg when replaying

camera = picamera.PiCamera() #https://picamera.readthedocs.io/en/release-1.12/api_camera.html#picamera
# Initialise the camera object
#camera.resolution = (infoObject.current_w, infoObject.current_h) #la résolution de la caméra prendra heigh and width de l'écran
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


# A function to handle keyboard/mouse/device input events
def input(events):
    for event in events:  # Hit the ESC key to quit the slideshow.
        if (event.type == QUIT or
                (event.type == KEYDOWN and event.key == K_ESCAPE)):
            pygame.quit()

#À quoi sert cette première fonction input ? Simplement à quitter en cas d'appui sur une touche ?
            
# set variables to properly display the image on screen at right ratio
def set_demensions(img_w, img_h): #Fonction utile que dans la fonction show_image pour que la dimention d'afficahge soit correcte.
    # Note this only works when in booting in desktop mode. 
    # When running in terminal, the size is not correct (it displays small). Why?

    # connect to global vars
    global transform_y, transform_x, offset_y, offset_x

    # based on output screen resolution, calculate how to display
    ratio_h = (infoObject.current_w * img_h) / img_w 

    if (ratio_h < infoObject.current_h):
        #Use horizontal black bars
        #print "horizontal black bars"
        transform_y = ratio_h
        transform_x = infoObject.current_w
        offset_y = (infoObject.current_h - ratio_h) / 2
        offset_x = 0
    elif (ratio_h > infoObject.current_h):
        #Use vertical black bars
        #print "vertical black bars"
        transform_x = (infoObject.current_h * img_w) / img_h
        transform_y = infoObject.current_h
        offset_x = (infoObject.current_w - transform_x) / 2
        offset_y = 0
    else:
        #No need for black bars as photo ratio equals screen ratio
        #print "no black bars"
        transform_x = infoObject.current_w
        transform_y = infoObject.current_h
        offset_y = offset_x = 0

def InitFolder(): #Cette fonction semble servir à définir le dossier "images" afin de stoker les photos
    global imagefolder
    global Message
 
    Message = 'Folder Check...'
    UpdateDisplay()
    Message = ''

    #check image folder existing, create if not exists
    if not os.path.isdir(imagefolder):  #Si la fonction os.path.isdir se vérifie, elle renverra TRUE. Donc si le path "Photos" n'existe pas...
        os.makedirs(imagefolder)    #...alors il est créé. En effet, la variable imagefolder correspond au dossier 'Photos' défini en début de programme.
            
    imagefolder2 = os.path.join(imagefolder, 'images') #Construction du path /images (on ajoute /image au path contenu dans imagefolder)
    if not os.path.isdir(imagefolder2): #Si la fonction ne se vérifie pas...
        os.makedirs(imagefolder2) #Alors on créé le chemin contenu dans la variable imagefolder2
        
def DisplayText(fontSize, textToDisplay): # Sert à initialiser la variable Message, Numeral ou CountDownPhoto dans la fonction UpdateDisplay. Comme ça, à l'appel de UpdateDisplay qui vient toujours après l'initialisation de l'une des trois variable, ce qui soit s'afficher s'affichera selon le type de message choisi à travers la variable utilisé.

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
            font = pygame.font.Font(None, fontSize) #pygame.font.Font va cahrger la font d'un fichier défini en attribu. Si le fichier est None, alors la font sera prise par défaut. L'autre attribu correspond à la taille de la font.
            text = font.render(textToDisplay, 1, (227, 157, 200)) #Render créer une nouvelle surface sur laquelle dessiner l'écriture. Impossible d'écrire sur plus qu'une ligne. La surface créée sera de dimentions appropriée à contenir le text. Les atributs sont : Le texte à écrire, un antialias en booleen qui correspond à des bords lisses si c'est à TRUE, la couleur (ici rose car 227 157 200) ainsi qu'en optionnel la couleur de fond du texte (surlignage je pense). La variable text va donc contenir les propriété de choisies. Voir https://devdocs.io/pygame/ref/font#pygame.font.Font.render
            textpos = text.get_rect() #Récupération du rectangle nécessaire à l'afficahge de la variable text http://www.frederic-junier.org/ISN/Cours/tutoriel-pygame.html
            textpos.centerx = background.get_rect().centerx #Positionnement du rectangle http://www.frederic-junier.org/ISN/Cours/tutoriel-pygame.html
            textpos.centery = background.get_rect().centery #Positionnement du rectangle http://www.frederic-junier.org/ISN/Cours/tutoriel-pygame.html
            if(ImageShowed):
                    backgroundPicture.blit(text, textpos) #blit est une fonction de pygame qui superpose text avec textpos
            else:
                    background.blit(text, textpos)
                
def UpdateDisplay(): #Cette fonction va initialiser les variables BackgroundColor, Message, Numeral et CountDownPhoto selon des propriétés de couleurs et taille
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
            text = font.render(Message, 1, (227, 157, 200)) #Modif couleur texte ; font.render va écrire du texte sur une nouvelle "surface"
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
   
    pygame.display.flip() #MàJ pour voir ce qui a été blitté (collé) sur l'écran.
    return


def ShowPicture(file, delay): #Va montrer le cliché pris dans CapturePicture (pas de template ici)
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
    pygame.display.flip()  # update the display - MàJ pour voir ce qui a été blitté (collé) sur l'écran.
    ImageShowed = True
    time.sleep(delay)
    
# display one image on screen
def show_image(image_path): #Fonction chargée d'afficher une image. Elle attend en entrée la variable image_path (path d'un fichier photo) afin de savoir quoi afficher
    screen.fill(pygame.Color("white")) # clear the screen   
    img = pygame.image.load(image_path) # load the image
    img = img.convert() # On converti le format des pixel du fond au même format que celui de l'écran http://www.frederic-junier.org/ISN/Cours/tutoriel-pygame.html
    set_demensions(img.get_width(), img.get_height()) # set pixel dimensions based on image 
    x = (infoObject.current_w / 2) - (img.get_width() / 2)
    y = (infoObject.current_h / 2) - (img.get_height() / 2)
    screen.blit(img,(x,y)) #Va dessiner au sein d'une surface le contenu de img en fonction des positions définies en x et y.
    pygame.display.flip() #MàJ pour voir ce qui a été blitté (collé) sur l'écran.

def CapturePicture(): #Cette fonction est chargée de prendre une cliché et de retourner son nom.
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
    pygame.display.flip() #MàJ pour voir ce qui a été blitté (collé) sur l'écran.
    camera.start_preview() # Lancement de l'aperçu
    BackgroundColor = "black"

    countDown = 6 #On place un temps en secondes dans la variable countDown
    while countDown > 0:      
            BackgroundColor = ""
            Numeral = ""
            Message = "Souriez ! Photo dans " + str(countDown) #On affiche le message + le compteur
            UpdateDisplay()        
            countDown = countDown - 1
            time.sleep(1) 


    for x in range(4, -1, -1): # Pour x compris dans un écart qui commence à 4(optionnal), s'arrête à -1 (required), avec un écart de -1 (optionnal) https://www.w3schools.com/python/ref_func_range.asp
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
        camera.stop_preview() # Fin de l'aperçu
        ShowPicture(filename, 2)
        ImageShowed = False
        return filename
    
    
def TakePictures(): #La fonction va passer plusieurs étapes : Afficher des images informatives (faites votre plus beau sourire) + lancer la fonction CapturePicture, ouvrir la photo prise par cette fonction et la coller sur une autre image (le template thématique) et enfin enregistrer l'image finale et proposer une impression de celle-ci
        global imagecounter
        global imagefolder
        global usbfolder
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


        input(pygame.event.get())
        show_image('images/faites_votre_plus_beau_sourire_rect.png')
        time.sleep(3) #Temps d'affichage de l'image
        #CountDownPhoto = "Prennez la pose et souriez !" #ancienne ligne de code : CountDownPhoto = "1/3"

        
        filename1 = CapturePicture() # La variable filename1 sera égale au résultat obtenu suite au lancement de la fonction CapturePicture, c'est à dire au nom de la photo.

#A la suite de cette ligne, les opératons de placement de la photo sur le template + renommage  + enregistrement de la photo vont se lancer. La partie impression de la photo est également proposée.

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
    
        bgimage.paste(image1, (40, 40))  # Puis on place la photo image1 sur le template thématique (1 an Sam). Plus x est petit, plus l'image est sur la gauche ; y petit = image en haut
        #bgimage.paste(image1, (625, 30))
        #bgimage.paste(image2, (625, 410))
        #bgimage.paste(image3, (55, 410))
        # Create the final filename
        ts = time.time()
        Final_Image_Name = os.path.join(imagefolder, "Final_" + str(TotalImageCount)+"_"+str(ts) + ".jpg")
        # Save it to the usb drive
        bgimage.save(Final_Image_Name)
        Final_Image_Name = os.path.join(usbfolder, "Final_" + str(TotalImageCount)+"_"+str(ts) + ".jpg")
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
        WaitForPrintingEvent() #On lance la fonction. Soit le compte à rebours va jusqu'à la fin, soit un appui est détecté et donc on imprime.
        Numeral = ""
        Message = ""
        print(Printing)
        if Printing: #Si Printing = TRUE
                if (TotalImageCount <= PhotosPerCart): #Si le total d'images prises est inférieur ou égal au total d'image prévues par photos
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
                                if printqueuelength > 1: #S'il y a + qu'un seul élément dans la file d'attente
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
                else: #Sinon, donc si le total d'images prises est supérieur au total d'image prévues par photos
                        Message = "Nous vous enverrons vos photos"
                        Numeral = ""
                        UpdateDisplay()
                        time.sleep(1)
                
        Message = ""
        Numeral = ""
        ImageShowed = False
        UpdateDisplay()
        time.sleep(1)

def MyCallback(channel): #Sert à dire de ne plus détecter d'évènements sur le pin BUTTON_PIN (25 donc) avant de repasser Printing à TRUE
    global Printing
    GPIO.remove_event_detect(BUTTON_PIN)
    Printing=True
    
def WaitForPrintingEvent(): #Chargé de retourner TRUE ou FALSE
    global BackgroundColor
    global Numeral
    global Message
    global Printing #Set à FALSE dans la fonction TakePictures mais sera modifié lors de l'appel à MyCallback
    global pygame
    countDown = 5
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING) #On bloque l'éxécution jusqu'à ce que l'évènement se produise. Voir https://deusyss.developpez.com/tutoriels/RaspberryPi/PythonEtLeGpio/
    GPIO.add_event_callback(BUTTON_PIN, MyCallback)
    
    while Printing == False and countDown > 0: #Tant que Printing = False et que countDown > 0, on exécute la boucle
        if(Printing == True): #Mais si Printing = True...
            return #...alors on retourne TRUE
        for event in pygame.event.get(): #Pour les événements dans la queue...           
            if event.type == pygame.KEYDOWN: #On lit la queue, s'il y a la flèche du bas...                
                if event.key == pygame.K_DOWN: 
                    GPIO.remove_event_detect(BUTTON_PIN) #Alors on retire cet évènement de la queue...
                    Printing = True #...Et on passe Printing à TRUE
                    return #Puis en renvoie TRUE       
        BackgroundColor = "" 
        Numeral = str(countDown) #Sinon on affiche le compte à rebours
        Message = ""
        UpdateDisplay() #On met à jour       
        countDown = countDown - 1 #On décrémente
        time.sleep(1) #on attends 1s
        
    GPIO.remove_event_detect(BUTTON_PIN) #On nettoie la queue d'évènements
        
    
def WaitForEvent(): #Est chargé de retourner TRUE ou FALSE
    global pygame
    NotEvent = True #initialisation de la variable NotEvent à TRUE. Il n'y a pas d'événement.
    while NotEvent: #tant qu'il n'y a pas d'évènement.... Tant que NotEvent est au statut défini au-dessus
            input_state = GPIO.input(BUTTON_PIN) #...alors on va lire le PIN. Correspond à TRUE. La variable input_state correspond à le lecture de l'entrée BUTTON_PIN (25). Voir https://deusyss.developpez.com/tutoriels/RaspberryPi/PythonEtLeGpio/#LIII-A
            if input_state == False: #Si l'état change (appui sur le bouton)...
                    NotEvent = False #Alors on indique cette variable change.           
                    return #On retourne l'état
            for event in pygame.event.get(): #pygame.event.get() va lire les évènements en attente dans la queue ainsi que les y retirer.           
                    if event.type == pygame.KEYDOWN: #Si dans la queue il y a un appui sur la flèche du bas sur le clavier alors on attends 0.2s (fin de la fonction)
                        if event.key == pygame.K_ESCAPE: #Mais si il y a un appui sur la touche echap https://www.pygame.org/docs/ref/key.html#comment_pygame_key_name
                            pygame.quit() #Alors on quitte le programme
                        if event.key == pygame.K_DOWN: #Toutefois s'il y a un appuisur la flèche du bas
                            NotEvent = False #Alors on change l'état et donc on attend 0.2s
                            return #On retourne l'état
            time.sleep(0.2)

def main(threadName, *args): # *args correspond à un tuple qui peut donc contenir plusieurs arguments quels qu'ils soient, var, string, float, etc.
    InitFolder() #Lance la fonction InitFolder c'est ça ? C'est défini tout en haut
    while True: #Tant que WaitForEvent renvoie TRUE
            show_image('images/appuyez4.jpg') #Alors on montre l'image "appuyez4.jpg"...
            WaitForEvent() #Puis on lance (arrière plan) la fonction qui bloque la fonction tant qu'il n'y a pas d'appui
            time.sleep(0.2) #Puis on attends 0.2s
            TakePictures() #Puis on lance la fonction TakePictures
    GPIO.cleanup()


# launch the main thread
Thread(target=main, args=('Main', 1)).start() # Cela représente la fonction principale du programme. C'est une activité de fil d'exécution qui va lancer la fonction main.
