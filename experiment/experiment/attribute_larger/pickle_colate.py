
import sys
import pickle
from tqdm import tqdm

argv = sys.argv[2:]
out_file = sys.argv[1]
data = []
print("loading")
for arg in tqdm(argv):
    with open(arg,"rb") as f:
        data += pickle.load(f)
print("outputting")
with open(out_file,'wb') as f:
    pickle.dump(data,f)
print("done")

