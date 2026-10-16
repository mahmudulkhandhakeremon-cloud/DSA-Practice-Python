##To Find Maximum value of an Array
##Part of Practice DSA

Mohammad_Sm=[7,12,25,9,4,3,2,1]
maxVal=Mohammad_Sm[0]

for i in Mohammad_Sm:
    if i > maxVal:
       maxVal=i

print("Highest Value of Array:",maxVal)