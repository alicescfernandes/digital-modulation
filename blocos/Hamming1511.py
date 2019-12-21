import numpy as np;
import time
from blocos.ADC_DAC import ADC_DAC #Codificador int-bit /  bit-int
import warnings
#TODO: Arranjar bit_to_int numero impar de bits

def bit_to_int(array,R):
    int_array = np.zeros(0,dtype=int)
    array = np.array(array,dtype=int)
    for k in range(0,len(array),R):
        bits = array[k:k+R]
        c = "0b" + "".join([str(c) for c in bits])
        int_array = np.append(int_array,int(c,2))
        
        #int_array = np.append(int_array,twos_comp(int(c,2),R))
       
    return int_array#int_array

def int_to_bit(array, R):
    array_2 = list(np.copy(np.array(array,dtype=int)))
    literais = [ ];
    bit_array = np.zeros(0)
    for k in array_2:
        binary_rep = np.binary_repr(k, width=R);
        int_array = np.array(list(binary_rep),int)
        bit_array = np.hstack((bit_array, int_array))
    return bit_array

class Hamming1511:
    def __init__(self):
        import numpy as np;
        self.MatrizParidade = np.array([[1, 1, 0, 0], [1, 0, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 0, 1], [0, 0, 1, 1], [1, 1, 1, 0], [1, 1, 0, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]], dtype=int)
        self.MatrizParidadeMapa = np.ones(len(self.MatrizParidade))
        self.k = 15  # bits palavra de codigo
        self.n = 11  # bits mensagem
        
    def descodificar(self,M): 
        M = M[0:len(M)-(len(M) % 15)]
        warnings.warn("Tamanho do sinal recebido não é múltiplo de 15")       
        c1 = ADC_DAC();
        # Para cada 11 bits, gerar 15, onde 4 são de controlo. Primeira trama é a quantidade de bits a remover no  final
        bits_a_descartar = 0;   
        MatrizParidade = np.array([[1,1,0,0],[1,0,1,0],[1,0,0,1],[0,1,1,0],[0,1,0,1],[0,0,1,1],[1,1,1,0],[1,1,0,1],[1,0,1,1],[0,1,1,1],[1,1,1,1]],dtype=int)
        MatrizParidadeMapa = np.zeros(len(MatrizParidade))
        
        #Calcular um mapa, converter bits para inteiros
        for c in range(0,len(MatrizParidade)):
            MatrizParidadeMapa[c] = c1.descodificar(MatrizParidade[c],4)
        
        MatrizGeradora = np.vstack((MatrizParidade,np.eye(4)))
        #Calcular Header
        header = M[0:15]

        #Verificar e corrigir erros
        header_descodificado = np.array(np.dot(header,MatrizGeradora) % 2,dtype=int ) #retorna um array de 4
        index = c1.descodificar(header_descodificado,4)[0] #se 0, está certo
        p_index = np.where(MatrizParidadeMapa == index)
        tem_erros =  len(p_index[0])
        
        if(tem_erros != 0):  
            index = p_index[0][0]
            
            if(index<11): #só pode modificar os primeiros 11 bits
                header[index] = (header[index]  + 1 ) % 2
                header_descodificado =  header[0:11];   
        else:
            header_descodificado =  header[0:11];        
        
        bits_a_descartar = c1.descodificar(header,11)[0]
        #bits_a_descartar = bit_to_int(header,11)[0]
        
        
        M = M[15:len(M)]
        
        calculo = int(len(M)) -  (int(len(M) / 15) * 4)
        
        dados_descodificados_2 = np.zeros( calculo )
        
        #print(len(M) / 15)
        for k,i in zip(range(0, len(M),15), range(0, len(M),11)): 
            dados = M[k:k+15]
            #print("dados",dados)
            #if(len(dados) < 15):
            #    #TODO: QPSK acrescenta mais um 0 na modulação, o que faz com que o loop n consiga andar de 15 em 15
            #    print('dados<15',"skipping",dados)
            #    #bits_a_descartar = bits_a_descartar + len(dados)
            #    break;
            N_descodificado = np.array(np.dot(dados,MatrizGeradora) % 2,dtype=int )
            index = c1.descodificar(N_descodificado,4)[0] #se 0, está certo
            p_index = np.where(MatrizParidadeMapa == index)
            tem_erros =  len(p_index[0])
            
            if(tem_erros != 0):  
                index = p_index[0][0]
                dados[index] = (dados[index]  + 1 ) % 2
                dados =  dados[0:11]
                dados_descodificados_2[i:i+11] = dados;
            else:
                dados =  dados[0:11]
                dados_descodificados_2[i:i+11] = dados;
        
        
        #Cortar bits no final
        if(bits_a_descartar > 10): bits_a_descartar = 10 #numero de bits a descartar não pode ser maior que o numero de bits da mensagem    
        #print("bits_a_descartar",header_descodificado, bits_a_descartar)
        
        
        dados_descodificados_2 = dados_descodificados_2[0:len(dados_descodificados_2) - bits_a_descartar]
        
        dados_descodificados_2 =  np.array(dados_descodificados_2,dtype=int);
        #print("Descodificado:\n" + str(dados_descodificados) + " " + str(len(dados_descodificados)))
        return dados_descodificados_2
        
    def codificar(self,N):
        # pad de 0's quando n há mais ints
        # Para cada 11 bits, gerar 15, onde 4 são de controlo
        codificador = ADC_DAC()
        #Calcular padding bits e adicioná-los
        padding_bits = 0
        
        #Append 0's to the end
        if(len(N)%11 > 0):
            padding_bits = ( 11 - (len(N)%11) )
            padding_bits_2 = np.full((padding_bits),0)
            N = np.hstack((N,padding_bits_2))
            
        b2 = padding_bits
        #print(N)
        N_codificado = np.ones( int(len(N)/11) * 15 )
        #print("Recebidos Codificador\n" + str(N) + " " + str(len(N)))
        MatrizParidade = np.array([[1,1,0,0],[1,0,1,0],[1,0,0,1],[0,1,1,0],[0,1,0,1],[0,0,1,1],[1,1,1,0],[1,1,0,1],[1,0,1,1],[0,1,1,1],[1,1,1,1]])
        MatrizGeradora = np.hstack((np.eye(11),MatrizParidade))
        
        for k,i in zip(range(0, len(N),11),range(0, len(N_codificado),15)) :
            N_codificado[i:i+15] = np.dot(N[k:k+11],MatrizGeradora) % 2 
            
        #Criar um header com os bits para cortar no final
        padding_bits = codificador.codificar([padding_bits] ,11)   
        
        #padding_bits = int_to_bit([padding_bits] ,11)   
        #print("padding_bits", b2 ,padding_bits)

        N_codificado = np.append(np.dot(padding_bits,MatrizGeradora) % 2, N_codificado )
        
        N_codificado = np.array(N_codificado,dtype=int)
        #print("Codificado:\n" +  str(N_codificado)  + " " + str(len(N_codificado)))
        return N_codificado

    
    def ber_linha(self, ber):
        r_c = self.k / self.n
        ber_linha = (3 * (self.n-1)) / 2 * (ber ** 2)
        return ber_linha

