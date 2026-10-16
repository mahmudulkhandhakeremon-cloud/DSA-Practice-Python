##To Calculate Insertion Sort
##Part of Practice DSA 
#Remembered Points:
#Consider the first element as the sorted part of the array.
#Take the next element from the unsorted part. Call it the key.
#Compare the key with elements in the sorted part, moving from right to left.
#If an element is greater than the key, shift it one position to the right.
#Insert the key into its correct position.
#Repeat the process until the entire array is sorted.


my_array=[64,34,25,12,22,11,90,5]
n=len(my_array)
for i in range (1,n):
    insert_index=i
    current_value=my_array.pop(i)
    for j in range(i-1,-1,-1):
        if my_array[j]>current_value:
            insert_index=j
    my_array.insert(insert_index,current_value)
print("Sorted Array:",my_array)