import numpy as np
import time
import matplotlib.pyplot as plt
from PIL import Image

#Import blocos para montar sistema
from blocos.ADC_DAC import ADC_DAC #Codificador int-bit /  bit-int
from blocos.UniformQuantizer import UniformQuantizer
from blocos.QPSKModulator import QPSKModulator
from blocos.AWGNChannel import AWGNChannel
from blocos.UniformQuantizer import UniformQuantizer
from blocos.Utils import * # Bad practice i know, but is only utilitary functions
from blocos.Hamming1511 import Hamming1511

def simulate_system(sinal,R=8, com_correcao_erros=False,ruido = 10**-1):    
    Vmax = np.max(sinal)
    R_codificacao = R
    pontos = 8
    energia_bit = 4;
    N0 = n0(ruido)

    qpsk = QPSKModulator();
    canal = AWGNChannel();
    quantificador = UniformQuantizer(R, Vmax, "midrise")
    dac = ADC_DAC()
    hamming = Hamming1511()
    
    #No ambito deste trabalho:
    # 1. Amostrar Sinal
    # 2. Quantificar sinal
    #print("2. Quantificar sinal")
    (sinal_q,niveis_sinal_q) = quantificador.quantificar(sinal)

    #<--- Calcular SNR Quantificacao Teórico
    snr_teorico = snr_uniforme(R, potencia(sinal), Vmax)

    # 3. Codifificar sinal (converter para binário)    
    sinal_q_c = dac.codificar(niveis_sinal_q,R_codificacao)
    ber_hamming_teorico = None
    
    if(com_correcao_erros):
        # 4. Adicionar Hamming 
        #print("4. Adicionar Hamming ")
        sinal_q_c_h =  hamming.codificar(sinal_q_c)
        #<--- Calcular BER Hamming Teórico (ber')
        #ber_hamming_teorico = ber_hamming(11,15,ruido)
        
    else:
        sinal_q_c_h = sinal_q_c
    
    # 5. Modular sinal
    (sinal_q_c_h_qpsk) = qpsk.modular(sinal_q_c_h, energia_bit,pontos)   
   
    #<-- Calcular BER QPSK
    ber_mod_qpsk = ber_qpsk(energia_bit,N0)
    
    # 6. Simular canal (sem modificar o header)
    sinal_q_c_h_qpsk_c = canal.simular_header(sinal_q_c_h_qpsk, ruido,8)  
  

    #<--- Calcular SNR 
    #SNR Canal: sinal modulado qpsk & sinal modulado recebido do canal - sinal modulado qpsk 
    snr_canal = snr_pratico(sinal_q_c_h_qpsk,sinal_q_c_h_qpsk-sinal_q_c_h_qpsk_c )
   
    # 7. Desmodular sinal QPSk
    sinal_recebido_desmodulado = qpsk.desmodular(sinal_q_c_h_qpsk_c)
    #sinal hamming  / sinal desmodulado
    ber_qpsk_pratico = None
    minIdx = np.minimum(len(sinal_q_c_h),len(sinal_recebido_desmodulado))
    ber_qpsk_pratico = ber_pratico(sinal_q_c_h[0:minIdx],sinal_recebido_desmodulado[0:minIdx])

    ber_apos_correcao = None
    ber_antes_correcao = None
    
    if(com_correcao_erros):
        
        # 8. Descodificar Hamming
        sinal_recebido_desmodulado_hamming = hamming.descodificar(sinal_recebido_desmodulado)

        #ber antes correcao: sinal codificado hamming & sinal demodulado qpsk
        #ber apos correcao: sinal codificado (int to bit )  & sinal descodificado hamming     
        #TODO: <--- Calcular BER Hamming Prático (após correcao)        
        minIdx = np.minimum(len(sinal_recebido_desmodulado),len(sinal_q_c_h))
        ber_antes_correcao = ber_pratico(sinal_q_c_h[0:minIdx],sinal_recebido_desmodulado[0:minIdx])
        
        #minIdx = np.minimum(len(sinal_q_c),len(sinal_recebido_desmodulado_hamming))
        ber_apos_correcao = ber_pratico(sinal_q_c, sinal_recebido_desmodulado_hamming)
        #print("sinal_q_c === sinal_recebido_desmodulado_hamming",np.array_equal(sinal_q_c,sinal_recebido_desmodulado_hamming))

    else:
        sinal_recebido_desmodulado_hamming = sinal_recebido_desmodulado
    
    # 9. Converter para "analógico"
    sinal_recebido_desmodulado_hamming_descodificado = dac.descodificar(sinal_recebido_desmodulado_hamming, R_codificacao)
    
    # 10. Desquantificar sinal
    sinal_recebido_desmodulado_hamming_descodificado_desquantificado = quantificador.desquantificar(sinal_recebido_desmodulado_hamming_descodificado)

    #TODO:<--- Calcular SNR Prático/Canal Rececao
    #SNR rececao - Sinal original com sinal desquantificado
    snr_rececao = None
    snr_rececao = snr_pratico(sinal,sinal_recebido_desmodulado_hamming_descodificado_desquantificado-sinal )
    
    #Verificar se o sinal recebido é igual ao sinal quantificado original
    #print(sinal_q,sinal_recebido_desmodulado_hamming_descodificado_desquantificado )
    #print("Array igual?",np.array_equal(sinal_q, sinal_recebido_desmodulado_hamming_descodificado_desquantificado))
    
    # Para além disso... 
    # Aplicar filtro passa-baixo para remover réplicas causadas pela amostragem
    # TADAAAAA, já está transmitido qualquer coisa
    
    return (sinal_recebido_desmodulado_hamming_descodificado_desquantificado,qpsk.constelacao(), 
            (ber_mod_qpsk,ber_qpsk_pratico,ber_antes_correcao,ber_apos_correcao,snr_teorico,  snr_canal,  snr_rececao))

