# I) Fibonacci
## Esta serie sirve para contar el numero total de opciones que se van acomulando, sumando los 
## dos ultimos valores.

def fibonacci(n):
    a = 0
    b = 1
    l = []
    for i in range(n):
        l.append(b)
        c = a + b
        a = b
        b = c
    return l
        
print(fibonacci(14))


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
    
print (position_pascal_triang(9,3))


#III) Maximo

def maximo(lista,a,b):
    maxim = 0
    if a>b:
        return 'Error, b must be greater than a'
    for i in range(a,b):
        if lista[i] > maxim:
            maxim = lista[i]
    return maxim

arreglo = [3,6,87,9,0,875,45,3,4,2,32,110,78,456,345,21,78]
print (maximo(arreglo,0,3))


#IV) Ordenamiento 

def cadena_orden(lista): 
    b = []
    for i in range(len(lista)):
        z = ''.join(sorted(lista[i], key= str.upper))
        b.append(z)
    return b

texto = ['hola', 'suerte', 'amor', 'computador', 'leXxicografiCco', 'tesoro']
print(cadena_orden(texto))


# V) Escaleras
## Este ejercicio se realiza con principios de Fibonacci

def escalera(n):
    steps = 0
    if n == 1:
        steps = 1
        return steps
    if n == 2:
        steps = 2
        return steps
    if n > 2:
        a = 1
        b = 2
        for i in range(2,n):
            steps = a + b
            a = b
            b = steps
    return steps
        
print(escalera(9))