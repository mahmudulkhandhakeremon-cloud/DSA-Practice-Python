##To Calculate Selection Sort(SWAP VALUE)
##Part of Practice DSA 
##Remembered Points:
## At first, find the lowest value of the array.
##Secondly, move the lowest value to the front of the unsorted part of the array.
##Thirdly, repeat this process for the remaining unsorted elements.
##Manual Review:
##Step 1: Start with an unsorted Array.
##Ex: [15, 22, 9, 11, 2]
##Step 2: Find the lowest value.
##Ex: 2 is the lowest value.
##Step 3: Move the lowest value to the front of the array.Ex: [2, 15, 22, 9, 11]
##Step 4: Repeat to find the next lowest value and place it in order:
##Ex: [2, 9, 15, 22, 11]
##Ex: [2, 9, 11, 15, 22]
##Finally: Array is sorted!
##Ex: [2, 9, 11, 15, 22]

Mohammad_Sm=[64,34,25,5,22,11,90,12]
n=len(Mohammad_Sm)
for i in range (n):
    min_index=i
    for j in range(i+1,n):
        if Mohammad_Sm[j]< Mohammad_Sm[min_index]:
           Mohammad_Sm[j],Mohammad_Sm[min_index] = Mohammad_Sm[min_index],Mohammad_Sm[j]
print("Sorted Array:",Mohammad_Sm)   