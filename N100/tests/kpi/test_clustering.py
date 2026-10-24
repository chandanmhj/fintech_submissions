import numpy as np
from sklearn.preprocessing import StandardScaler
from src.analytics.clustering import FEATURES

def test_five_required_features(): assert len(FEATURES)==5
def test_scaling_centres_features():
 x=StandardScaler().fit_transform(np.array([[1.,2.],[3.,4.],[5.,6.]])); assert np.allclose(x.mean(0),0,atol=1e-8)
