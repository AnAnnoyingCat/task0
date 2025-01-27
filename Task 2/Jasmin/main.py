# This serves as a template which will guide you through the implementation of this task.  It is advised
# to first read the whole template and get a sense of the overall structure of the code before trying to fill in any of the TODO gaps
# First, we import necessary libraries:
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct, RBF, Matern, RationalQuadratic, ConstantKernel
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_predict
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.impute import KNNImputer

def data_loading():
    """
    This function loads the training and test data, preprocesses it, removes the NaN values and interpolates the missing 
    data using imputation

    Parameters
    ----------
    Returns
    ----------
    X_train: matrix of floats, training input with features
    y_train: array of floats, training output with labels
    X_test: matrix of floats: dim = (100, ?), test input with features
    """
    # Load training data
    train_df = pd.read_csv("Task 2\\Data\\train.csv")
    
    print("Training data:")
    print("Shape:", train_df.shape)
    print(train_df.head(2))
    print('\n')
    
    # Load test data
    test_df = pd.read_csv("Task 2\\Data\\test.csv")

    print("Test data:")
    print(test_df.shape)
    print(test_df.head(2))

    # Dummy initialization of the X_train, X_test and y_train
    # TODO: Depending on how you deal with the non-numeric data, you may want to 
    # modify/ignore the initialization of these variables   
    """ X_train = np.zeros_like(train_df.drop(['price_CHF'],axis=1)) #not needed here, since with one-hot encoding for season we have different shapes 
    y_train = np.zeros_like(train_df['price_CHF'])
    X_test = np.zeros_like(test_df) """

    # TODO: Perform data preprocessing, imputation and extract X_train, y_train and X_test

   
    #One-hot encoding of season for training data, spring: 0100, summer: 0010, autumn: 1000, winter: 0001
    X_train_numerical = train_df.select_dtypes(exclude="object") #X_train with only numerical data
    X_train_nominal = train_df.select_dtypes(include="object") #X_train with only nominal data
    encoder = OneHotEncoder(sparse=False, handle_unknown="error")
    X_train_encoded = encoder.fit_transform(X_train_nominal)
    one_hot_features = pd.DataFrame(X_train_encoded)
    train_df = X_train_numerical.join(one_hot_features)
    """ print("TRAIN_DF W/ ONE-HOT:")
    print(train_df.head(5)) """

    X_array = train_df.values
     # replace missing data with the mean of the rest of the data
    imp_train = SimpleImputer(missing_values=np.nan, strategy='mean')
    imp_train.fit(X_array)
    X_array = imp_train.transform(X_array)
    
    X_train = np.delete(X_array, 1, axis=1) #drop price_CHF

    y_train = X_array[:, 1]

    # One-hot encoding of season for test-data, spring: 0100, summer: 0010, autumn: 1000, winter: 0001
    X_test_numerical = test_df.select_dtypes(exclude="object")
    X_test_nominal = test_df.select_dtypes(include="object")
    encoder_test = OneHotEncoder(sparse=False, handle_unknown="error")
    X_test_encoded = encoder_test.fit_transform(X_test_nominal)
    one_hot_features_test = pd.DataFrame(X_test_encoded)
    test_df = X_test_numerical.join(one_hot_features_test)
    """ print("TEST_DF W/ ONE-HOT:")
    print(test_df.head(5)) """
    X_test = test_df.values
    
    # replace missing data with the mean of the rest of the data
    imp_X_test = SimpleImputer(missing_values=np.nan, strategy='mean')
    imp_X_test.fit(X_test)
    X_test = imp_X_test.transform(X_test) 
    """ print("X_TEST IMPUTED:")
    print(X_test[:5]) """
    
    # End TODO

    assert (X_train.shape[1] == X_test.shape[1]) and (X_train.shape[0] == y_train.shape[0]) and (X_test.shape[0] == 100), "Invalid data shape"
    return X_train, y_train, X_test

