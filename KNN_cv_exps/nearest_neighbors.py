import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KNeighborsClassifier
from scipy.sparse import csr_matrix
import sklearn.datasets
import scipy.spatial
class KNN_classifier:
    def __init__(self,k,strategy,metric,weights,test_block_size):
        self.k=k
        self.metric=metric
        self.strategy=strategy
        self.weights=weights
        self.test_block_size=test_block_size
    def fit(self,X,y):
        if(self.strategy=='my_own'):
            self.X=X.astype(float)
            self.y=y
        else:
            self.X=X.astype(float)
            self.y=y
            self.neigh=NearestNeighbors(n_neighbors=self.k,algorithm=self.strategy,metric=self.metric)
            self.neigh.fit(X,y)
        return self

    
    def find_kneighbors(self,X,return_distance):
        if(self.strategy=="my_own"):
            X=X.astype(float)
            folds=X.shape[0]//self.test_block_size
            ostatok=X.shape[0]%self.test_block_size
            t=0
            IND2=np.zeros((X.shape[0],self.k),dtype=int)
            DIS2=np.zeros((X.shape[0],self.k),dtype=float)
            for i in range(folds):
                if (self.metric=="euclidean"):
                    EUC=np.sum( (X[i*self.test_block_size:(i+1)*self.test_block_size,np.newaxis]-self.X)**2,axis=2)**0.5
                    for j in range(self.test_block_size):
                        IND2[t]=np.argsort(EUC[j])[:self.k]
                        DIS2[t]=np.take(EUC[j],IND2[t])[:self.k]
                        t+=1
                elif(self.metric=="cosine"):
                    norm_X=(np.sum(X**2,axis=1)**0.5)[(i)*self.test_block_size:(i+1)*self.test_block_size,np.newaxis]
                    norm_Y=(np.sum(self.X**2,axis=1)**0.5)
                    norm_X[norm_X==0]=1
                    norm_Y[norm_Y==0]=1
                    COS=np.arccos((np.sum(X[i*self.test_block_size:(i+1)*self.test_block_size,np.newaxis]*self.X,axis=2))/(norm_X*norm_Y))
                    for j in range(self.test_block_size):
                        IND2[t]=np.argsort(COS[j])[:self.k]
                        DIS2[t]=np.take(COS[j],np.argsort(COS[j]))[:self.k]
                        t+=1
                else : print("your metric doesnt exist")
            if(ostatok!=0):
                for i in range(ostatok):
                    if (self.metric=="euclidean"):
                        EUC=np.sum( (X[(folds)*self.test_block_size:,np.newaxis]-self.X)**2,axis=2)**0.5
                        IND2[t]=np.argsort(EUC[i])[:self.k]
                        DIS2[t]=np.take(EUC[i],np.argsort(EUC[i]))[:self.k]
                        t+=1
                    elif(self.metric=="cosine"):
                        norm_X=(np.sum(X**2,axis=1)**0.5)[(folds)*self.test_block_size:,np.newaxis]
                        norm_Y=(np.sum(self.X**2,axis=1)**0.5)
                        norm_X[norm_X==0]=1
                        norm_Y[norm_Y==0]=1
                        COS=np.arccos((np.sum(X[(folds)*self.test_block_size:,np.newaxis]*self.X,axis=2))/(norm_X*norm_Y))
                        IND2[t]=np.argsort(COS[i])[:self.k]
                        DIS2[t]=np.take(COS[i],np.argsort(COS[i]))[:self.k]
                        t+=1
                    else : print("your metric doesnt exist")
            
            if(return_distance==False):
                return IND2
            else : return (IND2,DIS2)
        else :
            IND=self.neigh.kneighbors(X)[1]
            DIS=self.neigh.kneighbors(X)[0]
            if(return_distance==False):
                return IND
            else : return (IND,DIS)
                        
    
    def predict(self,X):
        X=X.astype(float)
        pred=np.zeros(X.shape[0])
        Y=self.find_kneighbors(X,True)
        ind=Y[0]
        dis=Y[1]
        for j in range(X.shape[0]):
            a=0
            union=np.zeros(ind[j].shape[0])
            for i in ind[j]:
                union[a]=self.y[i]
                a+=1
            size=0
            ans=np.unique(union) #Объеденные метки класса
            ans2=np.zeros(ans.shape[0])# Кол-во меток по классам
            if(self.weights==False):
                for k in (np.array(ans,dtype=int)):
                    count=0
                    for i in ind[j]:
                        if(k==self.y[i]):
                            ans2[size]+=1
                        count+=1
                    size+=1
            else:
                for k in (np.array(ans,dtype=int)):
                    count=0
                    for i in ind[j]:
                        if(k==self.y[i]):
                            ans2[size]+=1*(1/(0.000001 + dis[j][count]))
                        count+=1
                    size+=1
            pred[j]=np.take(ans,np.argmax(ans2))
        return np.array(pred,dtype=int)
