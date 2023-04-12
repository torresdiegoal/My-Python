# II) TRIANGULO DE PASCAL SOLO LOS VALORES

import numpy as np

def triangle_pascal_values(n):
    matriz = np.zeros([n,n])
    k = 0
    
    for i in range(n):
        for j in range(i+1):
            if j == 0 or i == j:  ## Ya que en los extremos siempre va uno
                matriz[i,j] = 1
            else:
                k = matriz[i-1,j] + matriz[i-1,j-1]
                matriz[i,j] = k
    return(matriz)

def position_pascal_triang(x,y):
    if y > x:
        return "Error, out of bounds"
    else:
        triang = triangle_pascal_values(x+1)
        return triang[x,y]
    
print(position_pascal_triang(9,3))

