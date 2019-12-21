import numpy as np
import time
import math


class ADC_DAC:
    def __init__(self):
        '''
        self.R = R
        '''

    def codificar(self, array, R):
        array_copy = np.array(array, dtype=int)
        bit_array = np.zeros(int(len(array) * R))
        #start_time = time.time()

        c = 0;
        f = '{0:0'+str(R)+'b}'
        for i in array_copy:
            binary_rep = f.format(i)
            bit_array[c:c+R] = list(binary_rep)
            c+=R

        #print("--- codificar  %s  segundos ---" % (time.time() - start_time))

        return np.array(bit_array)

    def descodificar(self, array, R):
        int_array = np.zeros(math.ceil(len(array)/R), dtype=int)
        array = np.array(array, dtype=int)

        #start_time = time.time()
        z = 0
        for i in range(0, len(array), R):
            c =  "".join(map(str,array[i:i+R]))
            int_array[z] = int(c, 2)
            z += 1

        #print("--- descodificar 2  %s  segundos ---" %  (time.time() - start_time))
        return int_array 


def testar_codificador():
    R = 8
    codificador = ADC_DAC()
    array = np.random.randint(0, 254, 2**18)  # 50331648
    array_bits = codificador.codificar(array, R)
    array_bit_to_int = codificador.descodificar(array_bits, R)
    print(array)
    print(array_bits)
    print(array_bit_to_int)
    print(np.array_equal(array, array_bit_to_int))


if __name__ == "__main__":
    testar_codificador()
