#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Este NÃO é um programa ROS

from __future__ import print_function, division 

import cv2
import os,sys, os.path
import numpy as np

print("Rodando Python versão ", sys.version)
print("OpenCV versão: ", cv2.__version__)
print("Diretório de trabalho: ", os.getcwd())

# Arquivos necessários
video = "jogovelha.mp4"

def encontra_simbolo(contornos) :
    """0 - vazio
       1 - circulo
       2 - x
    """
    if len(contornos) == 0:
        return 0
    else:
        for contorno in contornos:
            if cv2.contourArea(contorno) > 1000:
                if cv2.contourArea(contorno) > 3000:
                    return 1
                else :
                    return 2


def calcula_vencedor(mat):
    lista_res = []
    lista_explicacao = []

    for p in [1,2]:
        #Regra 1 - mesma linha
        if mat[0,0] == p and mat[0,1] == p and mat[0,2] == p:
            lista_res.append(p)
            lista_explicacao.append("posições: (0,0), (0,1), (0,2)")
        if mat[1,0] == p and mat[1,1] == p and mat[1,2] == p:
            lista_res.append(p)
            lista_explicacao.append("posições: (1,0), (1,1), (1,2)")
        if mat[2,0] == p and mat[2,1] == p and mat[2,2] == p:
            lista_res.append(p)
            lista_explicacao.append("posições: (2,0), (2,1), (2,2)")
        
        #Regra 2 - mesma coluna
        if mat[0,0] == p and mat[1,0] == p and mat[2,0] == p:
            lista_res.append(p)
            lista_explicacao.append("posições: (0,0), (1,0), (2,0)")
        if mat[0,1] == p and mat[1,1] == p and mat[2,1] == p:
            lista_res.append(p)
            lista_explicacao.append("posições: (0,1), (1,1), (2,1)")
        if mat[0,2] == p and mat[1,2] == p and mat[2,2] == p:
            lista_res.append(p)
            lista_explicacao.append("posições: (0,2), (1,2), (2,2)")

        #Regra 3 diagonais
        if mat[0,0] == p and mat[1,1] == p and mat[2,2] == p:
            lista_res.append(p)
            lista_explicacao.append("posições: (0,0), (1,1), (2,2)")
        if mat[0,2] == p and mat[1,1] == p and mat[2,0] == p:
            lista_res.append(p)
            lista_explicacao.append("posições: (0,2), (1,1), (2,0)")

    return lista_res, lista_explicacao
 


if __name__ == "__main__":

    # Inicializa a aquisição da webcam
    cap = cv2.VideoCapture(video)


    print("Se a janela com a imagem não aparecer em primeiro plano dê Alt-Tab")

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if ret == False:
            #print("Codigo de retorno FALSO - problema para capturar o frame")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
            #sys.exit(0)

        # Our operations on the frame come here
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        i_linhas, i_colunas = np.where(gray > 10)
        min_linha = min(i_linhas)
        max_linha = max(i_linhas)
        min_col = min(i_colunas)
        max_col = max(i_colunas)

        rgb = rgb[min_linha:max_linha, min_col:max_col]
        # rgb é nossa imagem sem as margens
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        faixa_min = (0, 200, 200)
        faixa_max = (20/2, 255, 255)
        mask = cv2.inRange(hsv, faixa_min, faixa_max )

        # Pegando as fronteiras das linhas e colunas
        ini_lin0 = 0
        ini_lin1 = int(mask.shape[0] / 3)
        ini_lin2 = int(mask.shape[0] * 2 / 3)
        ini_col0 = 0
        ini_col1 = int(mask.shape[1] / 3)
        ini_col2 = int(mask.shape[1] * 2 /3 )  

        img00 = mask[ ini_lin0:ini_lin1, ini_col0:ini_col1 ]
        img01 = mask[ ini_lin0:ini_lin1, ini_col1:ini_col2 ]
        img02 = mask[ ini_lin0:ini_lin1, ini_col2:]
        img10 = mask[ ini_lin1:ini_lin2, ini_col0:ini_col1 ]
        img11 = mask[ ini_lin1:ini_lin2, ini_col1:ini_col2 ]
        img12 = mask[ ini_lin1:ini_lin2, ini_col2:]
        img20 = mask[ ini_lin2:, ini_col0:ini_col1 ]
        img21 = mask[ ini_lin2:, ini_col1:ini_col2 ]
        img22 = mask[ ini_lin2:, ini_col2:]

        # identificar os contornos vermelhos]
        cont00, tree = cv2.findContours(img00, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cont01, tree = cv2.findContours(img01, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cont02, tree = cv2.findContours(img02, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cont10, tree = cv2.findContours(img10, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cont11, tree = cv2.findContours(img11, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cont12, tree = cv2.findContours(img12, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cont20, tree = cv2.findContours(img20, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cont21, tree = cv2.findContours(img21, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cont22, tree = cv2.findContours(img22, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        
        # preencher uma matriz com os símbolos encontrados
        mat_jogo = np.zeros((3,3))
        mat_jogo[0,0] = encontra_simbolo(cont00)
        mat_jogo[0,1] = encontra_simbolo(cont01)
        mat_jogo[0,2] = encontra_simbolo(cont02)
        mat_jogo[1,0] = encontra_simbolo(cont10)
        mat_jogo[1,1] = encontra_simbolo(cont11)
        mat_jogo[1,2] = encontra_simbolo(cont12)
        mat_jogo[2,0] = encontra_simbolo(cont20)
        mat_jogo[2,1] = encontra_simbolo(cont21)
        mat_jogo[2,2] = encontra_simbolo(cont22)

        # Verificar se as bolas ganham
        resultado, explicacao = calcula_vencedor(mat_jogo)

        # imprimeo resultado do jogo
        if len(resultado) == 0:
            cv2.putText(frame, "Não há vencedor", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
            print("Não há vencedor")
        else :
            for res, expl in zip(resultado, explicacao):
                if res == 1:
                    cv2.putText(frame, "BOLINHAS vencem", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
                    print("BOLINHAS vencem: ", expl)
                elif res == 2:
                    cv2.putText(frame, "X vencem", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
                    print("X vencem: ", expl)

        # NOTE que em testes a OpenCV 4.0 requereu frames em BGR para o cv2.imshow
        cv2.imshow('imagem', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

