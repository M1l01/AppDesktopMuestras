# Importación de Librerias
import os
from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import font, ttk
import cv2
from PIL import Image, ImageTk
import numpy as np
import datetime
import subprocess

#------------------------ Funciones ----------------------------
def imgAjuste(image, brightness=0, contrast=0):
    """
    Parameters:
    - image: The input image.
    - brightness: Value to adjust brightness (-255 to 255).
    - contrast: Value to adjust contrast (-127 to 127).
    """
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow
        image = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)
        image = cv2.addWeighted(image, alpha_c, image, 0, gamma_c)

    return image

def registro():
    global InputNombreReg, InputCantFotos, InputEdad, pathGeneral, lblInfo, btnIniciarCap
    global Cantidad, UserName, Age
    
    UserName, Age, Cantidad = InputNombreReg.get(), InputEdad.get(), InputCantFotos.get() #Obtencion de Variables de la Interfaz

    ContNums = 0
    
    if not UserName or not Cantidad or not Age:
        lblInfo.config(text="*Uno o mas de los espacios del formulario esta vacío",
                       fg="red")
        lblInfo.place(x=120, y=475)
        #print("Uno o mas de los espacios del formulario esta vacío")
    else:
        for c in Cantidad + Age:
            codAscii = ord(c)
            #print(f"Ascii: {codAscii}")
            if codAscii >= 48 and codAscii <= 57:
                ContNums = ContNums + 1
                #print("Caracter Correcto")
            else:
                print(f"Caracter Incorrecto: '{c}'")

        if ContNums == len(Cantidad)+len(Age):
            lblInfo.config(text="*Cuestionario Completo Correctamente",
                        fg="green")
            lblInfo.place(x=120, y=475)
            #print("Cuestionario Completo Correctamente")
            for l in UserName:
                if l == " ":
                    arrayUserName = UserName.split(l)
                    UserName = ""
                    for element in arrayUserName:
                        if element == arrayUserName[0]:
                            UserName = UserName + element
                        else:
                            UserName = UserName + "_" + element
            Cantidad = int(Cantidad) + 22 #Transformamos la variable cantidad a entero
            Age = int(Age)

            if Age >= 12 and Age <= 80:
                #Verificacion de Usuario Registrado Anteriormente
                ListNames = os.listdir(pathGeneral)
                #print(ListNames)
                Names = []

                #Checking de Lista
                for name in ListNames:
                    Names.append(name)
                    #print(name)
                if UserName in Names:
                    #Usuario registrado Anteriormente
                    lblInfo.config(text="*Usuario Registrado Anteriormente",
                                fg="red")
                    lblInfo.place(x=120, y=475)
                else:
                    #Usuario NO registrado
                    os.makedirs(pathGeneral + f"//{UserName}")
                    horafecha = str(datetime.datetime.now())
                    horafecha = horafecha.split(" ")[0]

                    archText = open(f"{pathGeneral}//{UserName}//{UserName}.txt", "w")
                    archText.write(f"{UserName}, {Age}, {Cantidad-22}, {horafecha}")
                    archText.close()

                    btnIniciarCap.config(state="normal")
                    btnRegistrar.config(state="normal")

                    lblInfo.config(text="*Usuario Registrado con Exito",
                                fg="green")
                    lblInfo.place(x=150, y=475)

                    print(f"Usuario {UserName} Registrado")
            else:
                lblInfo.config(text="*Edad Incorrecta",
                        fg="red")
                lblInfo.place(x=40, y=440)
        else:
            lblInfo.config(text="*Cuestionario Completo Incorrectamente",
                        fg="red")
            lblInfo.place(x=120, y=475)
            #print("Cuestionario Completo Incorrectamente")

def VideoCaptura():
    global video, btnIniciarCap, cmbCamaras, tupCams, lblInfo, btnRegistrar
    caminput = cmbCamaras.get()
    print(caminput)

    lblInfo.config(text="Captura en proceso...",
                    fg="green")
    lblInfo.place(x=175, y=475)

    btnRegistrar.config(state="disabled")
    
    for cam in tupCams:
        print(cam)
        if caminput == cam[1]:
            camidx = cam[0]
    print(f"Camara Escogida {camidx}")
    
    video = cv2.VideoCapture(camidx)
    print("Camara Iniciada")
    
    IniciarCamara()

