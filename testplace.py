i = 0
chor_li = ['c','c','c','c','d','d','e','e']
chor_rang_li = []
while i < len(chor_li)-1:
    range_start = i
    while i < len(chor_li)-1 and chor_li[i+1] == chor_li[i]:
        i = i+1
    i = i+1
    range_end = i
    chor_rang_li.append(range(range_start,range_end))

print(chor_rang_li)


for i in range(len(chor_rang_li)):
    for j in range(len(chor_rang_li[i])):
        print(chor_rang_li[i][j])