def modeling_and_prediction(X_train, y_train, X_test):
    """
    This function defines the model, fits training data and then does the prediction with the test data 

    Parameters
    ----------
    X_train: matrix of floats, training input with 10 features
    y_train: array of floats, training output
    X_test: matrix of floats: dim = (100, ?), test input with 10 features

    Returns
    ----------
    y_test: array of floats: dim = (100,), predictions on test set
    """

    y_pred=np.zeros(X_test.shape[0])
    #TODO: Define the model and fit it using training data. Then, use test data to make predictions

    # Gaussian Process Regression with RBF kernel
    # Gives local score of ca. 0.65 but public score of -0.5
    X_train_train, X_train_test, y_train_train, y_train_test = train_test_split(X_train, y_train, test_size=0.2, random_state=13)
    kernel = ConstantKernel(constant_value=3) * RBF(length_scale=1, length_scale_bounds=(1e-2, 1e2))
    gp = GaussianProcessRegressor(kernel=kernel, alpha=1, n_restarts_optimizer=10)
    gp.fit(X_train_train, y_train_train)
    y_train_test_predict = gp.predict(X_train_test)
    localScore = r2_score(y_train_test, y_train_test_predict)#, squared=False)
    print("LOCAL SCORE:")
    print(localScore)
    
    # w/ cross-validation
    """ # Define the Gaussian Process Regressor model
    kernel = ConstantKernel(constant_value=3) * RBF(length_scale=1, length_scale_bounds=(1e-2, 1e2))
    gp = GaussianProcessRegressor(kernel=kernel, alpha=1, n_restarts_optimizer=10)

    # Use cross-validation to make predictions on the training data
    y_train_cv_predict = cross_val_predict(gp, X_train, y_train, cv=5)  # 5-fold cross-validation

    # Fit the model on the entire training data
    gp.fit(X_train, y_train)

    # Calculate the R^2 score using the predictions from cross-validation
    cv_score = r2_score(y_train, y_train_cv_predict)
    print("Cross-validation R^2 score:", cv_score) """

    

    # calculated r2 score from scratch to see if it differs from r2_score (it doesn't)
    """ locScoreCalc = 0.0
    zähler = 0.0
    nenner = 0.0
    mean = np.mean(y_train_test)
    N = len(y_train_test)
    for i in range (N):
        interim = y_train_test[i] - y_train_test_predict[i]
        interim = interim ** 2
        zähler += interim
    for i in range (N):
        interim = y_train_test[i] - mean
        interim = interim ** 2
        nenner += interim
    
    locScoreCalc = 1 - (zähler / nenner)
    print("SCORE CALCULATED:")
    print(locScoreCalc) """

    y_pred = gp.predict(X_test)

    #End TODO

    assert y_pred.shape == (100,), "Invalid data shape"
    return y_pred

 # exactly the same as in chris template, but for test.csv
def generate_missing_values_files():
    ############ train data ############
    
    # Import data and onehot-encode seasons
    train_df = pd.read_csv("Task 2\\Data\\train.csv")
    train_df_price_values = train_df.drop(['season'], axis=1)

    # Split off and handle the seasons
    season_column = train_df[['season']]
    seasons = ['spring', 'summer', 'autumn', 'winter']
    enc = OneHotEncoder(categories=[seasons], sparse=False)
    oneHotSeasons = enc.fit_transform(season_column)
    onehot_seasons_df = pd.DataFrame(oneHotSeasons,  columns=enc.get_feature_names_out(['season']))
    print(onehot_seasons_df)
    
     # KNN Imputer
    imp = KNNImputer(n_neighbors=4,weights='uniform')
    avg_data = imp.fit_transform(train_df_price_values)
    avg_data_df = pd.DataFrame(avg_data, columns=train_df_price_values.columns)
    full_data = pd.concat([onehot_seasons_df, avg_data_df], axis=1)
    full_data.to_csv("Task 2/Data/filled_in_data_knn.csv", index=False)

    ############## test data ##############
    
    train_df = pd.read_csv("Task 2\\Data\\test.csv")
    train_df_price_values = train_df.drop(['season'], axis=1)

    # Split off and handle the seasons
    season_column = train_df[['season']]
    seasons = ['spring', 'summer', 'autumn', 'winter']
    enc = OneHotEncoder(categories=[seasons], sparse=False)
    oneHotSeasons = enc.fit_transform(season_column)
    onehot_seasons_df = pd.DataFrame(oneHotSeasons,  columns=enc.get_feature_names_out(['season']))
    print(onehot_seasons_df)
    
     # KNN Imputer
    imp = KNNImputer(n_neighbors=4,weights='uniform')
    avg_data = imp.fit_transform(train_df_price_values)
    avg_data_df = pd.DataFrame(avg_data, columns=train_df_price_values.columns)
    full_data = pd.concat([onehot_seasons_df, avg_data_df], axis=1)
    full_data.to_csv("Task 2/Data/test_filled_in_data_knn.csv", index=False)

    """ # Univariante
    ##Avg_colwise
    imp = SimpleImputer(missing_values=np.nan, strategy='mean')
    avg_data = imp.fit_transform(train_df_price_values)
    avg_data_df1 = pd.DataFrame(avg_data, columns=train_df_price_values.columns)
    full_data = pd.concat([onehot_seasons_df,avg_data_df1], axis=1)
    full_data.to_csv("Task 2/Data/test_filled_in_data_avg_colwise.csv", index=False)

    ##Median_colwise
    imp = SimpleImputer(missing_values=np.nan, strategy='median')
    avg_data = imp.fit_transform(train_df_price_values)
    avg_data_df2 = pd.DataFrame(avg_data, columns=train_df_price_values.columns)
    full_data = pd.concat([onehot_seasons_df,avg_data_df2], axis=1)
    full_data.to_csv("Task 2/Data/test_filled_in_data_median_colwise.csv", index=False)

    ##Avg_rowwise
    # Hypothesis: prices between countries are correlated, so this might work.
    imp = SimpleImputer(missing_values=np.nan, strategy='mean')
    avg_data = imp.fit_transform(train_df_price_values.transpose())
    avg_data_df3 = pd.DataFrame(avg_data.transpose(), columns=train_df_price_values.columns)
    full_data = pd.concat([onehot_seasons_df,avg_data_df3], axis=1)
    full_data.to_csv("Task 2/Data/test_filled_in_data_avg_rowwise.csv", index=False)

    ##Median_rowwise
    imp = SimpleImputer(missing_values=np.nan, strategy='median')
    avg_data = imp.fit_transform(train_df_price_values.transpose())
    avg_data_df4 = pd.DataFrame(avg_data.transpose(), columns=train_df_price_values.columns)
    full_data = pd.concat([onehot_seasons_df,avg_data_df4], axis=1)
    full_data.to_csv("Task 2/Data/test_filled_in_data_median_rowwise.csv", index=False)

    # Multivariante
    ## Iterative Imputer

    imp = IterativeImputer(max_iter=126, random_state=13)
    avg_data = imp.fit_transform(train_df_price_values)
    avg_data_df = pd.DataFrame(avg_data, columns=train_df_price_values.columns)
    full_data = pd.concat([onehot_seasons_df, avg_data_df], axis=1)
    full_data.to_csv("Task 2/Data/test_filled_in_data_iterimp.csv", index=False) """