def IniciarCamara():
    global video, contador, UserName, Cantidad, pathGeneral, CantMuestras

    carpeta = pathGeneral + f"//{UserName}//Fotos_Muestra{CantMuestras+1}" #Ruta para la toma de muestras segun el usuario
    
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
        print(f"Carpeta Creada para {UserName}")

    if video.isOpened():
        ret, frame = video.read()
        if ret:
            if contador <= Cantidad:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    #Cambio Contraste
                frame_eq = imgAjuste(gray, brightness=-130, contrast=33)

                median_bluerred = cv2.medianBlur(frame_eq, 3)

                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                enhanced_clahe = clahe.apply(median_bluerred)

                sharp_kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
                sharpened = cv2.filter2D(enhanced_clahe, -1, sharp_kernel)

                smoothed = cv2.GaussianBlur(sharpened, (3,3), 0)

                if contador > 22:
                    fotoMuestra = smoothed.copy()
                    cv2.imwrite(carpeta + f"//Foto_{contador-22}.png", fotoMuestra)
                    
                #Mostrar imagen en pantalla
                img = Image.fromarray(smoothed)
                image = ImageTk.PhotoImage(image=img)
                lblVideo.configure(image=image)
                lblVideo.image = image
                lblVideo.after(10, IniciarCamara)
                    
                contador = contador + 1

            else:
                CantMuestras = CantMuestras + 1
                print(f"Cantidad de Muestras: {CantMuestras}")
                DetenerCamara()
                resetParameters()
        else:
            DetenerCamara()
            resetParameters()
    else:
        DetenerCamara()
        resetParameters()

def DetenerCamara():
    global video, lblVideo
    if video:
        lblVideo.image = np.zeros((640, 480))
        video.release()
        video = None
        

def resetParameters():
    global InputNombreReg, InputCantFotos, InputEdad, contador, btnIniciarCap, CantMuestras, cmbCantidadMuestras, lblInfo
    
    InputCantMuestras = cmbCantidadMuestras.get()
    InputCantMuestras = int(InputCantMuestras)

    #print(f"Cantidad de Muestras Seleccionadas: {InputCantMuestras}")

    if CantMuestras == InputCantMuestras:
        lblInfo.config(text="Toma de muestra Concluida", fg="#030a71")
        lblInfo.place(x=165,y=475)
        btnIniciarCap.config(state="disabled")
        btnRegistrar.config(state="normal")
        InputNombreReg.delete(0, END)
        InputCantFotos.delete(0, END)
        InputEdad.delete(0, END)
        CantMuestras = 0

    else:
        #btnRegistrar.config(state="disabled")
        lblInfo.config(text="Coloque la otra mano para segunda muestra", fg="#030a71")
        lblInfo.place(x=115, y=475)

    contador = 1

def seleccionRuta():
    global pathGeneral, btnRegistrar, lblpathGeneral
    pathGeneral = filedialog.askdirectory()
    if pathGeneral:
        btnRegistrar.config(state="normal")
        lblpathGeneral.config(text="*Path Seleccionado", fg="green")
    print(f"Seleccionar la Ruta {pathGeneral}, {type(pathGeneral)}")

def listar_camaras():
    # Comando para listar dispositivos de vídeo
    comando = "wmic path Win32_PnPEntity where \"Service like 'usbvideo%'\" get Name"
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
    dispositivos = resultado.stdout.strip().split('\n')
    
    # Filtrar y limpiar la lista de dispositivos
    dispositivos = [dispositivo.strip() for dispositivo in dispositivos if dispositivo.strip() and dispositivo.strip() != 'Name']

    camaras = []
    for i in range(5):
        captura = cv2.VideoCapture(i)
        if captura.isOpened():
            camaras.append((i, dispositivos[i] if i<len(dispositivos) else f"Camara {i}"))
            captura.release()
    
    return camaras, dispositivos

#-------------------------------  Interfaz --------------------------------

