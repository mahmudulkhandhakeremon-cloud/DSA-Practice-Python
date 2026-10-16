## 58--Length of Last Word
##Problem Solution
class Solution(object):
    def LengthOfLastWord(self,s):
        return(len(s.split()[-1]))

s=Solution()
print(s.LengthOfLastWord("Hello World!"))