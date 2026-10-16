##To Calculate Bubble Sort Improvement
##Part of Practice DSA
## We remember: 1.An Array with value to sort.
## 2.An inner Loop that goes through the array and swaps values if the first
##Value is higher than the next value.This loop must loop through one less value each time it runs.
##3.An outer loop controls how many times the inner loop must loop.For an Array with n values,this outer
##Loop must run n-1 times.



Mohammad_Sm=[64,34,25,12,22,11,9,60,5,7,3]##Array
n=len(Mohammad_Sm)##Calculate the Length of Array

for i in range(n-1): ##Outer Loop
    swapped=False
    for j in range(n-i-1): ##Inner Loop 
        if Mohammad_Sm[j]> Mohammad_Sm[j+1]:
           Mohammad_Sm[j],Mohammad_Sm[j+1]=Mohammad_Sm[j+1],Mohammad_Sm[j]
           swapped=True
    if not swapped:
        break
print("Sorted array:",Mohammad_Sm)