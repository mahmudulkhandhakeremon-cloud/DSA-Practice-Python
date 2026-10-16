##34--Find First and Last Position of Element in sorted Array
##Problem Solution


class Solution:
    def searchRange(self, nums, target):
        def find_bound(is_first):
            low = 0
            high = len(nums) - 1
            ans = -1
            
            while low <= high:
                mid = (low + high) // 2
                if nums[mid] == target:
                    ans = mid
                    if is_first:
                        high = mid - 1  
                    else:
                        low = mid + 1   
                elif nums[mid] < target:
                    low = mid + 1
                else:
                    high = mid - 1
            return ans
        first = find_bound(True)
        last = find_bound(False)
        return [first, last]
print([5,7,7,8,8,10],8)