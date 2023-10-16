'''
    module for imeplementing utility functions for string processing
'''


def common_prefix(s1, s2):
    l = 0

    while l < len(s1) and l < len(s2):
        if s1[l] == s2[l]:
            l += 1
        else:
            break
        
    return l

def common_suffix(s1, s2):
    l = 1
    while l < len(s1) and l < len(s2):
        if s1[-l] == s2[-l]:
            l += 1
        else:
            break

    return l - 1
    