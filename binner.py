import pandas as pd
df = pd.read_csv("acute-inflammations.csv")
df['V1'] = pd.cut(df['V1'], bins=3)
# df['Glucose'] = pd.cut(df['Glucose'], bins=3)
# df['BloodPressure'] = pd.cut(df['BloodPressure'], bins=3)
# df['SkinThickness'] = pd.cut(df['SkinThickness'], bins=3)
# df['Insulin'] = pd.cut(df['Insulin'], bins=3)
# df['BMI'] = pd.cut(df['BMI'], bins=3)
# df['DiabetesPedigreeFunction'] = pd.cut(df['DiabetesPedigreeFunction'], bins=3)
# df['Age'] = pd.cut(df['Age'], bins=3)
# df['oldpeak'] = pd.cut(df['oldpeak'], bins=3)
# df['slope'] = pd.cut(df['slope'], bins=3)
# df['ca'] = pd.cut(df['ca'], bins=3)
# df['thal'] = pd.cut(df['thal'], bins=3)

print(df)

# z = df.drop(columns=)
# print(z)
df.to_csv('binned-inflammations.csv')
