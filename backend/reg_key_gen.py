# -*- coding: utf-8 -*-
import os, hashlib

def main():
    seq=[1,0,3,7,4,2,5,6]
    pc_name=os.getenv('COMPUTERNAME', default='LocalMachine')
    seed=f'{pc_name}*'
    hash_str=hashlib.sha256(seed.encode('utf-8')).hexdigest()
    key=''.join([hash_str[i] for i in seq])
    print(key, '<=', seed)

if __name__=='__main__':
    main()
