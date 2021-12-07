def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def RangeChange(Old, New, val):
    OldRange = (Old[1] - Old[0])
    NewRange = (New[1] - New[0])
    return (((val - Old[0]) * NewRange) / OldRange) + Old[0]
