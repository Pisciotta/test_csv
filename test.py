import pandas as pd
from sklearn.metrics import precision_score

def function(df):
        '''
            Describe your function's logic here.
        '''
        params = dict()
        params["N"] = 20
        params["margin"] = 0.9
        # Initializing predictions as a boolean series:
        predictions = pd.Series(data=True, index=df.index)
        
        # Implement your logic after this line:
        closeVolume = df[["close", "volume"]].values
        for i, (price, volume) in enumerate(closeVolume):
          if i < params["N"]:
            continue

          recentValues = closeVolume[i-params["N"]:i,:]
          maxVolume = max(recentValues[:,1])
          comparePrice = min([pastPrice for pastPrice, pastVolume in recentValues if pastVolume >= params["margin"]*maxVolume])

          if price <= comparePrice:
            predictions.iloc[i] = True
        
        return predictions
        
if __name__ == "__main__":
  gain = -0.1
  next_candles = 5
  scores = []
  for i, fName in enumerate(["BBIG", "PIXY", "RELI", "SXTC", "WEI"]):
    df = pd.read_csv(filepath_or_buffer="https://raw.githubusercontent.com/Pisciotta/test_csv/main/"+fName+".csv")
    predictions = function(df)
    df["thresh"] = df.close*(1+gain)
    df["real"] = df.close.rolling(next_candles).min().shift(-next_candles)
    if gain < 0:
      df["class"] = df["real"] < df["thresh"]
    else:
      df["class"] = df["real"] > df["thresh"]
    score = int(precision_score(df["class"], predictions)*100) if sum(predictions) > 0 else 0
    print("Score",i,":", score,"%")
    scores.append(score)
  print("---------\nMean Value:", sum(scores)/len(scores), "%")