def defineXY(file_train, file_test):
    df_train = pd.read_csv("{0}".format(file_train))
    X_train = df_train.drop(['price_CHF'], axis=1)
    y = df_train['price_CHF']
    df_test = pd.read_csv("{0}".format(file_test))
    return X_train.values, y.values, df_test.values

# Main function. You don't have to change this
if __name__ == "__main__":
    #generate_missing_values_files()
    # Data loading
    #X_train, y_train, X_test = data_loading()
    # The function retrieving optimal LR parameters
    
    # J - use chris csv file for different kind of data preprocessing
    """ y_pred=modeling_and_prediction(X_train, y_train, X_test) # my own preprocessing
    # Save results in the required format
    dt = pd.DataFrame(y_pred) 
    dt.columns = ['price_CHF']
    dt.to_csv('Task 2\\Jasmin\\results.csv', index=False)
    print("\nResults file successfully generated!")
    
    X_train, y_train, X_test = defineXY("Task 2\\Data\\filled_in_data_avg_colwise.csv", "Task 2\\Data\\test_filled_in_data_avg_colwise.csv")
    y_pred=modeling_and_prediction(X_train, y_train, X_test) # avg colwise
    # Save results in the required format
    dt = pd.DataFrame(y_pred) 
    dt.columns = ['price_CHF']
    dt.to_csv('Task 2\\Jasmin\\results_avg_colwise.csv', index=False)
    print("\nResults file successfully generated!")
    
    X_train, y_train, X_test = defineXY("Task 2\\Data\\filled_in_data_avg_rowwise.csv", "Task 2\\Data\\test_filled_in_data_avg_rowwise.csv")
    y_pred=modeling_and_prediction(X_train, y_train, X_test) # avg rowwise
    # Save results in the required format
    dt = pd.DataFrame(y_pred) 
    dt.columns = ['price_CHF']
    dt.to_csv('Task 2\\Jasmin\\results_avg_rowwise.csv', index=False)
    print("\nResults file successfully generated!")
    
    X_train, y_train, X_test = defineXY("Task 2\\Data\\filled_in_data_median_colwise.csv", "Task 2\\Data\\test_filled_in_data_median_colwise.csv")
    y_pred=modeling_and_prediction(X_train, y_train, X_test) # median colwise
    # Save results in the required format
    dt = pd.DataFrame(y_pred) 
    dt.columns = ['price_CHF']
    dt.to_csv('Task 2\\Jasmin\\results_median_colwise.csv', index=False)
    print("\nResults file successfully generated!")
    
    X_train, y_train, X_test = defineXY("Task 2\\Data\\filled_in_data_median_rowwise.csv", "Task 2\\Data\\test_filled_in_data_median_rowwise.csv")
    y_pred=modeling_and_prediction(X_train, y_train, X_test) # median rowwise
    # Save results in the required format
    dt = pd.DataFrame(y_pred) 
    dt.columns = ['price_CHF']
    dt.to_csv('Task 2\\Jasmin\\results_median_rowwise.csv', index=False)
    print("\nResults file successfully generated!")
    
    X_train, y_train, X_test = defineXY("Task 2\\Data\\filled_in_data_iterimp.csv", "Task 2\\Data\\test_filled_in_data_iterimp.csv")
    y_pred=modeling_and_prediction(X_train, y_train, X_test) # iterative imputer
    # Save results in the required format
    dt = pd.DataFrame(y_pred) 
    dt.columns = ['price_CHF']
    dt.to_csv('Task 2\\Jasmin\\results_iterimp.csv', index=False)
    print("\nResults file successfully generated!")
     """
    generate_missing_values_files()
    X_train, y_train, X_test = defineXY("Task 2\\Data\\filled_in_data_knn.csv", "Task 2\\Data\\test_filled_in_data_knn.csv")
    y_pred=modeling_and_prediction(X_train, y_train, X_test) # knn imputer
    # Save results in the required format
    dt = pd.DataFrame(y_pred) 
    dt.columns = ['price_CHF']
    dt.to_csv('Task 2\\Jasmin\\results_knn.csv', index=False)
    print("\nResults file successfully generated!")
    
    
    
    