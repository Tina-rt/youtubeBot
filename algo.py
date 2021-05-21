# l = [i for i in range(20)]

def show(list_, page, n):
	i = (page-1)*n
	s = page*n
	return list_[i:s]

# print(show(l, 6))
