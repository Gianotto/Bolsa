import numpy as np
import time, sys

arr = np.array([[1, 2, 3], [4, 5, 6]])

a = np.array(42)
b = np.array([1, 2, 3, 4, 5])
c = np.array([[1, 2, 3], [4, 5, 6]])
d = np.array([[[1, 2, 3], [4, 5, 6]], [[1, 2, 3], [4, 5, 6]]])

print(a.ndim)
print(b.ndim)
print(c.ndim)
print(d.ndim)

print (d)


x = np.cos(np.pi/2)

print(x)


startTime = time.time()
while True:
    elapsedTime = time.time() - startTime
    print('.', end="")
    sys.stdout = "..."
    time.sleep(0.5)
    if elapsedTime >= 10:
        print('')
        break