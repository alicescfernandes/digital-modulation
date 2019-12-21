import numpy as np;
from scipy.special import erfc

def erro_quantizacao(sinal,sinal_quantificado):
    """
    Calcula um sinal que corresponde ao erro de quantificacao
    """
    return sinal-sinal_quantificado

def teste():
    print(1)

def n0(sigma_quadrado):
    '''
    Calcular N0 (com o ruido do canal - sigma ao quadrado)
    '''
    return sigma_quadrado * 2

def snr_uniforme(R, Potencia, Vmax):
    """
    Aplica formula de calculo do SNR do Quantificador Uniforme
    
    R: Numero de bits
    P: Potencia do sinal
    Vmax: Voltagem máxima do sinal
    """
    return 6.02 * R + 10 * np.log10(3 * (Potencia / Vmax**2))

def snr_nao_uniforme(R):
    """
    Aplica formula de calculo do SNR na quantificação não uniforme, de acordo com a lei µ
    R: Numero de bits
    """
    return 6 * R - 10

#SNR em DB (P sinal / P ruido) convertido a db
def snr_pratico(sinal, erro):
    '''
    Calcula a SNR prática em função de dois sinais
    '''
    return 10 * np.log10( np.sum(sinal ** 2) / np.sum(erro ** 2) )


def potencia(sinal):
    '''
    Calcular a potencia do sinal
    '''
    return np.sum( (sinal ** 2) / len(sinal) )


def ber_hamming(n, k, ber):
    '''
    Calcula o BER de acordo com o Código de Hamming
    '''
    r_c = k / n
    ber_linha = (3 * (n-1) / 2) * (ber ** 2)
    return ber_linha

def ber_repeticao(n,ber):
    '''
    Calcula o BER de acordo com o Código de Repeticao
    '''
    r_c = 1 / n
    s = 1
    k = int(n+1/2)  # 2+1/2 = 1.5
    ber_linha = (np.math.factorial(n) / (np.math.factorial(s)  * np.math.factorial(k))) * ber**(n+1/2)
    return ber_linha

def ber_paridade(n,ber):
    '''
    Calcula o BER de acordo com o Código de Paridade
    '''
    r_c = (n-1)/n #Razão código
    ber_linha = (n-1) * (ber**2)
    return ber_linha

def ber_pratico(sinal_1,sinal_2):
    bits_errados = np.sum(np.logical_xor(sinal_1, sinal_2))
    ber = bits_errados / len(sinal_1)
    return ber;

def eb_qpsk(A,Tb):
    '''
    Calcula Energia de bit da modulacao QPSK
    '''
    return 1/2 * (A**2) * Tb


def bt_qpsk(alpha, Rb):
    '''
    Calcula largura de banda QPSK
    '''
    return Rb/2 * (1+alpha)


def ber_qpsk(Eb,n_0):
    '''
    Calcula o BER de acordo com a modulação QPSK
    '''
    if(n_0 ==0 ): return 0
    return 1/2 * erfc(np.sqrt(Eb/n_0))


