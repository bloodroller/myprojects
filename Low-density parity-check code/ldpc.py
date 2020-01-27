import numpy as np

def rref(B1):
    B = np.copy(B1)
    B=B.astype(int)
    n,m=B.shape[0],B.shape[1]
    j=0
    for i in range(n):
        while((np.sum(B[(i):,j])==0)):
            j=j+1
            if(j==m-1):
                break
        if(B[i,j]==0):
            for x in range(i+1,n):
                if(B[x,j]!=0):
                    a=np.copy(B[i])
                    b=np.copy(B[x])
                    B[x]=a
                    B[i]=b
                    break
        B[i]=(B[i]/B[i,j])%2
        for k in range(n):
            if(k!=i):
                B[k]=(B[k]-B[i]*B[k,j])%2
        j=j+1
    return B

def get_eye_ind(mat):
    rank=mat.shape[0]
    ind=[]
    mas_eyes=np.eye(rank)
    i=0
    for j in range(mat.shape[1]):
        check=np.equal(mas_eyes[:,i],mat[:,j])
        if(np.sum(check)==rank):
            ind.append(j)
            i=i+1
        if(i==rank):
            break
    return ind

def make_generator_matrix(H):
    M=H.copy()
    m, n = M.shape[0], M.shape[1]
    k = n - m
    if(m != np.linalg.matrix_rank(M)):
        raise DegenerateMatrixError('given check matrix is degenerate')
    M = rref(M)
    eye_ind = get_eye_ind(M)
    ind = np.delete(np.arange(n),eye_ind)
    G = np.zeros((n,k),dtype=np.int8)
    G[ind,:] = np.eye(k)
    G[eye_ind] = M[:,ind]
    return (G, ind)


def update_messages_h_to_e(mu_h_to_e, mu_e_to_h, s, factor_index, var_indices, output_var_indices, non_converged_indices, trim=1e-8):
    num_synd = np.arange(non_converged_indices.shape[0])
    pl = np.zeros((num_synd.shape[0],2))
    for k in output_var_indices:
        j = np.where(var_indices==k)[0]
        delta_pl = np.prod(1 - 2 * mu_e_to_h[factor_index,np.delete(var_indices,j),:][:,non_converged_indices],axis=0)
        pl[num_synd,0] = 0.5 * (1 + delta_pl)
        pl[num_synd,1] = 0.5 * (1 - delta_pl)
        mu_h_to_e[factor_index,k,non_converged_indices] = pl[num_synd,(s[factor_index,non_converged_indices]+1) % 2]


def update_messages_e_to_h_and_beliefs(mu_e_to_h, beliefs, mu_h_to_e, q, var_index, factor_indices, output_factor_indices, non_converged_indices, trim=1e-8):
    for k in output_factor_indices:
        j=np.where(factor_indices==k)[0]
        p_1 = q * np.prod(mu_h_to_e[np.delete(factor_indices,j),var_index,:][:,non_converged_indices],axis=0)
        p_0 = (1-q) * np.prod(1 - mu_h_to_e[np.delete(factor_indices,j),var_index,:][:,non_converged_indices],axis=0)
        mu_e_to_h[k,var_index,non_converged_indices] = np.divide(p_1,(p_1+p_0),where=((p_1+p_0)!=0))
    p_1_b = q * np.prod(mu_h_to_e[factor_indices,var_index,:][:,non_converged_indices],axis=0)
    p_0_b = (1-q) * np.prod(1 - mu_h_to_e[factor_indices,var_index,:][:,non_converged_indices],axis=0)
    beliefs[var_index,non_converged_indices] = np.divide(p_1_b,(p_1_b+p_0_b),where=((p_1_b+p_0_b)!=0))