#Variables para la Captura
pathGeneral = ""
contador = 1
Cantidad = ""
CantMuestras = 0
tupCams, CamDisp = listar_camaras()

#Creacion de la Interfaz
ventana = Tk()
ventana.title("Toma de Muestras Prototipo")
ventana.geometry("1200x700")

video = None

#Input Texto
InputNombreReg = ttk.Entry(ventana, style="MyEntry.TEntry", font=font.Font(family="Calisto MT", size=11))
InputNombreReg.place(x=40, y=320, width=350)

InputEdad = ttk.Entry(ventana, style="MyEntry.TEntry", font=font.Font(family="Calisto MT", size=11))
InputEdad.place(x=40, y=410, width=150)

InputCantFotos = ttk.Entry(ventana, style="MyEntry.TEntry", font=font.Font(family="Calisto MT", size=11))
InputCantFotos.place(x=300, y=410, width=150)

#Botones
btnRegistrar = tk.Button(ventana, text="Registrar", state="disabled" ,bg = "#030a71", fg="white" ,relief="flat",
                      cursor="hand2", command=registro, font=("Calisto MT", 12, "bold"))
btnRegistrar.place(x=50, y=575, width=150, height=45)

btnIniciarCap = tk.Button(ventana, text="Iniciar Captura", state="disabled", bg = "#030a71", fg="white",
                          relief="flat", cursor="hand2", command=VideoCaptura, font=("Calisto MT", 12, "bold"))
btnIniciarCap.place(x=300, y=575, width=150, height=45)

btnSelectDir = tk.Button(ventana, text="Buscar", bg="#030a71", fg="white",
                         cursor="hand2", command=seleccionRuta, font=("Calisto MT", 10, "bold"))
btnSelectDir.place(x=30, y=30, width=100, height=30)

#Labels
lblpathGeneral = tk.Label(ventana, text="*Seleccione un Directorio", fg="red",
                        font=("Calisto MT", 9, "bold"))
lblpathGeneral.place(x=140, y=35)

lblTitleVentana = tk.Label(ventana, text="Obtención de Muestras", fg="black",
                           font=("Calisto MT", 28, "bold"))
lblTitleVentana.place(x=80, y=120)

lblVideo = tk.Label(ventana, bg="black")
lblVideo.place(x=525, y=150, width=640, height=480)

lblVideoTxt = tk.Label(ventana, text="Captura de Video", fg="black",
                       font=("Calisto MT", 20, "bold"))
lblVideoTxt.place(x=750, y=100)

lblInputName = tk.Label(ventana, text="Introduce el Nombre", fg="black",
                        font=("Calisto MT", 14, "bold"))
lblInputName.place(x=40, y=280)

lblInputCantidad = tk.Label(ventana, text="Cantidad de Fotos", fg="black",
                        font=("Calisto MT", 14, "bold"))
lblInputCantidad.place(x=295, y=370)

lblInputEdad = tk.Label(ventana, text="Edad" ,fg="black",
                        font=("Calisto MT", 14, "bold"))
lblInputEdad.place(x=40, y=370)

lblInfo = tk.Label(ventana, text="", fg="black",
                    font=("Calisto MT", 10, "bold"))
lblInfo.place(x=120, y=475)

lblLinea = tk.Label(ventana, text="", bg="black")
lblLinea.place(x=250, y=525, width=1, height=150)

lblSelectCamara = tk.Label(ventana, text="Selecciona tu cámara", fg="black",
                           font=("Calisto MT", 10, "bold"))
lblSelectCamara.place(x=100, y=220)

lblCantidadMuestras = tk.Label(ventana, text="Cantidad de Muestras", fg="black",
                               font=("Calisto MT", 10, "bold"))
lblCantidadMuestras.place(x=300, y=220)

#Combo Camaras - Seleccionar
cmbCamaras = ttk.Combobox(ventana, values=CamDisp, state="readonly")
cmbCamaras.current(0)
cmbCamaras.place(x=90, y=200)

cmbCantidadMuestras = ttk.Combobox(ventana, values=[2,1], state="readonly")
cmbCantidadMuestras.current(0)
cmbCantidadMuestras.place(x=340, y=200, width=50)

ventana.mainloop()