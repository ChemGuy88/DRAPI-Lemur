from pathlib import Path
from drapi.drapi import successiveParents

fp = Path(__file__)
print(fp)

fp1, n1 = successiveParents(fp, -1)
print(fp1, n1)

fp2, n2 = successiveParents(fp, 0)
print(fp2, n2)

fp3, n3 = successiveParents(fp, 1)
print(fp3, n3)

fp4, n4 = successiveParents(fp, 2)
print(fp4, n4)

fp5, n5 = successiveParents(fp, 5)
print(fp5, n5)
