def  Recursion(list1,min,max,sorting_type):  #재귀를 위한 함수

    if min<max:
        idx = sorting(list1,min,max,sorting_type) # 쪼깨자

        Recursion(list1,min,idx-1,sorting_type) # 쪼갠거 왼쪽을 정렬한다!

        Recursion(list1,idx+1,max,sorting_type) # 쪼갠거 오른쪽을 정렬한다!
    else:
        pass
        
def sorting(list1,min,max,sorting_type):
    pivot = list1[max] #기준점
    idx=min #바뀌는위치
    i = min

    if sorting_type == True:        # 입력받는 sorting_type이 True이면 오름차순
        while i<max:
            if list1[i] <= pivot:
                temp = list1[i]
                list1[i]=list1[idx]
                list1[idx]=temp
                idx=idx+1
            i=i+1 
        temp = list1[idx]
        list1[idx]=list1[max]
        list1[max]=temp
        return idx
    else:                       #True가 아닌 다른값 즉, False이면 내림차순
        while i<max:
            if list1[i] >=pivot:
                temp=list1[i]
                list1[i]=list1[idx]
                list1[idx]=temp
                idx=idx+1
            i=i+1
        temp=list1[idx]
        list1[idx]=list1[max]
        list1[max]=temp
        return idx

list1 = []              #숫자 들어갈 리스트.
minercheck = False      #배열에 들어갈 값이 음수인지 판단하기 위한 변수

while 1:
    sentence = input()          #입력값
    find_type = -1              #-o가있는지 판단하기 위해 있음.
    while 1:
        find_type = sentence.find("-o")    #find로 -o가있는 위치를 찾음. 만약 없다면 find_type의 값이 바뀌지 않아 다시 입력해야함.
        if sentence[find_type+3] == "A":
            sorting_type=True              #sorting_type은 오름차순 내림차순을 결정하기 위해 사용.
            break
        elif sentence[find_type+3]=="D":
            sorting_type=False
            break
        else:
            print("Wrong sorting type insert \'A\'or\'D\' ")        #A 나 D가 오지않으면 오름,내림결정못함 다시.
            find_type=-1                                            #-o는 있으나 A D가없을수있으니 find_type 다시 초기화.
            break
    if find_type==-1:
        continue
        
    lines = sentence.find("-i")                                     #-i가 나오는 위치를 찾아 그전에 나오는 숫자들은 배열에 넣지 않게하기위함.
    if lines == -1:
        print("No start array. \'-i\'. start array")
        continue
    
    chiper_checker =False # 10이상의 수를 넣기 위해 체커를 이용, 다음 숫자가 나오는 스페이스바가 나오기 전까지 숫자를 10배씩 곱해 다시 넣어주기위해 만듬
    line_cnt =0                         #-i가 나오는 줄까지 반복하기 위해서 카운트 해줄변수.
    for line in sentence:
        if line_cnt <= lines:
            line_cnt=line_cnt+1
            continue

        if line[0].isdigit() == True:                   #line[0]에 있는 값을 isdigit 함수를 사용하여 숫자일 경우 True를 반환하게됨.
            if chiper_checker == False:                 #만약 chiper_checker가 False 일 경우 처음 숫자가 들어가는것 이기 때문에 chiper_cnt에 line값이 들어감.
                chiper_cnt = int(line)
                chiper_checker=True
            elif chiper_checker ==True:                 #chiper_checker가 True이면 앞에 숫자가 이미 있었던것이기 때문에 chiper_cnt에 10을 곱하고 거기에 line을 더함.
                chiper_cnt = chiper_cnt*10 + int(line)
          
        elif line[0] == " ":                            # " "이 나오는것은 숫자의 입력이 끝났음을 뜻함. 숫자가 들어간 이상 chiper_checker가 켜지기고, 앞에 -가 있냐 없냐에 따라
            if chiper_checker == True:                  # minercheck가 켜지기 때문에 그에 맞춰 chiper_cnt를 list1에 대입함.
                if minercheck ==True:
                    list1.append(chiper_cnt*-1)
                else:
                    list1.append(chiper_cnt)
                chiper_checker=False
            minercheck = False                          # list1에 숫자를 넣고 다시 minercheck false로 초기화.
        elif line[0] == "-":                            # -가 나오면 minercheck 켜짐.
            minercheck = True

    list1.append(chiper_cnt)
    min=0
    max=len(list1)
    break

Recursion(list1,min,max-1,sorting_type)
i =0
print("[",end='')
while i<max-1:
    print(list1[i],end=', ')
    i=i+1
print(list1[max-1],"]")
