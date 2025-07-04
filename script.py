# f=open('5m_Sales_Records.csv','r')
# for line in f:
#     print(line)
#     print()
#     print(type(line))
#     print(line.split(','))
#     print(len(line.split(',')))
#     # print(ty)
#     break




from sale.models import location

with open('5m_Sales_Records.csv','r') as f:
    # f_contents=f.readlines()
    # print(f_contents)
    # f.close()
    ls=[]
    for line in f:
        line=line.split()
        if line[0]=='Region':
            continue
        ls.append(line)
        print(ls[0])
        if len(ls)==3:
            break
        # print(line.split(','))
        # print(type(line))
        # line=line.split(',')
        # location=location()
        # location.region=
        # break