def decode(s, H, q, schedule='parallel', max_iter=200, tol_beliefs=1e-4, display=False):
    m, n, num_s = H.shape[0], H.shape[1], s.shape[1]
    mu_e_to_h = np.full((m,n,num_s),q)
    mu_h_to_e = np.zeros_like(mu_e_to_h)
    output_factor_indices = np.arange(m)
    output_var_indices = np.arange(n)
    non_converged_indices = np.arange(num_s)
    beliefs = np.zeros((n, num_s))
    num_iters_decod = np.full(num_s,max_iter)
    status_decod = np.full(num_s,2)
    lst = []
    if( schedule == 'parallel'):
        for factor_index in range(m):
            e_ind = np.where(H==1)[0]
            args = np.where(e_ind==factor_index)[0]
            var_indices = np.where(H==1)[1][args]
            update_messages_h_to_e(mu_h_to_e, mu_e_to_h, s, factor_index, var_indices,
                                   output_var_indices, non_converged_indices)
        for i in range(max_iter):
            for var_index in range(n):
                args = np.where(np.where(H==1)[1]==var_index)[0]
                factor_indices = np.where(H==1)[0][args]
                update_messages_e_to_h_and_beliefs(mu_e_to_h, beliefs, mu_h_to_e, q, var_index, factor_indices,
                                                   output_factor_indices, non_converged_indices)
                
            hat_e = np.argmax( np.concatenate((1-beliefs[:,:,np.newaxis],beliefs[:,:,np.newaxis]),axis=2), axis=2)
            
            for j in np.delete(list(range(num_s)),lst):
                if( np.sum((np.dot(H,hat_e)%2)[:,j]==s[:,j]) == m):
                    lst.append(j)
                    num_iters_decod[j] = i
                    status_decod[j] = 0
                elif (np.sum( (beliefs[:,j]==beliefs[:,j][0])) == n):
                    status_decod[j] = 1
                    lst.append(j)
            if(len(lst)==num_s):
                break
                                 
            for factor_index in range(m):
                e_ind = np.where(H==1)[0]
                args = np.where(e_ind==factor_index)[0]
                var_indices = np.where(H==1)[1][args]
                update_messages_h_to_e(mu_h_to_e, mu_e_to_h, s, factor_index, var_indices,
                                       output_var_indices, non_converged_indices)
            if(display==True):
                print(i)
                
    if( schedule == 'sequential'):
        for i in range(max_iter):
            for var_index in range(n):
                output_var_indices = np.array([var_index])
                args = np.where(np.where(H==1)[1]==var_index)[0]
                factor_indices = np.where(H==1)[0][args]
                for factor_index in factor_indices:
                    e_ind = np.where(H==1)[0]
                    args2 = np.where(e_ind==factor_index)[0]
                    var_indices = np.where(H==1)[1][args2]
                    update_messages_h_to_e(mu_h_to_e, mu_e_to_h, s, factor_index, var_indices,
                                                       output_var_indices, non_converged_indices)
                update_messages_e_to_h_and_beliefs(mu_e_to_h, beliefs, mu_h_to_e, q, var_index, factor_indices,
                                                               factor_indices, non_converged_indices)
            hat_e = np.argmax( np.concatenate((1-beliefs[:,:,np.newaxis],beliefs[:,:,np.newaxis]),axis=2), axis=2)
            
            for j in np.delete(list(range(num_s)),lst):
                if( np.sum((np.dot(H,hat_e)%2)[:,j]==s[:,j]) == m):
                    lst.append(j)
                    num_iters_decod[j] = i
                    status_decod[j] = 0
                elif (np.sum( (beliefs[:,j]==beliefs[:,j][0])) == n):
                    status_decod[j] = 1
                    lst.append(j)
            if(len(lst)==num_s):
                break
                
            if(display==True):
                print(i)
                
    results = {"num_iter":num_iters_decod,"status":status_decod}

    return (hat_e,results)


def estimate_errors(H, q, num_syndromes=200, display=False, schedule='parallel'):
    e = np.random.binomial(1, q, (H.shape[1], num_syndromes))
    s = H.dot(e) % 2
    [hat_e,results] = decode(s, H, q, schedule)
    err_bit = np.sum(hat_e!=e)/(e.shape[1]*e.shape[0])
    err_block = np.sum(np.sum(hat_e!=e,axis=0)>=1)/e.shape[1]
    diver = len(np.where(results['status']==2)[0])/num_syndromes
    
    return (err_bit, err_block, diver)

