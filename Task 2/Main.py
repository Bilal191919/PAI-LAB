import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

train_df = pd.read_csv('train.csv')
test_df = pd.read_csv('test.csv')

def process_data(df):
    data = df.copy()
    
    def split_cabin(x):
        if pd.isna(x):
            return pd.Series([np.nan, np.nan, np.nan])
        else:
            try:
                parts = x.split('/')
                return pd.Series([parts[0], parts[1], parts[2]])
            except:
                return pd.Series([np.nan, np.nan, np.nan])

    data[['Deck', 'Num', 'Side']] = data['Cabin'].apply(split_cabin)
    data = data.drop(['Name', 'Cabin'], axis=1)
    
    return data

train_clean = process_data(train_df)
test_clean = process_data(test_df)

print("--- Starting Exploratory Data Analysis (EDA) ---")

print("\nData Info:")
print(train_clean.info())

print("\nMissing Values Count:")
print(train_clean.isnull().sum())

plt.figure(figsize=(6, 4))
sns.countplot(x='Transported', data=train_clean)
plt.title('Distribution of Target Variable (Transported)')
plt.show()

plt.figure(figsize=(10, 6))
sns.histplot(data=train_clean, x='Age', hue='Transported', kde=True, element="step")
plt.title('Age Distribution by Transported Status')
plt.show()

numeric_df = train_clean.select_dtypes(include=[np.number])
plt.figure(figsize=(10, 8))
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Heatmap')
plt.show()

print("--- EDA Finished. Proceeding to Model Training ---")

X = train_clean.drop(['PassengerId', 'Transported'], axis=1)
X = train_clean.drop(['PassengerId', 'Transported'], axis=1)
y = train_clean['Transported'].astype(int)

X_test = test_clean.drop(['PassengerId'], axis=1)
test_ids = test_clean['PassengerId']

X['Num'] = pd.to_numeric(X['Num'])
X_test['Num'] = pd.to_numeric(X_test['Num'])

numerical_cols = ['Age', 'RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck', 'Num']
categorical_cols = ['HomePlanet', 'CryoSleep', 'Destination', 'VIP', 'Deck', 'Side']

num_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

cat_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('encoder', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', num_transformer, numerical_cols),
        ('cat', cat_transformer, categorical_cols)
    ])

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=200, 
                                          min_samples_split=5, 
                                          min_samples_leaf=2, 
                                          random_state=42))
])

print("Training Model on Full Data...")
model.fit(X, y)

print("Predicting on Test Data...")
predictions = model.predict(X_test)

predictions_bool = predictions.astype(bool)

output = pd.DataFrame({
    'PassengerId': test_ids,
    'Transported': predictions_bool
})

output.to_csv('submission.csv', index=False)
print("Success! 'submission.csv' file has been saved.")