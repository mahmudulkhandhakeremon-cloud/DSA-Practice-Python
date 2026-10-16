##To calculate Fibonacci Value 
##Part of Practice DSA
##Implementation Using a For Loop

prev2=0
prev1=1
print(prev1,prev2)

for fibo in range(20):
    newfibo=prev1+prev2
    print(newfibo)
    prev2=prev1
    prev1=newfibo
    