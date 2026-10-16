##To Calculate Fibonacci Value
##Part of Practice DSA
##Finding The nth Fibonacci Number Using Recursion
## nth Fibonnaci value calculate Formula: F(n)= F(n-1)+F(n-2)

def Fibonacci(n):
    if n <=1:
        return n
    else:
        return Fibonacci(n-1)+Fibonacci(n-2)
print(Fibonacci(20))