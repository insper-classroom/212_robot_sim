#! /usr/bin/env python3
# -*- coding:utf-8 -*-

# Rodar com 
# roslaunch my_simulation rampa.launch


from __future__ import print_function, division
import rospy
import numpy as np
import numpy
import math
import cv2
import time
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image, CompressedImage, LaserScan
from sensor_msgs.msg import Imu
from cv_bridge import CvBridge, CvBridgeError
from numpy import linalg
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped
from tf import transformations

from nav_msgs.msg import Odometry
from std_msgs.msg import Header


import visao_module


bridge = CvBridge()

cv_image = None
media = []
centro = []

area = 0.0 # Variavel com a area do maior contorno

resultados = [] # Criacao de uma variavel global para guardar os resultados vistos

x = 0
y = 0
z = 0 
id = 0

leituras = [] # Guarda as leituras do laser

angulos = None # Variável que guarda os angulos da IMU

def leu_imu(dado):
    global angulos
    quat = dado.orientation
    lista = [quat.x, quat.y, quat.z, quat.w]
    angulos = np.degrees(transformations.euler_from_quaternion(lista))
    mensagem = """
	Tempo: {:}
	Orientação: {:.2f}, {:.2f}, {:.2f}
	Vel. angular: x {:.2f}, y {:.2f}, z {:.2f}\

	Aceleração linear:
	x: {:.2f}
	y: {:.2f}
	z: {:.2f}

    """.format(dado.header.stamp, angulos[0], angulos[1], angulos[2], dado.angular_velocity.x, dado.angular_velocity.y, dado.angular_velocity.z, dado.linear_acceleration.x, dado.linear_acceleration.y, dado.linear_acceleration.z)
    print(mensagem)


def scaneou(dado):
    global leituras
    print("Faixa valida: ", dado.range_min , " - ", dado.range_max )
    print("Leituras:")
    print(np.array(dado.ranges).round(decimals=2))
    leituras = dado.ranges
	#print("Intensities")
	#print(np.array(dado.intensities).round(decimals=2))

# A função a seguir é chamada sempre que chega um novo frame
def roda_todo_frame(imagem):
    print("frame")
    global cv_image
    global media
    global centro
    global resultados

    now = rospy.get_rostime()
    imgtime = imagem.header.stamp
    lag = now-imgtime # calcula o lag
    delay = lag.nsecs

    try:
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        cv_image = temp_image.copy()
        centro, media, resultados = visao_module.identifica_cor(cv_image)
        # ATENÇÃO: ao mostrar a imagem aqui, não podemos usar cv2.imshow() dentro do while principal!! 
        cv2.imshow("cv_image", cv_image)
        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)
    
if __name__=="__main__":
    rospy.init_node("Q3")

    topico_imagem = "/camera/image/compressed"

    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)
    recebedor_laser = rospy.Subscriber("/scan", LaserScan, scaneou)
    recebe_scan = rospy.Subscriber("/imu", Imu, leu_imu)

    print("Usando ", topico_imagem)

    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)

    tolerancia = 25

    try:
        v_cruzeiro = 0.2
        # Insight do Adney:
        # Mesmo em manobra de desvio, o robô não pode parar repentinamente pois deslizaria 
        v_desvio = 0.07
        w_desvio = 0.15

        while not rospy.is_shutdown():

            # Inicializando - por default anda em frente com uma velocidade não muito alta
            vel = Twist(Vector3(v_cruzeiro, 0, 0), Vector3(0, 0, 0))

            # Sensor de menor prioridade
            # Usando a imagem para saber se tenho que alinhar o robô
            # É útil se o desvio não é muito grande e não estou muito próximo à parede
            # Proporciona um alinhamento fino
            if media is not None and len(media) > 0 and media[0] > centro[0] + 50 :
                vel = Twist(Vector3(v_desvio,0,0), Vector3(0,0,-w_desvio))
            elif media is not None and len(media) > 0 and media[0] < centro[0] - 50:
                vel = Twist(Vector3(v_desvio,0,0), Vector3(0,0,w_desvio))

            # Sensor de prioridade média: pode sobrescrever os comandos obtidos com a câmera
            # Se estiver lateralmente muito próximo à parede, gira no sentido de se afastar
            # A proximidade máxima admitida é 30 cm
            if leituras is not None and len(leituras) > 0 and leituras[90] < 0.3:
                # A parede está próxima à esquerda do robô, tem que girar à direita
                vel = Twist(Vector3(v_desvio,0,0), Vector3(0,0,-w_desvio))
            elif leituras is not None and len(leituras) > 0 and leituras[270] < 0.3:
                # A parede está próxima à direita do robô, tem que girar à direita
                vel = Twist(Vector3(v_desvio,0,0), Vector3(0,0,w_desvio))

            # Usando o laser para parar o robô se houver algum obstáculo logo à frente
            if leituras is not None and len(leituras) > 0 and leituras[0] < 0.2:
                vel = Twist(Vector3(0,0,0), Vector3(0,0,0))

            # Sensor de prioridade máxima: verifica a orientação absoluta do robô
            # Caso o desvio seja muito grande, tenta girar no sentido contrário até se recuperar
            if angulos is not None and angulos[2] > 30:
                vel = Twist(Vector3(v_desvio,0,0), Vector3(0,0,-w_desvio))
            elif angulos is not None and angulos[2] < -30:
                vel = Twist(Vector3(v_desvio,0,0), Vector3(0,0,w_desvio))

            # Publica a velocidade resultante
            velocidade_saida.publish(vel)

            rospy.sleep(0.1)

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")


