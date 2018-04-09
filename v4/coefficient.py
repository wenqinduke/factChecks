import numpy as np

x = np.array([4.5, 5.5, 8.5 , 7.0, 7.5, 5.5, 6.5, 6.5, 5])
y = np.array([4.5, 4.5, 6.07, 7.0, 7.5, 5.5, 5 , 4.32, 5])

A = np.vstack([x, np.ones(len(x))]).T
m, c = np.linalg.lstsq(A, y)[0]
print (m,c)
