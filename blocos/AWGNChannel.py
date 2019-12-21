import numpy as np

class AWGNChannel:
    def __init__(self, BER=0):
        '''Construtor'''

    def simular(self, sinal_in, potencia_ruido):
        #sinal_saida = np.copy(sinal_in).astype(int)
        sinal_saida = sinal_in + \
            np.sqrt(potencia_ruido) * np.random.randn(1, len(sinal_in))
        return sinal_saida[0]

    #Simula ruido sem aplicar ruido no header (para não arrebentar na desmodulação do hamming )
    def simular_header(self, sinal_in, potencia_ruido, pontos_qpsk=0):
        #sinal_saida = np.copy(sinal_in).astype(int)
        sinal_saida = sinal_in + np.sqrt(potencia_ruido) * np.random.randn(1, len(sinal_in))
        sinal_saida = sinal_saida[0]

        #Simular o canal sem prejudicar o header
        pontos_a_retirar = 11 * 2 * pontos_qpsk
        sinal_saida[0:pontos_a_retirar] = sinal_in[0:pontos_a_retirar]

        return sinal_saida

if __name__ == '__main__':
    ruido = 10**-1
    sinal_entrada = [0, 1, 1, 0, 1, 1, 0, 0]
    canal = AWGNChannel()
    print(canal.simular(sinal_entrada, 2*10))

    