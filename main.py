#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Subitus
Verifica que los audios de locutores concuerde con el texto enviando
03/02/22
'''

import pandas as pd 
import speech_recognition as sr
import os.path
from thefuzz import fuzz
import sys
import difflib
import csv
import os
from pydub import AudioSegment
import shutil

print('Iniciando el programa...')

if getattr(sys, 'frozen', False):
    print('ejecutable')
    BASE_DIR = sys.executable[:-5]
else:
    print('local')
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))


# Ruta de los archivos fuente
PATH_FILES = '{}/archivos/'.format(BASE_DIR)
# Ruta de salida de resultados
PATH_OUTPUT = '{}/salida/'.format(BASE_DIR)

# Verifica si existe la carpeta de salida sino la crea
if(not os.path.exists('{}'.format(PATH_OUTPUT))):
    os.mkdir(PATH_OUTPUT)
else:
    shutil.rmtree(PATH_OUTPUT)
    os.mkdir(PATH_OUTPUT)

# Se inicializa el reconocimiento de voz
r = sr.Recognizer()
# Se lee el archivo audios.CSV
df = pd.read_csv ('{}audios.csv'.format(PATH_FILES))
csv_file_content = []
for index, row in df.iterrows():
    info_csv = []
    print('=================================================')
    text = ''
    path_audio = '{}{}.wav'.format(PATH_FILES,row['Nombre'])
    info_csv.append(path_audio)
    print('Buscando el audio: {}'.format(path_audio))  
    if(os.path.exists('{}'.format(path_audio))):
        print('Analizando el audio...\n\n')
        info_csv.append(row['Texto'])
        try: 
            with sr.AudioFile(path_audio) as source:
                audio = r.record(source)
                text = r.recognize_google(audio, language='es-MX')
            info_csv.append(text)
            texto_free = row['Texto'].replace(',','').replace('.','').replace(':','').replace('(','').replace(')','').lower().strip()
            concordancia = fuzz.ratio(texto_free, text.lower())
            info_csv.append(concordancia)
            print('La concordacia es del: {}'.format(concordancia))
            if concordancia <= 99:
                generador_diferencia = difflib.ndiff(texto_free.splitlines(), text.lower().strip().splitlines())
                difference = difflib.HtmlDiff(tabsize=2, wrapcolumn=50)
                with open("{}diff {}.html".format(PATH_OUTPUT, row['Nombre']), "w") as fp:
                    html = difference.make_file(fromlines=texto_free.splitlines(), tolines=text.lower().strip().splitlines(), fromdesc="Guión", todesc="Audio del locutor")
                    fp.write(html)
            song = AudioSegment.from_wav(path_audio)
            song.export("{}{}.mp3".format(PATH_OUTPUT, row['Nombre']), format="mp3")
        except Exception as e:
            print('Error el cargar el audio: {}'.format(e))
    else:
        print('No existe el archivo!')
        info_csv.append('No existe el archivo!')
    csv_file_content.append(info_csv)
    print('=================================================')

with open('{}relacion.csv'.format(PATH_OUTPUT), mode='w') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['AUDIO','TEXTO ORIGINAL', 'TEXTO DEL AUDIO', 'CONCORDANCIA'])
    for row in csv_file_content:
        csv_writer.writerow(row)
