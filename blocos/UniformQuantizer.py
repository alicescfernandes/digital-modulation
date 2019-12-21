import numpy as np
import warnings

class UniformQuantizer:
    def __init__(self,R,vmax,tipo,usar_lei_mi=False):
        self.R = R
        self.vmax = vmax
        self.tipo = tipo
        
        L = int(2 ** self.R); #intervalos de quantficação
        delta_quantificacao = (2 * self.vmax) / L; #Delta de quantificação
        self.L = L
        self.delta_quantificacao = delta_quantificacao
        self.usar_lei_mi = usar_lei_mi
        self.quantizer()

    def quantizer(self):
        niveis_quantificacao = np.zeros(self.L);
        niveis_quantificacao_idx = np.zeros(self.L)

        if(self.tipo == "midrise"):
            niveis_de_quantificacao = np.arange(-self.delta_quantificacao/2+self.delta_quantificacao, self.vmax, self.delta_quantificacao)
            niveis_quantificacao[int(self.L/2):self.L] = niveis_de_quantificacao #Copiar os niveis_quantificacao_idx de um array, para o array de 0's
            niveis_quantificacao[0:int(self.L/2)] = niveis_de_quantificacao[::-1] * -1 #Inverter a array e multiplicar por -1 para obter os valores negativos
            niveis_quantificacao_idx = np.arange(-1*self.vmax,self.vmax+self.delta_quantificacao,self.delta_quantificacao)

        elif(self.tipo == "midtread"):
            
            niveis_quantificacao = np.arange(-self.delta_quantificacao * int(self.L/2) ,self.delta_quantificacao * int(self.L/2) + self.delta_quantificacao , self.delta_quantificacao)
            niveis_quantificacao_idx_positivo = np.arange(-self.delta_quantificacao/2+self.delta_quantificacao, self.vmax, self.delta_quantificacao)
            niveis_quantificacao_idx[int(self.L/2):self.L] = niveis_quantificacao_idx_positivo
            niveis_quantificacao_idx[0:int(self.L/2)] = niveis_quantificacao_idx_positivo[::-1] * -1
            
        return (niveis_quantificacao, niveis_quantificacao_idx)

    def desquantificar(self, sinal_niveis_quantificacao_idx):
        niveis_quantificacao, valores_decisao = self.quantizer()

        return np.array([niveis_quantificacao[int(idx)] for idx in sinal_niveis_quantificacao_idx])

    def quantificar(self,sinal):
        niveis_quantificacao, valores_decisao = self.quantizer();
        sinal_quantificado = np.zeros(len(sinal))
        indexes_quantificacao = np.zeros(len(sinal))
        
        if(self.usar_lei_mi):
            #Se usar lei mi, ent passar primeiro por ai
            self.quantificar_mi(sinal, self.vmax);

        if(np.max(sinal) > self.vmax):
            warnings.warn( ("\nValor máximo do sinal excede o Vmax do quantificador.\nValor Máximo Sinal {0}, Vmax Quantificador: {1}\nValores vão ser truncados a {1}").format(np.max(sinal),self.vmax) )

        if(self.tipo =="midtread"):
            #Ajustar os valores para os valores que o quantificador conheçe
            #Para depois não arrebentar no loop
            sinal[sinal> np.max(valores_decisao)] = np.max(valores_decisao);
            sinal[sinal<(np.max(valores_decisao)) * -1 ] = (np.max(valores_decisao)) * -1 

        
        sinal[sinal>self.vmax] = self.vmax;
        sinal[sinal<(self.vmax) * -1 ] = (self.vmax) * -1 
        
        #Numpy way
        
        #np.where ( condição [a avaliar em verdadeiro], array onde se aplica a condução, [valor_de_substitição] )
        #retorna uma array com os valores avaliados a true substituidos pelo valor_de_substitição
        
        #Find a way to do this without a for
        for amostra in range(0,len(sinal)):
            
            #Para cada nivel
            #ver em que nivel fica a amostra  
            amostra_a_quantificar = sinal[amostra]
            
            #-quantificador.delta_quantificacao
            index = np.where(valores_decisao >= amostra_a_quantificar)[0][0] #usar o np.where apenas para obter os indexes, mas esta função é uma função de substituição
            #print(np.where(valores_decisao >= amostra_a_quantificar))     
            if(self.tipo == "midrise"): index = index - 1
            
            if (index == len(niveis_quantificacao)): index = index-1; #A array de valores de decisão tem sempre +1 elemento que a array de valores de quantificação
            if (index < 0):index = 0
                
            sinal_quantificado[amostra] = niveis_quantificacao[index]
            
            #print(str(amostra_a_quantificar) +" " + str(sinal_quantificado[amostra]))

            indexes_quantificacao[amostra] = index


            
        return (sinal_quantificado,indexes_quantificacao)

    def quantificar_mi(self,sinal_entrada, u=255):
        sinal = np.copy(sinal_entrada)
        #Usar list comprehension para calcular a func de u. Valores positivos
        sinal[sinal>0] = [ np.log(1+u * (abs(m)/self.vmax))/np.log(1+u) * self.vmax for m in  sinal[sinal>0] ]
        
        #Usar list comprehension para calcular a func de u. Valores Negativos
        sinal[sinal<0] = [  ( np.log(1+u * (abs(m)/self.vmax))/np.log(1+u) ) * self.vmax * -1 for m in  sinal[sinal<0] ]
        
        return sinal;

    def snr(self, P, snr_pratico):
        if(self.usar_lei_mi == True):
            return  6 * self.R - 10
        
        return 10 * np.log10(3 * ( P / self.Vmax**2 ) ) + 6 * self.R

if __name__ == "__main__":
    Vmax = 1;
    r = 4;
    sinal_rampa = np.arange(-Vmax,Vmax,0.1)

    quantificador = UniformQuantizer(r, Vmax,"midrise")
    (sinal_1, idx) = quantificador.quantificar(sinal_rampa)
    sinal_1_desquantificado = quantificador.desquantificar(idx)

    print(sinal_1)
    print(sinal_1_desquantificado)
    print(np.array_equal(sinal_1, sinal_1_desquantificado))
