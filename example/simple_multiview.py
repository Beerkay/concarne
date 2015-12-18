# -*- coding: utf-8 -*-

"""
This example illustrates how simple it is to train a classifier using
contextual data.

It illustrates the exemplary use of the multi-view pattern; for more info
on how to use other patterns, check out synthetic.py.

For a realistic example with real data check out handwritten.py. 

For more details see the documentation and the paper
http://arxiv.org/abs/1511.06429 
"""

from __future__ import print_function

import concarne
import concarne.patterns
import concarne.training

import lasagne
import theano.tensor as T

try:
    import sklearn.linear_model as sklm
except:
    print (
"""You don't have scikit-learn installed; install it to compare
contextual learning to simple supervised learning""")
    sklm = None

import numpy as np



if __name__ == "__main__":
    
    #--------------------------------------------------------    
    # Generate the data
    
    num_samples = 300
    
    input_dim = 50
    context_dim = 50
    
    # generate some random data with 100 samples and 5 dimensions
    X = np.random.randn(num_samples, input_dim)
    
    # select the third dimension as the relevant for our classification
    # task
    S = X[:, 2:3]
    
    # The labels are simply the sign of S 
    # (note the downcast to int32 - this is required by theano)
    y = np.asarray(S > 0, dtype='int32').reshape( (-1,) )
    # This means we have 2 classes - we will use that later for building
    # the pattern
    num_classes = 2
    
    # Now let's define some context: we simulate an additional sensor
    # which contains S, but embedded into a different space
    C = np.random.randn(num_samples, context_dim)
    # set second dimension of C to correspond to S
    C[:, 1] = S[:,0]
    
    # let's make it harder to find S in X and C by applying a random rotations
    # to both data sets
    R = np.linalg.qr(np.random.randn(input_dim, input_dim))[0] # random linear rotation
    X = X.dot(R)

    Q = np.linalg.qr(np.random.randn(context_dim, context_dim))[0] # random linear rotation
    C = C.dot(Q)
   
    #--------------------------------------------------------
    # Define the pattern
    
    # now that we have some data, we can use a contextual pattern to learn
    # from it. 
    # since X and C are two different "views" of the relevant data S,
    # the multi-view pattern is the most natural choice.
    
    # The pattern needs three functions: phi(X) which maps X to an intermediate
    # representation (that should somewhat correspond to S); psi which 
    # performs classification using phi(X); and beta(C) which maps C to S.
    # The goal of the multi-view pattern is to find phi and beta, s.t.
    # phi(X)~beta(X) and psi s.t. that psi(phi(X))~Y
    
    # Let's first define the theano variables which will represent our data
    input_var = T.matrix('inputs')  # for X
    target_var = T.ivector('targets')  # for Y
    context_var = T.matrix('contexts')  # for C

    # Now define input layers; in our example X and C will be the inputs
    input_layer = lasagne.layers.InputLayer(shape=(None, input_dim),
                                        input_var=input_var)
    context_input_layer = lasagne.layers.InputLayer(shape=(None, context_dim),
                                        input_var=context_var)

        
    # Now define the functions - we choose linear functions
        
    # Size of the intermediate representation phi(X); since S is 1-dim,
    # phi(X) can also map to a 1-dim vector
    idim = 1 
    phi = lasagne.layers.DenseLayer(input_layer, idim, nonlinearity=None, b=None, name="phi")
    psi = lasagne.layers.DenseLayer(phi, num_classes, nonlinearity=lasagne.nonlinearities.softmax, b=None, name="psi")
    beta = lasagne.layers.DenseLayer(context_input_layer, idim, nonlinearity=None, b=None, name="beta")
    
    # now that we have figured our all functions, we can pass them to the pattern
    pattern = concarne.patterns.MultiViewPattern(phi=phi, psi=psi, beta=beta,
                                                 target_var=target_var, 
                                                 context_var=context_var,
                                                 # we have to define two loss functions: 
                                                 # the target loss deals with optimizing psi and phi wrt. X & Y
                                                 target_loss=lasagne.objectives.categorical_crossentropy,
                                                 # the context loss deals with optimizing beta and phi wrt. X & C,
                                                 # for multi-view it is beta(C)~phi(X)
                                                 context_loss=lasagne.objectives.squared_error)

    #--------------------------------------------------------
    # Training 
    
    # first split our data into training, test, and validation data
    split = num_samples/3

    X_train = X[:split]
    X_val = X[split:2*split]
    X_test = X[2*split:]
    
    y_train = y[:split]
    y_val = y[split:2*split]
    y_test = y[2*split:]

    C_train = C[:split]
    
    
    # instantiate the PatternTrainer which trains the pattern via stochastic
    # gradient descent
    trainer = concarne.training.PatternTrainer(pattern,
                                               num_epochs=100,
                                               learning_rate=0.01,
                                               batch_size=10,
                                               momentum=0.9,
                                               procedure='simultaneous',
                                               verbose=True,
                                               )
   
    # we use the fit_XYC method because our X, Y and C data all have the same
    # size. Also note the [] our C_train - because it is possible to pass
    # multiple contexts to some patterns, you have to pass context data
    # in a list.
    trainer.fit_XYC(X_train, y_train, [C_train], X_val=X_val, y_val=y_val)

    # print some statistics
    print("=================")
    print("Test score...")
    trainer.score(X_test, y_test, verbose=True)    
    
    # Let's compare to supervised learning!
    if sklm is not None:
        # let's try different regularizations
        for c in [1e-5, 1e-1, 1, 10, 100, 1e5]:
            lr = sklm.LogisticRegression(C=c)
            lr.fit(X_train, y_train)
            print ("Logistic Regression (C=%f) accuracy = %.3f %%" % (c, 100*lr.score(X_test, y_test)))