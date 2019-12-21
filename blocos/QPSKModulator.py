import numpy as np
from blocos.ADC_DAC import ADC_DAC
#from ADC_DAC import ADC_DAC

import time
class QPSKModulator:
    def __init__(self):
        self.Rs = 1
        self.Ts = 1/self.Rs
        self.P = 8

        ''' Construtor '''
        # self.Eb = Eb #Energia média por bit
        # self.P = P #Pontos por símbolo
        # self.Fc = Fc #Frequencia Portadora

        # Para QSPK, os simbolos são 00,01,10,11. Cada um desses simbolos vão corresponder
        # a uma fase (ver gráfico de fases),
        # e é com essa fase que se modula a sinusoide

        self.tabelas_cos = {
            0: np.pi/4,  # 00 #1 q
            1: (3 * np.pi)/4,  # 01 # 2 q
            2: (7 * np.pi)/4,  # 10 # 3 q
            3: (5 * np.pi)/4,  # 11 #4 q
        }

        tempo = np.arange(0, self.Ts,  1/self.P)

        self.tabelas_cos2 = {
            0: np.cos(2 * np.pi * self.Rs * tempo + np.pi/4),  # 00 #1 q
            1: np.cos(2 * np.pi * self.Rs * tempo + (3 * np.pi)/4),  # 01 # 2 q
            2: np.cos(2 * np.pi * self.Rs * tempo + (7 * np.pi)/4),  # 10 # 3 q
            3: np.cos(2 * np.pi * self.Rs * tempo + (5 * np.pi)/4),  # 11 #4 q
        }

        self.tabelas_cos3 = {
            "00": np.cos(2 * np.pi * self.Rs * tempo + np.pi/4),  # 00 #1 q
            "01": np.cos(2 * np.pi * self.Rs * tempo + (3 * np.pi)/4),  # 01 # 2 q
            "10": np.cos(2 * np.pi * self.Rs * tempo + (7 * np.pi)/4),  # 10 # 3 q
            "11": np.cos(2 * np.pi * self.Rs * tempo + (5 * np.pi)/4),  # 11 #4 q
        }

    #FIX: Send a header, telling the bits to be cut on decode
    def modular(self, sinal_entrada, Eb, P):
        sinal_entrada = np.array(sinal_entrada)
        # Para cada par de dois bits, calcular um arange de uma sinusoide de P pontos e concatenar numa array final
        # para ser mais rápido: calcular tamanho do sinal transmitido para evitar appends, e depois só substituir nos indexes
        self.Eb = Eb
        bits_to_be_cut = len(sinal_entrada) % 2

        if(bits_to_be_cut > 0):
            sinal_entrada = np.append(sinal_entrada, np.zeros(bits_to_be_cut))

        sinal_entrada = sinal_entrada.astype(int)
        tempo = np.arange(0, self.Ts,  1/self.P)

        amplitude = np.sqrt((2 * Eb) / self.Ts)

        start_time = time.time()       
        a6 = ["".join(map(str,sinal_entrada[k:k+2])) for k in range(0,len(sinal_entrada),2) ] #Using strings para mapear simbolos
        a5 = [self.tabelas_cos3[x] for x in a6] #mapear fases
        a6 = np.array([amplitude * fase for fase in a5]) #multiplicar fases
        a6 = a6.reshape(len(a6) * len(a6[0])) #Reshape is faster than the for loop below
        print("--- %s mod 2 qpsk segundos ---" % (time.time() - start_time))

        #start_time = time.time()
        #b2 = adc_dac.descodificar(sinal_entrada, 2)
        #t_amostras = np.zeros(len(tempo) * len(b2))
        #i = 0;
        #for x in b2:
        #    fase = self.tabelas_cos[x]
        #    t_amostras[i:i+8] =  amplitude * np.cos(2 * np.pi * 

        #print("--- %s ccc segundos ---" % (time.time() - start_time))
        #print(np.array_equal(a4,a6))
        return a6

    # TP3 - Pergunta 2
    def desmodular(self, sinal_recetor):
        # No desmodulador: teoricamente...
        P = self.P

        tempo = np.arange(0, 1 * len(sinal_recetor) / P, 1/P)

        # Multiplicar por uma sin e um cos
        sinal_recetor_sin = sinal_recetor * (np.sqrt(2 * 1) * np.sin(2*np.pi * 1 * tempo) * -1)
        sinal_recetor_cos = sinal_recetor * (np.sqrt(2 * 1) * np.cos(2*np.pi * 1 * tempo))

        a = np.zeros(int(len(sinal_recetor_sin) / P))
        b = np.zeros(int(len(sinal_recetor_cos) / P))

        #start_time = time.time()

        for (s, i) in zip(range(0, len(sinal_recetor_sin), P), range(0, len(a))):
            a[i] = np.sum(sinal_recetor_sin[s:s+P])
            b[i] = np.sum(sinal_recetor_cos[s:s+P])

        #print("--- %s ccc segundos ---" % (time.time() - start_time))

        a = a * (2/P)
        b = b * (2/P)

        self.sin = np.copy(a)
        self.cos = np.copy(b)

        # Calcular o sinal
        a[a > 0] = 0
        a[a < 0] = 1
        b[b > 0] = 0
        b[b < 0] = 1

        sinal_desmodulado = np.array([[a[k], b[k]] for k in range(0, len(a))])

        sinal_desmodulado = sinal_desmodulado.reshape(
            len(sinal_desmodulado) * len(sinal_desmodulado[0]))

        # e se a multiplicacao por sin for positivo, então simbolo[1] é 0, senão é 1
        # e se a multiplicacao por cos for positivo, então simbolo[0] é 0, senão é 1

        # No sinal discreto, fazer um somatorio a cada 8 bits e multiplicar por sin e cos e reconstruir o simbolo através disso
        # calcular o numero total de itens, e fazer só put a cada 8 bits

        return sinal_desmodulado
        # OLD-Para cada dois bits (simbolo), multiplicar por uma sin e um cos

    def constelacao(self):
        return self.sin, self.cos

def testar():
    modulador = QPSKModulator()
    sinal_a_modular = [0, 0, 0, 1, 1, 0, 1, 1]
    sinal_a_modular = [0, 0]

    sinal_a_modulado = modulador.modular(sinal_a_modular, 4, 8)
    sinal_desmodulado = modulador.desmodular(sinal_a_modulado)
    print(sinal_desmodulado, np.array_equal(
        sinal_a_modular, sinal_desmodulado))

def stress_test():
    modulador = QPSKModulator()
    # Stress Test
    numero_elementos = 2**18 # 50331648   # 2**4
    print("testar com", numero_elementos, "elementos")
    sinal_a_modular = np.random.randint(0, 2, numero_elementos)
    start_time = time.time()
    sinal_a_modulado = modulador.modular(sinal_a_modular, 4, 8)
    print("--- %s segundos a modular ---" % (time.time() - start_time))

    start_time = time.time()
    sinal_desmodulado = modulador.desmodular(sinal_a_modulado)
    print("--- %s segundos a desmodular ---" % (time.time() - start_time))

#testar()
#stress_test()
