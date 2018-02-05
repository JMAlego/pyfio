def spiral_pattern(self):
  direction = [(1,0),(0,1),(-1,0),(0,-1)]
  point = (0,0)
  cycle = 0
  size = self.__col_row_size
  limit = size - 1
  n = 0
  while n < size**2:
    for i in range(0, limit):
      yield point
      point = (point[0]+direction[cycle%4][0], point[1]+direction[cycle%4][1])
      n += 1
    cycle += 1
    if (cycle < 3 and cycle == 0) or (cycle > 2 and cycle%2 == 1 and cycle != (2*size - 1)):
      limit = limit - 1

def spiral_pattern_inverse(self):
  direction = [(1,0),(0,1),(-1,0),(0,-1)]
  cycle = 0
  size = self.__col_row_size
  point = (size/2,size/2 - 1)
  limit = 0
  n = 0
  while n < size**2:
    for i in range(0, limit):
      yield point
      point = (point[0]+direction[cycle%4][0], point[1]+direction[cycle%4][1])
      n += 1
    cycle += 1
    if cycle%2 == 1:
      limit = limit + 1
       
def left_to_right_pattern(self):
  for y in range(0, self.__col_row_size):
    for x in range(0, self.__col_row_size):
      yield (x,y)

def random_pattern(self):
  picked = []
  while len(picked) < self.__board_size:
    rand = (random.randint(0, self.__col_row_size), random.randint(0, self.__col_row_size))
    if not rand in picked:
      yield rand
      picked.append(rand)
      
def random_pattern_2(self):
  items = []
  for item in self.left_to_right_pattern():
    items.append(item)
  random.shuffle(items)
  for item in items:
    yield item