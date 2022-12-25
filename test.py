import pandas as pd
import numpy as np
from sklearn.metrics import precision_score
import hyperopt
from hyperopt import fmin, hp, tpe, STATUS_OK

'''
Set your function's parameters
'''
params = {}
params["N"] = [0,10,1] # Parameter "N" in the range 0 to 10 (min step = 1)
params["margin"] = [0,10,0.1] # Parameter "margin" in the range 0 to 10 (min step 0.1)
'''
Set your class. E.g. True if next 5 candles close price drops below 10%,
otherwise False.
'''
gain = -0.1
next_candles = 5

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
  df["real"] = df.close.rolling(next_candles).min().shift(-next_candles)
  df["class"] = df["real"] < df["thresh"] if gain < 0 else df["real"] > df["thresh"]
  score = int(precision_score(df["class"], predictions)*100) if sum(predictions) > 0 else 0
  return -score

if __name__ == "__main__":
  scores, space = [], []
  for key in params:
    space.append(hp.quniform(key, params[key][0], params[key][1], params[key][2]))
  for i, fName in enumerate(["BBIG", "PIXY", "RELI", "SXTC", "WEI"]):
    df = pd.read_csv(filepath_or_buffer="https://raw.githubusercontent.com/Pisciotta/test_csv/main/"+fName+".csv")
    fn = lambda x: loss(df, function(df,x))
    min_params = fmin(fn=fn, space=space, algo=tpe.suggest, max_evals=500)
    scores.append(fn(min_params.values()))
  print("Scores", scores)
  print(["PASS" if score < -90 else "FAIL" for score in scores])
