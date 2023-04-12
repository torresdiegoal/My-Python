# I) Fibonacci
##

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


print(fibonacci(15))
