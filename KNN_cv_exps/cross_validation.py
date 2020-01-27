import nearest_neighbors
import numpy as np

def kfold(n,n_folds):
    k=n//n_folds
    ostatok=n%n_folds
    i=0
    roster=[]
    while i<n_folds-1:
        mas1=np.arange(i*k,(i+1)*k)
        mas21=np.arange(k*(i+1),n)
        mas22=np.arange(k*i)
        mas23=np.concatenate((mas22,mas21))
        roster.append( (mas23,mas1) )
        i+=1
    if(ostatok==0):
        mas1=np.arange(i*k,(i+1)*k)
        mas21=np.arange(k*(i+1),n)
        mas22=np.arange(k*i)
        mas23=np.concatenate((mas22,mas21))
        roster.append( (mas23,mas1) )
        i+=1
    else:
        mas1=np.arange(i*k,(i+1)*k+ostatok)
        mas21=np.arange(k*(i+1),n)
        mas22=np.arange(k*i)
        mas23=np.concatenate((mas22,mas21))
        mas23=mas23[:(n-k)-ostatok]
        roster.append( (mas23,mas1) )
    return roster


def knn_cross_val_score(X,y,k_list,score,cv,weights,metric,strategy,test_block_size):
    if(score=="accuracy"):
        args=np.arange(X.shape[0])
        np.random.shuffle(args)
        X=X[args]
        y=y[args]
        X=X.astype(float)
        y=y.astype(float)
        if(cv==False):
            cv=kfold(X.shape[0],3)
        dictionary={}
        y_true=len(cv[0][1])
        accuracy=np.zeros(len(cv),dtype=float)
        maxk=np.max(k_list)
        ind=np.zeros( (len(cv)-1,X[cv[0][1]].shape[0],maxk),dtype=int)
        dis=np.zeros( (len(cv)-1,X[cv[0][1]].shape[0],maxk),dtype=float)
        argmaxk=np.argmax(k_list)
        classifer=nearest_neighbors.KNN_classifier(k=maxk,strategy=strategy,metric=metric,test_block_size=test_block_size,weights=weights) 
        for count in range(len(cv)-1):#бегаем по фолдам
            classifer.fit(X[cv[count][0],:],np.take(y,cv[count][0])) 
            Y=classifer.find_kneighbors(X[cv[count][1],:],True)
            ind[count]=Y[0]
            dis[count]=Y[1]
            a=predict2(X[cv[count][1],:],ind[count],dis[count],np.take(y,cv[count][0]),weights)
            b=y[count*y_true:(count+1)*y_true]#истинные значения
            accuracy[count]=np.sum(a==b)/(a.shape[0])#РЕАЛИЗОВАЛ ACCURACY
        classifer.fit(X[cv[count+1][0],:],np.take(y,cv[count+1][0])) 
        Y=classifer.find_kneighbors(X[cv[count+1][1],:],True)
        b=y[(count+1)*y_true:]
        ind2=np.zeros( (Y[1].shape[0],Y[1].shape[1]) )
        dis2=np.zeros( (Y[1].shape[0],Y[1].shape[1]) )
        ind2=Y[0]
        dis2=Y[1]
        a=predict2(X[cv[count+1][1],:],ind2,dis2,np.take(y,cv[count+1][0]),weights)
        accuracy[count+1]=np.sum(a==b)/(a.shape[0])
        dictionary[maxk]=accuracy
        for i in k_list[:argmaxk]:
            accuracy=np.zeros(len(cv),dtype=float)
            for count in range(len(cv)-1):
                a=predict2(X[cv[count][1],:],ind[count][:,:i],dis[count][:,:i],np.take(y,cv[count][0]),weights)
                b=y[count*y_true:(count+1)*y_true]
                accuracy[count]=np.sum(a==b)/(a.shape[0])
            a=predict2(X[cv[count+1][1],:],ind2[:,:i],dis2[:,:i],np.take(y,cv[count+1][0]),weights)
            b=y[(count+1)*y_true:]
            accuracy[count+1]=np.sum(a==b)/(a.shape[0])
            dictionary[i]=accuracy
        return dictionary
    else:
        print("score doesnt exist")
        


def predict2(X,ind,dis,y,weights): 
    X=X.astype(float)
    pred=np.zeros(X.shape[0])
    for j in range(X.shape[0]):
        a=0
        union=np.zeros(ind[j].shape[0])
        for i in ind[j]:
            union[a]=y[i]
            a+=1
        size=0
        ans=np.unique(union) #Объеденные метки класса
        ans2=np.zeros(ans.shape[0])# Кол-во меток по классам
        if(weights==False):
            for k in (np.array(ans,dtype=int)):
                count=0
                for i in ind[j]:
                    if(k==y[i]):
                        ans2[size]+=1
                    count+=1
                size+=1
        else:
            for k in (np.array(ans,dtype=int)):
                count=0
                for i in ind[j]:
                    if(k==y[i]):
                        ans2[size]+=1*(1/(0.000001 + dis[j][count]))
                    count+=1
                size+=1
        pred[j]=np.take(ans,np.argmax(ans2))
    return np.array(pred,dtype=int)
