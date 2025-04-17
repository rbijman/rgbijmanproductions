# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 14:40:28 2025

@author: rbijman
"""

#%% Logistic regression

import numpy as np
from sklearn.linear_model import LogisticRegression

dataset = [[-2.0011, 0],
           [-1.4654, 0],
           [0.0965, 0],
           [1.3881, 0],
           [3.0641, 0],
           [7.6275, 1],
           [5.3324, 1],
           [6.9225, 1],
           [8.6754, 1],
           [7.6737, 1]]

X = np.array(dataset)[:,0:1]
Y = np.array(dataset)[:,1]

X

clf_LR = LogisticRegression(C=1.0,penalty='l2', tol=0.0001)

clf_LR.fit(X,Y)

Y_pred = clf_LR.predict(X)

clf_LR.predict_proba(X)

np.column_stack((Y,Y_pred))

clf_LR.predict(np.array([4.1]).reshape(1,-1))


#%% Introduction to Classification

from sklearn.datasets import fetch_openml
mnist = fetch_openml(name='mnist_784')

#%% Understanding MNIST

X,y = mnist['data'], mnist['target']

y.astype("float")


import matplotlib.pyplot as plt

def viz(n):
    plt.imshow(X[n].reshape(28,28))
    plt.show()

viz(4)


#%% SGD Stochastic Gradient Descent

from sklearn.model_selection import train_test_split

X = np.array(X)
Y = np.array(y).astype('int')

np.unique(Y,return_counts=True)

X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.2, shuffle=True, random_state=42)

#or in case you want an exact split 
num_split = 60000

X_train, X_test, Y_train, Y_test = X[:num_split], X[num_split:], Y[:num_split], Y[num_split:]
# to shuffle:
shuffle_index = np.random.permutation(num_split)
X_train,Y_train = X_train[shuffle_index], Y_train[shuffle_index]

#Training a Binary Classifyer

Y_train_0 = (Y_train == 0)
Y_train_0
Y_test_0 = (Y_test == 0)
Y_test_0

np.unique(Y_train_0,return_counts=True)

#SGD classifier (Linear classifiers (SVM,Logistic regression) with SGD training)

from sklearn.linear_model import SGDClassifier

clf = SGDClassifier(random_state=0)
clf.fit(X_train,Y_train_0)

viz(1000)
clf.predict(X[1000].reshape(1,-1))

#%% Performance Measure and Stratified K-Fold

from sklearn.model_selection import StratifiedKFold
from sklearn.base import clone

clf = SGDClassifier(random_state=0)

skfolds = StratifiedKFold(n_splits=3, random_state=100, shuffle=True)

for train_index, test_index in skfolds.split(X_train,Y_train_0):
    clone_clf = clone(clf)
    x_train_fold = X_train[train_index]
    y_train_folds = (Y_train_0[train_index])
    x_test_fold = X_train[test_index]
    y_test_fold = (Y_train_0[test_index])
    
    clone_clf.fit(x_train_fold,y_train_folds)
    y_pred = clone_clf.predict(x_test_fold)
    n_correct = sum(y_pred == y_test_fold)
    print("{0:.4f}".format(n_correct/len(y_pred)))
    
#MORE efficient and actually a wrapper around what we see here above

from sklearn.model_selection import cross_val_score
cross_val_score(clf,X_train,Y_train_0,cv=3,scoring='accuracy')

#%% Confusion Matrix
# Danger of blindly applying evaluator as a performance measure
# When you are trying to classify between being a 0 or not and 90% of your data is not a 0, you will already in 90% of the cases be 'correct' 

from sklearn.model_selection import cross_val_predict
Y_train_0_pred = cross_val_predict(clf, X_train,Y_train_0,cv=3)

from sklearn.metrics import confusion_matrix
confusion_matrix(Y_train_0, Y_train_0_pred)

#%% Precission
from sklearn.metrics import precision_score
precision_score(Y_train_0, Y_train_0_pred)

#%% Recall
from sklearn.metrics import recall_score
recall_score(Y_train_0,Y_train_0_pred)

#%% f1
from sklearn.metrics import f1_score
f1_score(Y_train_0,Y_train_0_pred)

#%% Precission Recall Tradeoff

clf.decision_function(X[1000].reshape(1,-1))

y_scores = cross_val_predict(clf, X_train, Y_train_0, cv=3,method="decision_function")

#Increase precission, reduses Recall and vice versa

#Precission Recall tradeoff curve
from sklearn.metrics import precision_recall_curve
precission, recall, thresholds = precision_recall_curve(Y_train_0,y_scores)
thresholds

#PR curve
plt.plot(precission,recall)
plt.show()

#%% ROC curve Receiver Operator Characteristics Curve (FP/TN+FP) = 1 - (TN/TN+FP)
import matplotlib.pyplot as plt


#ROC curve
from sklearn.metrics import roc_curve
fpr, tpr, thresholds = roc_curve(Y_train_0,y_scores)
plt.plot(fpr,tpr)
plt.show()

from sklearn.metrics import roc_auc_score
AUC = roc_auc_score(Y_train_0,y_scores)
AUC

# Use PR curve whenever the Positive class is rare
# Use ROC curve whenever the negative class is rare
