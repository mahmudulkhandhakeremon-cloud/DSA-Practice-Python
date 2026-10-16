##136. Single Number
##Problem Solution
class Solution(object):
    def singleNumber(self,nums):
        result=0
        for num in nums:
            result=result ^num
        return result
s=Solution()
print(s.singleNumber([2,2,1]))