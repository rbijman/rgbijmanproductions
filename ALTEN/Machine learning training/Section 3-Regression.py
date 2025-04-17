# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 11:47:08 2025

@author: rbijman
"""
import numpy as np
import pandas as pd


df = pd.read_csv(r'Documents\GitHub\rgbijmanproductions\ALTEN\Machine learning training\data\housing.data',delim_whitespace=True,header=None)
col_name = ['CRIM','ZN','INDUS','CHAS','NOX','RM','AGE','DIS','RAD','TAX','PTRATIO','B','LSTAT','MEDV']
df.columns = col_name

df.head()

#%% Exploratory Data Analysis (EDA)
import seaborn as sns
import matplotlib.pyplot as plt
df.describe()

col_study = ['CRIM','ZN','INDUS','NOX','RM']
sns.pairplot(df[col_study],height=1.5)
plt.show()

df.corr().round(3)

col_interest = ['CRIM','ZN','INDUS','CHAS',"MEDV"]
sns.heatmap(df[col_interest].corr(),annot=True)
plt.show()

#%% Linear Regression with Scikit-Learn
df.head()

X = df['RM'].values.reshape(-1,1) #-1 is the unknown dimension
y = df['MEDV'].values

from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X,y)
print(model.coef_,model.intercept_)

sns.regplot(x=X,y=y)
plt.show()

#prediction
model.predict([np.array([5]).reshape(1,-1)])

#%% Five steps Machine Learning Process
#1. Choose a class of model by importing the appropirate estimator class from Scikit
#2. Choose a model hyperparameter (if needed) and instatinate the class with desired values
#3. Arange the feature and Target matrix/vectors
#4. Fit the data by calling the fit method
#5. Aply the model to new data by using the predict method
ml2 = LinearRegression()
X = df['LSTAT'].values.reshape(-1,1)
Y = df['MEDV'].values
ml2.fit(X,Y)
sns.regplot(x=X,y=Y)
plt.show()

ml2.predict(np.array([15]).reshape(1,-1))

#%% Robust Regression - RANdom SAmple Consensus (RANSAC) Algorithm
#1. Select min_samples random samples from the original data and check whether the set of data is valid (see is_data_valid)
#2. Fit a model to the reandom subset (base_estimator.fit) and check whehter the estimated model is valid (See is_model_valid)
#3. Classify all data as inliers or outliers by calculaten the residuals to the estmated model (base_estimator.predict(X) - y) - all data samples with absolute residuals smaller than the residual_threshold are considered as inliers
#4. Save fitte model as best model if number of inliers samples is maximal. In case the current estimated model has the same number of inliers, it is only considered as the best model if it has better score

X = df['LSTAT'].values.reshape(-1,1)
Y = df['MEDV'].values

from sklearn.linear_model import RANSACRegressor

ransac = RANSACRegressor()
ransac.fit(X,Y)

inlier_mask= ransac.inlier_mask_ 
outlier_mask = np.logical_not(inlier_mask)

line_X = np.arange(0,40,1)
line_y_ransac = ransac.predict(line_X.reshape(-1,1))

line_y_ml2 = ml2.predict(line_X.reshape(-1,1))

plt.scatter(X[inlier_mask],Y[inlier_mask])
plt.scatter(X[outlier_mask],Y[outlier_mask],color = 'red',marker='s')
plt.plot(line_X,line_y_ransac) #Robust regression result
plt.plot(line_X,line_y_ml2) # Non-Robust regression result
plt.show()

#%% Evaluate Regression model performance
from sklearn.model_selection import train_test_split

X = df.iloc[:,:-1].values
Y = df['MEDV'].values

X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.2, random_state=0)

lr = LinearRegression()
lr.fit(X_train,Y_train)
y_train_pred = lr.predict(X_train)
y_test_pred = lr.predict(X_test)

#Method1 Residual analysis, should be random!
plt.scatter(y_train_pred,y_train_pred-Y_train,c='blue',marker='o',label='Training data')
plt.scatter(y_test_pred,y_test_pred-Y_test,c='orange',marker='*',label='Test data')
plt.xlabel('Predicted values')
plt.ylabel('Residuals')
plt.hlines(y=0, xmin=-10, xmax=50, lw=2,color='k')
plt.xlim([-10,50])
plt.show()

#Method2 Mean Squared Error , the lower the better
from sklearn.metrics import mean_squared_error

print(mean_squared_error(Y_train, y_train_pred))
print(mean_squared_error(Y_test, y_test_pred))

#Method3 R2, the higher the better (1- Sum of Squared Errors/Sum of squares)
from sklearn.metrics import r2_score

print(r2_score(Y_train, y_train_pred))
print(r2_score(Y_test, y_test_pred))


#%% Multiple regression
df.shape

x=df.iloc[:,:-1]
y = df.iloc[:,-1].values

#Statsmodels
import statsmodels.api as sm

X_constant = sm.add_constant(x) #add intercept/bias IMPORTANT OTHERWISE MODEL IS WITHOUT INTERCEPT
pd.DataFrame(X_constant)
model = sm.OLS(y,X_constant[['const',"CRIM","ZN","CHAS","NOX"]]) #Ordanary leas squares model
lr = model.fit()
lr.summary() #Look at Adjusted R2 for model quality, Cond. No. the higher the more chance for multicolinearity

#Multicolinearity
#Check for cross corelation
corr_matrix = x.corr()
sns.heatmap(corr_matrix, annot=True,cmap='YlGnBu')
plt.show()
#Check eigenvalues - small values represent presence of colinearity
eigenvalues,eigenvectors = np.linalg.eig(corr_matrix)
pd.Series(eigenvalues).sort_values()
np.abs(pd.Series(eigenvectors[:,8])).sort_values(ascending=False)

print(x.columns[2],x.columns[8],x.columns[9])

#%% Regularized Regression

#Ridge Regression (L2 penalize method)
# Can't zero out coefficients; You either end up including all the coefficient or none of them.

#LASSO (Least absolute Shrinkage and Selection Operator) (L1 penalize method)
# Does both parameter shrinkage and variable selection automatically

#Elastic Net (L1,L2 penalize mothod)
# if some of your coverates are highly correlated, you may want to look ath the Elastic net instead of Lasso

#%% Polynomial Regression - non linear relationships

#example y = X^3 + 100 + e

np.random.seed(42)
n_samples = 100
X = np.linspace(0,20,n_samples)
rng = np.random.randn(n_samples) * 100 #NOISE!! --> e

Y = X**3 + rng + 100


import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

polyreg = PolynomialFeatures(degree=2)
X_poly = polyreg.fit_transform(X.reshape(-1,1))

lr1 = LinearRegression()
lr2 = LinearRegression()

lr1.fit(X.reshape(-1,1),Y)
lr2.fit(X_poly,Y)

model1_pred = lr1.predict(X.reshape(-1,1))
model2_pred = lr2.predict(X_poly)

plt.scatter(X,Y)
plt.plot(X,model1_pred)
plt.plot(X,model2_pred)
plt.show()
print(sklearn.metrics.r2_score(Y,model1_pred),sklearn.metrics.r2_score(Y,model2_pred) )


#%% Dealing with Non-linear Relationships
#Decission Tree
from sklearn.tree import DecisionTreeRegressor

X = df[['LSTAT']].values
Y = df[['MEDV']].values

tree = DecisionTreeRegressor(max_depth=3)

tree.fit(X,Y)

sort_idx = X.flatten().argsort() #sort the x values from lowest to largest, needed for decission tree

plt.scatter(X[sort_idx],y[sort_idx])
plt.plot(X[sort_idx],tree.predict(X[sort_idx]),color='k')
plt.xlabel('LSTAT')
plt.ylabel('MEDV')
plt.show()

#Random Forest

#AdaBoost

#%% Feature importance
# AdaBoost and Random Forrest have a feature_imporatence_ method

#%% Exercise on Feature importance
X = df.iloc[:,:-1]
Y = df.iloc[:,-1].values

from sklearn.tree import DecisionTreeRegressor

X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.3, random_state=42)

tree = DecisionTreeRegressor(max_depth=3)

tree.fit(X_train,Y_train)

Y_pred_train = tree.predict(X_train)
Y_pred_test = tree.predict(X_test)

from sklearn.metrics import mean_squared_error, r2_score

print(mean_squared_error(Y_train, Y_pred_train),mean_squared_error(Y_test, Y_pred_test))
print(r2_score(Y_train, Y_pred_train),r2_score(Y_test, Y_pred_test))

pd.DataFrame(tree.feature_importances_,df.columns[:-1],columns=['Feature']).sort_values('Feature').plot(kind='bar')
plt.show()

#%% Data pre-processing
#Gradient decent method as a measure - not for this course

#Assumptions:
# implicit/explicit assumption of machine learning algorithms: The features follow a normal distribution
# Most method are based on linear assumptions
# Most machine learning requires the data to be standard normally distributed. Gaussian with zero mean and unit variance

# In practice we often ignore the shape of the distribution and just transform the data to center it by removing the mean value of each feature, than scale it by dividing non-constant features by their standard deviation

#Standardization Z-score

from sklearn import preprocessing

X_train = np.array([[1.,-1.,2.],[2.,0.,0.],[0.,1.,-1.]])
X_train.mean(axis=0)

X_scaled = preprocessing.scale(X_train)
X_scaled
X_scaled.mean(axis=0) #all 0
X_scaled.std(axis=0) #all 1

# Important!!! Only preprocess the trainining data, not the test dat. The test data should be multiplied with the scaler. Otherwise risk of leaking information from test data into training data

# In depth what happens in .scale function
scaler = preprocessing.StandardScaler().fit(X_train)
scaler.mean_
scaler.scale_

scaler.transform(X_train)

X_test = [[-1.,1.,0.]]
scaler.transform(X_test) #apply the scaler to test data

#MinMaxScaler (max[1]-min[0])/(X.max(axis=0)-X.min(axis=0))
# Scaling features to lie between a given minimum and maximum value, often between zero and one, or so that the maximum absolute value of each feature is scaled to unit-size
# The motivation to use this scaling include robustness to very small standard deviations of features and preserving zero entries in sparse data

min_max_scaler = preprocessing.MinMaxScaler() #default [0,1]

X_train_minmax = min_max_scaler.fit_transform(X_train) #combines fit and transform in one call
X_train_minmax
X_test = np.array([[-3.,-1.,0.],[2.,1.5,4.]])
X_test_minmax = min_max_scaler.transform(X_test)
X_test_minmax #not perse in the range of [0,1]

#MaxabsScaler [-1,1] range
# works very similar as MinMaxScalar, but scales in a way that the training data lies within the range [-1,-1] by dividing through the largest maxmimum value in each feature. It is meant for data that is already centered at zero or sparse data

max_abs_scaler = preprocessing.MaxAbsScaler()
X_train_maxabs = max_abs_scaler.fit_transform(X_train)
X_train_maxabs

#Scaling sparse data
# Centering sparse data would destroy the sparseness structure in the data, and thus rarely is a sensible thing to do. It can be wise to do if different features are on different scales

#Scaling vs Whitening
# It is sometimes not enough to center the features independently, since a downstream model can further make some assumption on the linear independence of the features.
# To adress this issue you can use sklearn.decomposition. PCA or sklearn.decomposition.RandomPCA with whiten=True to further remove the linear correaltion accros features

#Normalization
#L1 Least absolute deviation - ensures the sum of absolute value is 1 in each row
#L2 least squares - ensures the sum of squares is 1
X_normalized = preprocessing.normalize(X_train,norm="l1")
X_normalized

#Binarization
# Setting a threshold to decide if data is 0 or 1
X_binarized = preprocessing.Binarizer(threshold=0).fit_transform(X_train)
X_binarized

#LabelEncoder
source = ['australia','singapore','new_zealand','hong-kong']
label_enc = preprocessing.LabelEncoder()
label_enc.fit_transform(source)
testdata = ['hong-kong','singapore','australia','new_zealand']
result = label_enc.transform(testdata)
result

#OneHotEncoder (check documentation)

#%% Variance-Bias Trade Off
# Variance tells how sensitive an estimatore  is to varying training sets
# Bias tells the average error for different training sets
# Noise is a property of the data
# Reducing the one usually leads to increase of the other

#Validation curve
# Split data in training, validation and testing data (80%/10%/10%)
# Validation is for identification of over- and under-fitting
# see documentation

#%% Learning curve
# Shows the validation and training score of an estimator for varying number of training samples


#%% Cross validation

# Holdout Method - split dataset in training, validation and test
# K-1 fold method = Split dataset in training and test and split the training in k times in k sets of which you use 9 for training and 1 for validation, while changing the validation set every time. Average the model performance
# stratified k-fold cross-validation uses stratified samples following the distribution of the original set (usually used for binary classes)

#Cross validation illustration

from sklearn.model_selection import train_test_split
from sklearn import svm

X_train, X_test, Y_train, Y_test = train_test_split(df.iloc[:,:-1],df.iloc[:,-1],test_size=0.4,random_state=0)

#1 time
regression = svm.SVR(kernel='linear',C=1).fit(X_train,Y_train)
regression.score(X_test,Y_test)

#Cross-validation
from sklearn.model_selection import cross_val_score

regression = svm.SVR(kernel='linear',C=1)
scores = cross_val_score(regression, df.iloc[:,:-1],df.MEDV,cv=5)
print(scores.mean(), scores.std() **2)

#Using pipelines we can do all this in one line:
    
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
pipe_svm = make_pipeline(StandardScaler(), #preprocess
                         PCA(n_components=2), #PCA
                         svm.SVR(kernel='linear',C=1) #Regressor initiating
                         )
pipe_svm.fit(X_train,Y_train) # fitting
x_pred = pipe_svm.predict(X_test)
print('Test accuracy: %.3f' % pipe_svm.score(X_test,Y_test))

from sklearn.model_selection import cross_val_score
scores = cross_val_score(estimator=pipe_svm,
                         X=X_train, 
                         y=Y_train, 
                         cv=10,
                         n_jobs=1)
print('CV accuracy scores: %s' % scores)
print('CV accuracy: %.3f +/- %.3f' % (np.mean(scores),np.std(scores)**2))