r_header = 16
im_inicial = Image.open( "test_images/lena_color.tif" )
a = np.array( im_inicial )
b = np.reshape( a , np.prod(a.shape));
c = np.unpackbits( b)
c1 = ADC_DAC()
header = c1.codificar(np.asarray(a.shape),r_header)
c = np.hstack((header, c))
x = c;
after_plots = []

def process_image(noise,R):

    plot_idx = 1;
    
    #Simulação com correção de erros
    start_time = time.time()
    (p_erros,b_1,d) = simulate_system(x,R,True,noise)
    print("--- Simulação de canal com erro demorou %s minutos ---" % ( (time.time() - start_time) / 60) )
    #Simulação sem correção de erros
    start_time = time.time()
    (p,b_2,d) = simulate_system(x,R,False,noise)
    print("--- Simulação de canal sem erro demorou %s minutos ---" % ( (time.time() - start_time) / 60) )
    
    # Convert floats to single integers
    p[p<0] = int(0)
    p[p>0] = int(1)
    p_erros[p_erros<0] = int(0)
    p_erros[p_erros>0] = int(1)

    # Parse header
    header_erros = p_erros[0:r_header*3]
    header = p_erros[0:r_header*3]
    d_erros = np.packbits(p_erros[r_header*3::].astype(int))
    d = np.packbits(p[r_header*3::].astype(int))

    image_final_erros = Image.fromarray(np.reshape(d_erros,tuple(c1.descodificar(header_erros,r_header))))
    image_final_erros.save("generated/noisy_image_hamming_r_{0}.bmp".format(R))

    image_final = Image.fromarray(np.reshape(d,tuple(c1.descodificar(header,16))))
    image_final.save("generated/noisy_image_r_{0}.bmp".format(R))
    
    plt.figure(figsize=(14,14));
    plt.suptitle("Code iteration with R={0}, noise = {1}".format(R,noise), fontweight="bold",fontsize=14)
    plt.subplot(2,3,plot_idx);
    plt.title("Original Image")
    plt.imshow(im_inicial,interpolation='nearest')
    plt.axis('off')

    plt.subplot(2,3,plot_idx+1);
    plt.imshow(image_final_erros,interpolation='nearest')
    plt.title("Received & Corrected Image")

    plt.axis('off')
    plt.subplot(2,3,plot_idx+2);
    plt.imshow(image_final,interpolation='nearest')
    plt.title("Received & Not Corrected Image")    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig("generated/image_result_r_{0}_noise_{1}".format(R,noise))
    plt.close()

    plt.figure(figsize=(14,14))
    plt.subplot(3,2,1)
    plt.scatter(b_1[0],b_1[1])
    plt.grid()
    plt.axis(xmin=-2*np.pi, xmax=2*np.pi, ymin=-2*np.pi, ymax=2*np.pi)
    plt.title("QPSK Constelation with error correction")
    plt.subplot(3,2,2)
    plt.scatter(b_2[0],b_2[1])
    plt.title("QPSK Constelation without error correction")
    plt.axis(xmin=-2*np.pi, xmax=2*np.pi, ymin=-2*np.pi, ymax=2*np.pi)
    plt.grid()
    plt.tight_layout()
    plt.savefig("generated/qpsk_constelation_r_{0}_noise_{1}".format(R,noise))
    plt.close()
    
process_image(2,8)