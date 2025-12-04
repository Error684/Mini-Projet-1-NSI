import pandas

df=pandas.read_csv("titanic_train.csv")
df_valid = pandas.read_csv("titanic_validation.csv")

k = 9

def dist(a1, a2, b1, b2, c1, c2):
    return ((a2-a1)**2 + (b2-b1)**2 + (c2-c1)**2)**0.5

def Convert(df):
    for i in range(len(df)):
        if df.loc[i, "Sex"] == "female":
            df.loc[i, "Sex"]= 0
        else:
            df.loc[i,"Sex"]=1
            
Convert(df_valid)
Convert(df)
            
def Test():
    juste = 0
    for i in range(len(df_valid)):
        if df_valid.iloc[i, 2] == KNN(df.iloc[i, 8], df.iloc[5], df.iloc[i, 3], k):
            juste = juste + 1
    return juste / len(df_valid) * 100
            
def KNN(a1, b1, c1, k):
    
    df["Distance"] = dist(a1, df["Parch"], b1 ,df["Sex"] , c1, df["Pclass"] )
    df_Sorted = df.sort_values(by = "Distance")
    
    Alive = 0
    Dead = 0
    
    for i in range (k):
        if df_Sorted.iloc[i,2] == 1 :
            Alive = Alive + 1
        elif df_Sorted.iloc[i,2] == 0 :
            Dead = Dead + 1
            
    if Alive > Dead:
        return 1
    elif Dead > Alive :
        return 0
    
print(Test())