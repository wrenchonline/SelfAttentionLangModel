#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 11:51:15 2019

@author: Hesham El Abd
@Description: The Module uses the Encoder unit of the transformer to construct
two Types of models the first is the Modeler which is used to construct 
language models and the second is the annotator which is used to map an input
sequene to a specific numerical label.
"""
# loadthe modules
from Parts import EncoderParts
import tensorflow as tf
from __future__ import print_function
# define the models
class Modeler(tf.keras.Model):
    def __init__(self,embedding_dim,
                 vocabulary_size,
                 conditional_string_length,
                 num_encoder_layer,num_heads,
                 num_neuron_pointwise,
                 rate=0.1,
                 return_attent_weights=True):
        """
        The Modeler is a model that is used to construct language models.
        ## inputs:
        
        # embedding_dim: is the embeedind dimension for each input integer to 
        the model.
        
        # vocabulary_size: is the number of unique words, characters or tokens 
        in the language.i.e. input language.
        
        # conditional_string_length: is the input sequence length.
        
        # num_encoder_layer: is the number of layers inside the encoder.
        
        # num_heads: is the number of heads inside the encoder, used for
        Multi-headed attention. which is used to increase the power of the 
        model to learn from different representaional spaces. 
        
        # num_neuron_pointwise: is the number of neurons in the feed-forward
        point wise attention neuros.
        
        # rate: is the dropout rate. 
        """
        super(Modeler,self).__init__()
        
        self.return_attent_weights=return_attent_weights
        
        self.encoder=EncoderParts.Encoder(num_layers=num_encoder_layer,
                             d_model=embedding_dim, 
                             num_heads=num_heads, 
                             dff=num_neuron_pointwise, 
                             input_vocab_size=vocabulary_size,
                             seq_len=conditional_string_length,
                             rate=rate,
                             return_attent_weights=return_attent_weights)
        self.dropout=tf.keras.layers.Dropout(rate=rate)
        self.pred_logits =tf.keras.layers.Dense(vocabulary_size)
    @tf.function
    def call(self, x,training):
        mask=EncoderParts.create_padding_mask(x)
        if not training and  self.return_attent_weights:
            encoded_seq, attent_weights=self.encoder(x,training,mask)
            encoded_seq=self.dropout(encoded_seq,training=training)
            modelPredictionLogit=self.pred_logits(encoded_seq)
            return self.pred_logits(encoded_seq), attent_weights
            
        else: 
            encoded_seq=self.encoder(x,training,mask)
            encoded_seq=self.dropout(encoded_seq,training=training)
            modelPredictionLogit=self.pred_logits(encoded_seq)
            return modelPredictionLogit
        
class Annotator(tf.keras.Model):
    def __init__(self,embedding_dim,
                 vocabulary_size,
                 sequence_length,
                 num_encoder_layer,
                 num_heads,
                 num_neuron_pointwise,
                 rate=0.1,
                 return_attent_weights=True,
                 distilation_units=10,
                 num_dense_units=1,
                 dense_activation=None):
        """
        The Annotator is a model that is used to label an input sequences, 
        for example, classifiying an input sequence into categories or doing 
        regression on the input sequence. The Annotator is composite of two 
        parts, the first is the Encoder which is used to encode an input 
        sequences and the second is a Dense network that is used for mapping 
        the encoded sequences into numerical labels.
        
        ## inputs:
        # embedding_dim: is the embedding dimension for each input integer to 
        the model.
        
        # vocabulary_size: is the number of unique words, characters or tokens 
        in the sequences.
        
        # sequence_length: is max input length, shorter sequences should be zero
        padded before being fed to the model. Masking is automattically enabled
        for zero values.
        
        # num_encoder_layer: is the number of layers inside the encoder.
        
        # num_heads: is the number of heads inside the encoder, used for
        Multi-headed attention. which is used to increase the power of the 
        model to learn from different representaional spaces. 
        
        # num_neuron_pointwise: is the number of neurons in the feed-forward
        point wise attention neuros.
        
        # rate: is the dropout rate,the same value will be used accross all the
        dropout layer of the model.
        
        # return_attent_weights: a bool, determine wherther or not to return 
        the self-attention weights of the model. 
        
        # distilation_units: is the number of dense units that set on top of
        the encoder 3D output and reduce the dimensionality of the last axis
        from num_neuron_pointwise to distilation_units.
        
        # num_dense_units: Is the number of neuron in the last layer of the 
        model, usually one for binary classification and regression problems 
        and equals to number of classes incase of multi-class 
        classfications problems.
        
        # dense_activation: is the activation function that will be applied to 
        the last dense layer, for example Relu or sigmoid, default
        is None. 
        """
        super(Annotator,self).__init__()
        
        self.return_attent_weights=return_attent_weights
        
        self.encoder=EncoderParts.Encoder(num_layers=num_encoder_layer,
                             d_model=embedding_dim, 
                             num_heads=num_heads, 
                             dff=num_neuron_pointwise, 
                             input_vocab_size=vocabulary_size,
                             seq_len=sequence_length,
                             rate=rate,
                             return_attent_weights=return_attent_weights)
        
        self.dis_units=tf.keras.layers.Dense(distilation_units,
                                             activation="relu")
        
        self.dropout=tf.keras.layers.Dropout(rate=rate)
        
        self.pred_logits =tf.keras.layers.Dense(num_dense_units,
                                                activation=dense_activation)
    @tf.function   
    def call(self, x,training):
        mask=EncoderParts.create_padding_mask(x)
        if not training and self.return_attent_weights:
            encoded_seq, attent_weights=self.encoder(x,training,mask)
            encoded_seq=self.dropout(encoded_seq,training)
            encoded_seq=self.dis_units(encoded_seq)
            encoded_seq=tf.reshape(encoded_seq,[-1,
                                 encoded_seq.shape[1]*encoded_seq.shape[2]])
            modelPredictionLogit=self.pred_logits(encoded_seq)
            return self.pred_logits(encoded_seq), attent_weights
            
        else: 
            encoded_seq=self.encoder(x,training,mask)
            encoded_seq=self.dropout(encoded_seq,training)
            encoded_seq=self.dis_units(encoded_seq)
            encoded_seq=tf.reshape(encoded_seq,[-1,
                                    encoded_seq.shape[1]*encoded_seq.shape[2]])
            modelPredictionLogit=self.pred_logits(encoded_seq)
            return modelPredictionLogit

class AnnotatorGRU(tf.keras.Model):
    def __init__(self,embedding_dim,
                 vocabulary_size,
                 sequence_length,
                 num_encoder_layer,
                 num_heads,
                 num_neuron_pointwise,
                 rate=0.1,
                 return_attent_weights=True,
                 unitsGRU=10,
                 num_dense_units=1,
                 dense_activation=None):
        """
        The Annotator is a model that is used to label an input sequences, 
        for example, classifiying an input sequence into categories or doing 
        regression on the input sequence. The AnnotatorGRU is composite of three
        parts, the first is the Encoder which is used to encode an input 
        sequences and the second is a light weight GRU network that is used 
        for mapping the 3D tensor produce by the encoder into a 2D tensor that
        will be fed to the third part which is a dense network that make the 
        output of the model.
        
        ## inputs:
        # embedding_dim: is the embedding dimension for each input integer to 
        the model.
        
        # vocabulary_size: is the number of unique words, characters or tokens 
        in the sequences.
        
        # sequence_length: is max input length, shorter sequences should be zero
        padded before being fed to the model. Masking is automattically enabled
        for zero values.
        
        # num_encoder_layer: is the number of layers inside the encoder.
        
        # num_heads: is the number of heads inside the encoder, used for
        Multi-headed attention. which is used to increase the power of the 
        model to learn from different representaional spaces. 
        
        # num_neuron_pointwise: is the number of neurons in the feed-forward
        point wise attention neuros.
        
        # rate: is the dropout rate,the same value will be used accross all the
        dropout layer of the model.
        
        # return_attent_weights: a bool, determine wherther or not to return 
        the self-attention weights of the model. 
        
        # GRU units: is the number of dense units that set on top of
        the encoder 3D output and produce a 2D tesnor representation out of it.
        
        # num_dense_units: Is the number of neuron in the last layer of the 
        model, usually one for binary classification and regression applications 
        and equal to number of classes incase of multi-class 
        classfications problems.
        
        # dense_activation: is the activation function that will be applied to 
        the last dense layer, for example Relu or sigmoid, default
        is None. 
        """
        super(AnnotatorGRU,self).__init__()
        
        self.return_attent_weights=return_attent_weights
        
        self.encoder=EncoderParts.Encoder(num_layers=num_encoder_layer,
                             d_model=embedding_dim, 
                             num_heads=num_heads, 
                             dff=num_neuron_pointwise, 
                             input_vocab_size=vocabulary_size,
                             seq_len=sequence_length,
                             rate=rate,
                             return_attent_weights=return_attent_weights)
        
        self.gru=tf.keras.layers.GRU(unitsGRU,
                                             activation="relu")
        
        self.dropout=tf.keras.layers.Dropout(rate=rate)
        
        self.pred_logits =tf.keras.layers.Dense(num_dense_units,
                                                activation=dense_activation)
    @tf.function   
    def call(self, x,training):
        mask=EncoderParts.create_padding_mask(x)
        if not training and self.return_attent_weights:
            encoded_seq, attent_weights=self.encoder(x,training,mask)
            encoded_seq=self.dropout(encoded_seq,training=training)
            encoded_seq=self.gru(encoded_seq)
            encoded_seq=self.dropout(encoded_seq,training=training)
            modelPredictionLogit=self.pred_logits(encoded_seq)
            return self.pred_logits(encoded_seq), attent_weights
            
        else: 
            encoded_seq=self.encoder(x,training,mask)
            encoded_seq=self.dropout(encoded_seq,training=training)
            encoded_seq=self.gru(encoded_seq)
            encoded_seq=self.dropout(encoded_seq,training=training)
            modelPredictionLogit=self.pred_logits(encoded_seq)
            return modelPredictionLogit