{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "8\n"
     ]
    }
   ],
   "source": [
    "#4. Fibonacci\n",
    "\n",
    "def fibonacci(n):\n",
    "    a = 0\n",
    "    b = 1\n",
    "    \n",
    "    for i in range(n):\n",
    "        c = a + b\n",
    "        a = b\n",
    "        b = c\n",
    "    return b\n",
    "\n",
    "print(fibonacci(5))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def maxim(a,b):\n",
    "    if a > b:\n",
    "        "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "ahlo\n"
     ]
    }
   ],
   "source": [
    "#7. Ordenamiento \n",
    "\n",
    "def cadena_orden(lista): \n",
    "    return  ''.join(sorted(lista, key= str.upper))\n",
    "        \n",
    "\n",
    "texto = 'hola'\n",
    "print(cadena_orden(texto))"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
