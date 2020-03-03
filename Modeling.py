import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import mean_squared_error
import seaborn as sns
import matplotlib.pyplot as plt

# Build train and test set
train = pd.read_csv('CharlotteData.csv')
test = pd.read_csv('CharlotteData.csv')
target = train['stars']
# outliers
train['outliers'] = 0
train.loc[train['stars'] < 0, 'outliers'] = 1

del train['stars']

#print(train.head())
#print(test.head())

# Try some models
# 1. Lightgbm
train_columns = [c for c in train.columns if c not in ['outliers']]
def lightgbm(train, test, n_folds=5):
    param = {'num_leaves': 31,
         'min_data_in_leaf': 30,
         'objective':'regression',
         'max_depth': -1,
         'learning_rate': 0.01,
         "min_child_samples": 20,
         "boosting": "gbdt",
         "feature_fraction": 0.9,
         "bagging_freq": 1,
         "bagging_fraction": 0.9 ,
         "bagging_seed": 11,
         "metric": 'rmse',
         "lambda_l1": 0.1,
         "verbosity": -1,
         "nthread": 4,
         "random_state": 4590}
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=4590)
    oof = np.zeros(len(train))
    predictions = np.zeros(len(test))

    feature_importance_df = pd.DataFrame()

    for fold_, (trn_idx, val_idx) in enumerate(folds.split(train, train['outliers'].values)):
        print("fold {}".format(fold_))
        trn_data = lgb.Dataset(train.iloc[trn_idx][train_columns], label=target.iloc[trn_idx])
        val_data = lgb.Dataset(train.iloc[val_idx][train_columns], label=target.iloc[val_idx])

        num_round = 10000
        clf = lgb.train(param, trn_data, num_round, valid_sets = [trn_data, val_data], verbose_eval=100, early_stopping_rounds = 100)
        oof[val_idx] = clf.predict(train.iloc[val_idx][train_columns], num_iteration=clf.best_iteration)

        fold_importance_df = pd.DataFrame()
        fold_importance_df["Feature"] = train_columns
        fold_importance_df["importance"] = clf.feature_importance()
        fold_importance_df["fold"] = fold_ + 1
        feature_importance_df = pd.concat([feature_importance_df, fold_importance_df], axis=0)

        predictions += clf.predict(test[train_columns], num_iteration=clf.best_iteration) / folds.n_splits

    np.sqrt(mean_squared_error(oof, target))
    return feature_importance_df

feature_importance = lightgbm(train, test, n_folds=5)

# plot the features
sns.set(font_scale=1.5)
cols = (feature_importance[["Feature", "importance"]]
        .groupby("Feature")
        .mean()
        .sort_values(by="importance", ascending=False)[:20].index)

best_features = feature_importance.loc[feature_importance.Feature.isin(cols)]

plt.figure(figsize=(10,15))
sns.barplot(x="importance",
            y="Feature",
            data=best_features.sort_values(by="importance",
                                           ascending=False))
plt.title('LightGBM Top 12 Features (avg over folds)')
plt.tight_layout()
plt.savefig('CharlotteData_Feartures_importances.png')

