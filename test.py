import pandas as pd
import numpy as np
from sklearn.metrics import precision_score
from hyperopt import fmin, hp, tpe

'''
Set your function's parameters
'''
params = {}
params["N"] = [0,15,1] # Parameter "N" in the range 0 to 10 (min step = 1)
params["margin"] = [0,5,0.1] # Parameter "margin" in the range 0 to 5 (min step 0.1)
'''
Set your class. E.g. True if next 7 candles close price drops below 10%,
otherwise False.
'''
gain = -0.1
next_candles = 7

def function(df, p):
        '''
            Describe your function's logic here.
        '''
        # Get parameters and cast to correct types (if not float)
        N,margin = p
        N = int(N)

        # Initializing predictions as a boolean series:
        predictions = pd.Series(data=False, index=df.index)
        
        # Implement your logic after this line:
        mean = df.close.rolling(N).mean()
        std = df.close.rolling(N).std()
        predictions = df.close > mean+margin*std

        return predictions


"""
NOT CHANGE AFTER THIS LINE
"""
def loss(df, predictions):
  df["thresh"] = df.close*(1+gain)
  if gain < 0:
    df["real"] = df.close.rolling(next_candles).min().shift(-next_candles)
    df["class"] = df["real"] < df["thresh"]
  else:
    df["real"] = df.close.rolling(next_candles).max().shift(-next_candles)
    df["class"] = df["real"] > df["thresh"]
  score = int(precision_score(df["class"], predictions)*100) if sum(predictions) > 0 else 0
  if score < 100:
    return -score
  else:
    return -score-sum(predictions)

if __name__ == "__main__":
  scores, space, trues = [], [], []
  for key in params:
    space.append(hp.quniform(key, params[key][0], params[key][1], params[key][2]))
  for i, fName in enumerate(["RLX","GTHX","ASTL","NILE","BABA","FINV","WEI"]):
    df = pd.read_csv(filepath_or_buffer="https://raw.githubusercontent.com/Pisciotta/test_csv/main/"+fName+".csv")
    df = df.iloc[::-1]
    fn = lambda x: loss(df, function(df,x))
    min_params = fmin(fn=fn, space=space, algo=tpe.suggest, max_evals=500)
    predictions = function(df,min_params.values())
    scores.append(loss(df, predictions))
    trues.append(sum(predictions))
  print("Scores", scores)
  print("Nr. of TRUE", trues)
  print("OK" if sum([1 if score < -90 else 0 for score in scores]) == len(scores) else "FAIL")
