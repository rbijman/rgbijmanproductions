# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 14:40:31 2025

@author: rbijman
"""

# Suport Vector machines can be used for Regression, Classification and outlier detection
# Supose we have 2 classes, SVM tries to find the best way to seperate the two classes
# The seperating line, is the line that allows for the largest margins between the two classes
# The samples that are closest to the sepearting line (or hyperplane) are called 'support vectors'

#%% Linear SVM Classification
# support vectors

# seperate with a straight line (linearly sepearable problems only)

# Margin: 
    # - hard margin classification:
        # Strictly based on those that are at the margin between the two classes
        # However this is senstive to outliers
    # - soft margin classification:
        # Widen the margin and allows for violation
        # Within Python sklearn you control the width of the margin
        # Control with C hyperparameter:
            # smaller C leads to wider street but more margin violations
            # high C leads to feweter margin violations but ends op with a smaller marging
    # - SVM is highly sensitive to feature scaling


import numpy as np
import pandas as pd
import seaborn as sns
from sklearn import datasets
from sklearn import svm
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Linear SVM implementation
df = sns.load_dataset('iris')
col = ['petal_length','petal_width']
X = df.loc[:,col]
species_to_num = {'setosa':0,'versicolor':1,'virginica':2}
df['tmp'] = df['species'].map(species_to_num)
Y =  df['tmp']

X_train, X_test, Y_train, Y_test = train_test_split(X,Y,train_size=0.8,random_state=3)

sc_x = StandardScaler()
X_std_train= sc_x.fit_transform(X_train)

C = 0.001
clf = svm.SVC(kernel='linear',C=C)
clf.fit(X_std_train,Y_train)

#Cross Validation within Train dataset
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import confusion_matrix, precision_score, recall_score,f1_score

results = cross_val_score(clf, X_std_train, Y_train, cv=10,scoring='accuracy')

print(f'Average Accuracty: {np.mean(results)}')
print(f'Accurace STD: {np.std(results)}')

Y_train_pred = cross_val_predict(clf,X_std_train,Y_train,cv=3)
confusion_matrix(Y_train,Y_train_pred)

precision_score(Y_train, Y_train_pred,average='weighted')
recall_score(Y_train, Y_train_pred, average='weighted')
f1_score(Y_train,Y_train_pred,average='weighted')

#Non-Linear SVM implementation (Kernal=polynomial)
#Idea is to transform the data such that it becomes possible to draw a streight line

# Delta compared to Linear SVM:
    # clf = svm.SVC(kernel='poly',degree=n,C=C,gamma='auto')

#Visualize SVM
Xv = X_std_train.reshape(-1,1)
h = 0.02
x_min,x_max = Xv.min(),Xv.max() + 1
y_min,y_max = Y_train.min(),Y_train.max() + 1
xx,yy = np.meshgrid(np.arange(x_min,x_max,h),np.arange(x_min,x_max,h))

z = clf.predict(np.c_[xx.ravel(),yy.ravel()])
z=z.reshape(xx.shape)
ax = plt.contourf(xx,yy,z,cmap='afmhot',alpha=0.3);
plt.scatter(X_std_train[:,0],X_std_train[:,0].reshape(-1,1),c=Y_train,s=80,alpha=0.9,edgecolors='g');
plt.show()

#%% Gaussian Radial Basis function (rbf) --> nonlinear polynomial
#The kernal function can be any of the followinw:
    # linear (x,x')
    # polynomial (y(x,x') + r)^d) (d is specified by keayword degree, r by coefTheta)
    # rbf (exp(-y||x-x'||2)) y is specified by keyword gamma must by greater than 0
    # sigmoid (than(y(x,x') + r)) where r is specified by coefTheta
    
#rbf is powerfull to model non-linearity

# Delta compared to Linear SVM:
    # clf = svm.SVC(kernel='rbf',C=C,gamma=n)
    
#sklearn also has the option to search for the best set of parameters using GridSearchCV:

from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV

pipeline = Pipeline([('clf',svm.SVC(kernel='rbf',C=1,gamma=0.1))])

params = {'clf__C':(0.1, 0.5, 1, 2, 5, 10, 20),'clf__gamma':(0.001,0.01, 0.1, 0.25, 0.5, 0.75, 1)}

svm_grid_rbf = GridSearchCV(pipeline, params, n_jobs=1,cv=3,verbose=1,scoring='accuracy')

svm_grid_rbf.fit(X_train,Y_train) #Fitting 3 folds for each of 49 candidates!!! total of 147 fits

svm_grid_rbf.best_score_

#%% Support Vector Regression SVR
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score

df = pd.read_csv(r'C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\Machine learning training\data\housing.data',delim_whitespace=True,header=None)
col_name = ['CRIM','ZN','INDUS','CHAS','NOX','RM','AGE','DIS','RAD','TAX','PTRATIO','B','LSTAT','MEDV']
df.columns = col_name

Y = df['MEDV'].values
X = df[['LSTAT']].values

svr = SVR(kernel='rbf',C=100,gamma='auto')
svr.fit(X,Y)

sort_idx = X.flatten().argsort()

plt.scatter(X[sort_idx],Y[sort_idx])
plt.plot(X[sort_idx],svr.predict(X[sort_idx]),color='k')
plt.show()

#Advantages SVM
    # effictive in high dimensional spaces
    # users only a subset of training points (support vectors) in the decission fuction
    # many different kernal functions can be specified for the decision function:
        #linear, Polynomial, RBF, Sigmoid, Custom
#Disadventages SVM:
    # Beware of overfitting when num_features > num_samples
    # Choice of kernal and Regularization can have a large impact on performance
    # No probability estimates
    # SCALING IS IMPORTANT
