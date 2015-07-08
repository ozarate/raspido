#!/usr/bin/python

import os
from array import array
import socket
import time
import threading
import sys
import glob
from datetime import datetime
import subprocess
import RPi.GPIO as GPIO
from multiprocessing import Process
import signal

#FICHEROS

dirOrigen = "/home/pi/ftpDocuments/" #directorio origen de los archivos
ext="*.sb" #extension de los archivos a ejecutar

#PULSADOR

botonPulsado=False
GPIO.setmode(GPIO.BOARD) #GPIO modo BOARD

boton=13 #pin pulsador
GPIO.setup(boton, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#LED

ledVerde = 15 #pin led verde
ledRojo = 11 #pin led rojo

GPIO.setup(ledVerde, GPIO.OUT)
GPIO.setup(ledRojo, GPIO.OUT)

# LEDS - hilos y funciones

class ledVerdeBlink(threading.Thread):
  def _init_(self):
    threading.Thread._init_(self)

  def run(self):
    for i in range (0,3):
      GPIO.output(ledVerde, GPIO.HIGH)
      time.sleep(0.5)
      GPIO.output(ledVerde, GPIO.LOW)
      time.sleep(0.5)
    GPIO.cleanup

class ledRojoBlink(threading.Thread):
  def _init_(self):
    threading.Thread._init_(self)

  def run(self):
    for i in range (0,3):
      GPIO.output(ledRojo, GPIO.HIGH)
      time.sleep(0.5)
      GPIO.output(ledRojo, GPIO.LOW)
      time.sleep(0.5)
    GPIO.cleanup
  
def rojoBlink():
    for i in range (0,3):
      GPIO.output(ledRojo, GPIO.HIGH)
      time.sleep(0.5)
      GPIO.output(ledRojo, GPIO.LOW)
      time.sleep(0.5)
    GPIO.cleanup


#SCRATCH

msg='raspido' #mensaje de broadcast. En scratch al recibir msg se inicia ejecucion

PORT = 42001 #puerto scratch
HOST = '127.0.0.1' #localhost


'''Crea un socket para comunicarse con Scratch. En caso de fallo actualiza
variable checkSocket a False, en caso contrario la actualiza a True.'''

def sockectScratch(timeout):   
    global scratchSock
    global checkSocket

    try:
        print("Connecting...")
        time.sleep(timeout)
        scratchSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        scratchSock.connect((HOST, PORT))

        
    except Exception as e:
        print e
        checkSocket=False
        #GPIO.output(ledRojo,True)
        #GPIO.output(ledVerde,False)
    else:
        checkSocket=True
        print("Connected!")
          
'''Funcion para enviar comando de broadcast + msg via el socket
a scratch. Antes de enivar el comando comprueba que el socket esta
activo, y en casod e fallo reintenta la creacion del socket.
'''
def sendScratchCommand(cmd):

    if checkSocket == True:
      n = len(cmd)
      a = array('c')
      a.append(chr((n >> 24) & 0xFF))
      a.append(chr((n >> 16) & 0xFF))
      a.append(chr((n >>  8) & 0xFF))
      a.append(chr(n & 0xFF))
      scratchSock.send(a.tostring() + cmd)
    else:
      sockectScratch(4)
      sendScratchCommand('broadcast "' + msg + '"')

#WAIT BUTTON
'''Espera a pulsacion del boton.
Tres tipos de pulsacion:
- Corta (pulsacionCorta): menos de 1 segundo
- Larga (pulsacionLarga): entre 1 y 3 segundos
- Muy larga (pulsacionOff): mas de 3 segundos
'''
    
def waitButton(boton):
    
    global pulsacionCorta
    global pulsacionLarga
    global pulsacionOff

    print "Waiting..."
    time.sleep(3)
    GPIO.output(ledRojo,False)
    GPIO.output(ledVerde,True)
    
    GPIO.remove_event_detect(boton)
    GPIO.wait_for_edge(boton, GPIO.BOTH)
    stamp = time.time()
    GPIO.remove_event_detect(boton)
    GPIO.wait_for_edge(boton, GPIO.BOTH)
    now = time.time()
    if now-stamp > 3:
        print "Pulsacion muy larga"
        pulsacionCorta=False
        pulsacionLarga=False
        pulsacionOff=True

    elif now-stamp > 1:
        print "Pulsacion larga"
        pulsacionCorta=False
        pulsacionLarga=True
        pulsacionOff=False

    else:
        print "Pulsacion corta"
        pulsacionCorta=True
        pulsacionLarga=False
        pulsacionOff=False


''' Bucle de ejecucion:
Espera pulsador/boton
Variables: botonPulsado= true/false
En caso de ser pulsado, recibe tipo de pulsacion
Si:
- Larga (pulsacionLarga): cerrar scratch
  botonPulsado=false
  
- Muy larga (pulsacionOff): detener programa

- Corta (pulsacionCorta):
  si es la primera vez que se pulsa (botonPulsado=false):
    se abre scratch y se ejecuta el archivo sb mas actual del directorio
  si ya se habia ejecutado scratch antes:
    ejecuta el comando
'''

while True:

    waitButton(boton)
    
    try:

        if pulsacionLarga:
            botonPulsado=False
            GPIO.output(ledVerde,False)
            print ("Closing scratch...")
            rojoBlink()
            os.system('pkill squeak')

        elif pulsacionOff:
          GPIO.output(ledRojo,True)
          time.sleep(1)
          GPIO.cleanup() 
          os.system('pkill squeak')
          os._exit(0)
              
        else:
            if (botonPulsado==False):
              botonPulsado = True
              print "Opening file..."
              ledVerdeBlink().start() #hilo led verde
              files = glob.iglob(os.path.join(dirOrigen, ext))
              diccionario={}
              for f in files:
                tiempo = os.path.getmtime(f)
                diccionario[f]= tiempo
              inverse = [(value,key) for key, value in diccionario.items()]
              ficheroReciente = max(inverse)[1]
              os.system('/usr/bin/scratch.old ' + ficheroReciente  + ' &')
              print ficheroReciente
	      sockectScratch(2)
              sendScratchCommand('broadcast "' + msg + '"')

            else:  
              botonPulsado = True
              GPIO.output(ledVerde,False)
              ledVerdeBlink().start() #hilo led verde
              sendScratchCommand('broadcast "' + msg + '"')
           
            
    except KeyboardInterrupt:
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit

GPIO.cleanup() 