def testar_hamming():
    print("Teste sem erro")

    array = np.random.randint(0, 2, 2**15)
    
    hamming1511 = Hamming1511()
    start_time = time.time()
    array_codificado = hamming1511.codificar(array)
 
    array_descodificado = hamming1511.descodificar(array_codificado)
    
    print("--- %s segundos Hamming ---" % (time.time() - start_time))
    print(array)
    print(array_codificado)
    print(array_descodificado)
    print(np.array_equal(array_descodificado, array))
    print("\n\n")
    
    

def testar_hamming_erro():
    print("Teste com erro")
    #Teste com erro
    array = np.random.randint(0, 2, 2**15)
    #array = np.random.randint(0, 2,22)
    #array = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    print("normal",array)

    hamming1511 = Hamming1511()

    array_codificado = hamming1511.codificar(array)
    array_codificado_erro = np.copy(array_codificado)

    for i in range(15, len(array_codificado),15):
        np.put(array_codificado_erro, i, (array_codificado_erro[i] + 1) % 2)

    print(array_codificado)

    print(array_codificado_erro)
    start_time = time.time()
    array_descodificado = hamming1511.descodificar(array_codificado_erro)
    print("--- %s segundos a descodificar ---" % (time.time() - start_time))

    print(array_descodificado)
    print(np.array_equal(array_descodificado, array))

if __name__ == "__main__":
    testar_hamming()
    testar_hamming_erro()
