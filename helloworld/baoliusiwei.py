import sys



sys.path.append('.')




def siwei(li):
    if isinstance(li,list):
        if not isinstance(li[0],str):
            li = [round(i,4) for i in li]
    
    return li


if __name__ == '__main__':
    a = ['a','bbbbb']
    print(siwei(a))

