# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 12:36:14 2025

@author: rbijman
"""

#CART Classification and Regression Tree

# gini is the measure of how much further splitting is possible, gini=0 means no split possible 
# Supervised learning
# Works for both classification and regression
# Foundation of Random Forrest
# Attractive because of interretability

#Decission tree works by:
    # split based on inpurity criteria
    # stopping criteria
    
# Adventages:
    # simple to undertand and interpret, can be visualized
    # requires little data preperation
    # able to handle both numerical and categorical data
    # possible to validate a model using statistical tests
    # performs well even if its assumptions are somewhat violated by the true model from which the data was generated
    
#disadventages:
    # overfitting. Mechanisms susc as pruning, setting the minumum number of samples required at a leaf node or setting a maximum depth of the tree are necessary to avoid this problem
    # decission trees can be unstable. Mitigant: use decission treses within an ensemble
    # cannot guareantee to return the globally optimal decision tree: Mittigant: training multipl etrees in an ensamble learner
    # Decission tree learners create biased trees ifs ome classed dominate. Recommendation: Balance the dataset prior to fitting
    
from sklearn import tree

X = [[0,0] , [1,2]]
Y = [0,1]

clf = tree.DecisionTreeClassifier()

clf.fit(X,Y)

clf.predict([[2,2]])

clf.predict_proba([[2,2]])

clf.predict_proba([[0.4,1.2]])

#DecissionTreeClassifier is capbable of both binary and multiclass classification

from sklearn.datasets import load_iris
from sklearn import tree

iris = load_iris()

X = iris.data[:,2:]
Y = iris.target

clf = tree.DecisionTreeClassifier(random_state=42)

clf.fit(X,Y)


#need to install graphviz

from sklearn.tree import export_graphviz
import graphviz

dot_data = export_graphviz(clf,out_file='tree.dot',feature_names=iris.feature_names[2:],class_names = iris.target_names, rounded=True,filled=True)

graph = graphviz.Source(dot_data)

graph.view #DOES NOT WORK


#%% Visualizig Decision Boundary

import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

df = sns.load_dataset('iris')
df.head

col = ['petal_length','petal_width']
X = df.loc[:, col]

species_to_num = {'setosa':0,'versicolor':1,'virginica':2}
df['tmp'] = df['species'].map(species_to_num)

Y = df['tmp']

clf = tree.DecisionTreeClassifier()
clf = clf.fit(X,Y)

Xv = X.values.reshape(-1,1)
h=0.02
x_min, x_max = Xv.min(), Xv.max() +1
y_min, y_max = Y.min(), Y.max() + 1

xx, yy = np.meshgrid(np.arange(x_min, x_max, h),np.arange(y_min,y_max,h))

z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
z=z.reshape(xx.shape)
ax = plt.contour(xx,yy,z, cmap = 'afmhot',alpha=0.3);
plt.scatter(X.values[:,0],X.values[:,1],c=Y,s=80,alpha=0.9,edgecolors='g')
plt.show()

# gini impurity measure for possibility to further split or not 

#%% Decission Tree Regression

from sklearn import tree

X = [[0,0],[3,3]]
Y = [0.75, 3]

tree_reg = tree.DecisionTreeRegressor(random_state=42)

tree_reg.fit(X,Y)

tree_reg.predict([[1.5,1.5]])

rng = np.random.RandomState(1)
X = np.sort(5 * rng.rand(80,1),axis=0)
Y = np.sin(X).ravel()

Y[::5] += 3 * (0.5 - rng.rand(16))

regr_1 = tree.DecisionTreeRegressor(max_depth=2)
regr_2 = tree.DecisionTreeRegressor(max_depth=5,min_samples_leaf=10) #regularisation min_samples_leaf, use GridSearchCV with params {'min_samples_leaf':list(range(5,20))} to check what is the optimal minimum sample leaf
regr_1.fit(X,Y)
regr_2.fit(X,Y)

X_test = np.arange(0.0,5.0,0.01)[:,np.newaxis]
Y_1 = regr_1.predict(X_test)
Y_2 = regr_2.predict(X_test)

plt.scatter(X,Y,s=20,edgecolors='k',c='darkorange',label='data')
plt.plot(X_test,Y_1,color='cornflowerblue',label='max_depth=2',linewidth=2)
plt.plot(X_test,Y_2,color='yellowgreen',label='max_depth=5',linewidth=2)
plt.legend()
plt.show()

# Discision trees tend to overfit

#%% Project HR
