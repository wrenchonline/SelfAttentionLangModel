#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 10:31:43 2019

@author: Hesham El Abd 
@Description: Visualization tools for the TransFormer self attention encoder
"""
import tensorflow as tf
import numpy as np
import matplotlib.pylab as plt
## 
def VizAttenMat(atten_Matrix):
    """
    A function that takes an input 2D Tensor and visualize it using matplotlib
    """
    assert len(atten_Matrix.shape)==2, "your input should be a symetrical 2D matrix"
    assert atten_Matrix.shape[0]==atten_Matrix.shape[1], "your input should be a symetrical 2D matrix"
    plt.matshow(atten_Matrix)
    plt.colorbar()
    plt.show()

def VizSelfAtten(atten_Tensor,num_example,num_heads,each_head):
    """
    A function to visualize the self-attention tensor generated by the 
    multiheaded attention layer of the transformer model
    ## inputs: 
    atten_Tensor: is a 4D Tensor of shape(batch_size,num_heads,seq_len,seq_len)
    
    num_example: is the number of example to visualize, they will be extracted
    along the first axis of the atten_Tensor starting from the 0th element.
    
    num_heads: the number of heads to visualize, They will be extracted from
    the 2nd axis of the tensor starting from 0.
    
    each_head: a bool, whether to visualize the attention of each head
    indivdually or to take the average across the number of heads
    """
    assert len(atten_Tensor.shape)==4,"Invalid input Tensor shape, please check your input"
    assert atten_Tensor.shape[2]==atten_Tensor.shape[3],""" bad input tensor, please check your tensor"""
    assert num_example>=1,"Number of examples should be at least one."
    assert num_heads>=1, "Number of heads should be at least one."
    assert isinstance(each_head,bool)," each_head should be a of bool type"
    print("Number of Examples: "+str(atten_Tensor.shape[0]))
    print("Number of heads: "+str(atten_Tensor.shape[1]))
    print("The sequence length: "+str(atten_Tensor.shape[2]))
    if each_head:
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    