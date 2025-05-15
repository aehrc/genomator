import glob
import os
files = glob.glob("*.pickle")
import pickle
from tqdm import tqdm
for f in tqdm(files):
    if 'mark' not in f:
        continue
    #print("LOADING")
    print(f)
    with open(f,'rb') as ff:
        Z = pickle.load(ff)
    assert len(Z)==2500
    Z = Z[:120]

    #print("CHECKING")
    new_file = f"../attribute/{f}"
    if os.path.isfile(new_file):
        with open(new_file,'rb') as ff:
            ZZ = pickle.load(ff)
            if len(ZZ) != 2500:
                continue

    print("DUMPING")
    print(new_file)
    with open(new_file,'wb') as ff:
        pickle.dump(Z,ff)
