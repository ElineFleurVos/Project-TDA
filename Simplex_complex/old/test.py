import math

import gudhi

c=gudhi.SimplexTree()
c.insert([1])
c.insert([2])
c.insert([3])
c.insert([4])
c.insert([5])

c.insert([1,2])
c.insert([1,3])
c.insert([1,4])
c.insert([2,3])
c.insert([2,4])
c.insert([2,5])
c.insert([3,4])
c.insert([3,5])
c.insert([4,5])



c.compute_persistence()
print(c.betti_numbers())

