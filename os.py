from tqdm import tqdm
import math
import copy
def runI(num_filter, pixel,px,pbar,ifmap_base,peI,cycle,arr,tol_cycle,plane,replay,ifmap_read,pe_used
                                                                    ,pex = 3,pey = 3,pez = 3,
                                                                    input_x=3,input_y=2,input_z=3,
                                                                    fx = 2,fy = 2,fz = 2,
                                                                    stride = 1,start=0,turn_flag=False):
    neginf = -math.inf
    #end=False
    E_h = (input_x - fx + stride) / stride #feature map size
    E_w = (input_y - fy + stride) / stride
    E_z = (input_z - fz + stride) / stride
    e2=1
    if E_h>0:
        e2=e2*E_h
    if E_w>0:
        e2=e2*E_w
    if E_z>0:
        e2=e2*E_z
    input_xyz=input_x*input_y*input_z
    if replay>0 or ( replay==0 and num_filter%pey==0):
      e2=e2*pey
    else:
      e2=e2*(num_filter%pey)
    if tol_cycle%2!=0:
        if plane==0:
            #print(pixel,peI[0:pex])
            
            for i in arr:
                if peI[i+plane]!=neginf:
                    pixel[i+plane]=pixel[i+plane]+1
                if pixel[i+plane] == fx*fy*fz and px<e2:
                    pbar.update(1)
                    #print(px,e2,' %2 ')
                    pixel[i+plane]=0
                    px=px+1
                elif pixel[i+plane] == fx*fy*fz and px>=e2:
                    pixel[i+plane]=0
            
                    #print(px,e2,' %00 ')


    else:
        for j in arr:
            #print(j, plane, len(peI))
            if peI[j+plane] == neginf:
                #前面有值且pe位置不在第一排
                if  j >= pex and peI[j+plane-pex]!=neginf:
                    peI[j+plane] = peI[j+plane-pex]
                    cycle[j+plane] =1
                #右邊有值且pe位置不在最右邊
                elif (j+1)%pex!=0 and peI[j+plane+1]!=neginf:
                    peI[j+plane] = peI[j+plane+1]
                    cycle[j+plane] =1
                            
                elif j+plane >=pex*pey and peI[j+plane-pex*pey]!=neginf:
                    peI[j+plane] = peI[j+plane-pex*pey]
                    cycle[j+plane] =1
                #cycle數(停留數)已滿
            elif peI[j+plane] != neginf and cycle[j+plane] == fz:

                if  j >= pex and peI[j+plane-pex]!=neginf:
                    peI[j+plane] = peI[j+plane-pex]
                    cycle[j+plane] =1
                    #print(2.1)
                elif (j+1)%pex!=0 and peI[j+plane+1]!=neginf:
                    peI[j+plane] = peI[j+plane+1]
                    cycle[j+plane] =1
                elif j+plane >=pex*pey and peI[j+plane-pex*pey]!=neginf:
                    peI[j+plane] = peI[j+plane-pex*pey]
                    cycle[j+plane] =1 
                else:
                    peI[j+plane] =  neginf   
                    cycle[j+plane] =0

            else:
                cycle[j+plane] =cycle[j+plane]+1

        if px !=e2 or replay!=0 :
            #輸入新的值
            j=-1
            #找到第一個pe為負無窮或cycle數(停留數)已滿的pe位置
            for i in range(0,pex): 
                if peI[i] == neginf or cycle[i]==fz+1:
                    if j >=0 and j < pex and not peI[j] == neginf :
                        j=i
                    elif j==-1:
                        j=i

            initDot=start+(stride*pez-1)
            #print('j:',j,'dot:',initDot,'px!=e2:',px !=e2 ,'if1:',(initDot+1)<input_xyz,initDot < (start-start%input_z)+(input_z-1),'if2:',
                 #(start-start%input_z)+stride*input_z<input_xyz)
            if j!=-1 and plane==0 and peI[j]==neginf:
                if px !=e2 and tol_cycle!=0 and (initDot+1)<input_xyz and initDot < (start-start%input_z)+(input_z-1) : 
                    start=initDot+1
                    peI[j]=start
                    cycle[j] =1

                elif px !=e2 and (start-start%input_z)+stride*input_z<input_xyz:
                    #print('op2')
                    if tol_cycle!=0:
                        start=(start-start%input_z)+stride*input_z
                        #print('s:',start)
                    peI[j]=start
                    cycle[j] =1                
                else:
                    #print('op3')
                    if px !=e2:
                        start=0
                        peI[j]=0
                        cycle[j] =1
                    elif replay!=0:
                        start=0
                        cycle[j] =1
                        peI[j]=0
                        turn_flag=True
                        #end=False
                        tol_cycle=0
                        replay=replay-1
                        px=0
                    else:
                        start=neginf
                        peI[j]=neginf
                        turn_flag=False
                        tol_cycle=0
        #else:
            #end=True


    for i in arr:
        if peI[i+plane]>=0:
            if i < pex and plane==0:
                ifmap_read += str(int(peI[i]+ifmap_base)) + ", "
            pe_used += 1
        elif i < pex and plane==0 :
            ifmap_read+=", "

    return px,replay,ifmap_read,pe_used,turn_flag,start,tol_cycle,replay,pixel,pbar


