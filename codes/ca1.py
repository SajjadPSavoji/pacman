import queue
import sys
import enum
import copy
import heapq
import sys
import timeit
import time

# ___________________________________________________________________________________________________
P = 'P'
Q = 'Q'
Fruits = ['1','2','3']
Agents = [P , Q]
Agent_restricted_fruit = [[2],[1]]
Wall = '%'
Blank = ' '
# file_path = None
# ___________________________________________________________________________________________________
class Move(enum.Enum):
    Up    = (-1 , 0)
    Down  = (1 , 0)
    Right = (0,1)
    Left  = (0,-1)

# ___________________________________________________________________________________________________
def manh_dist(tup1 , tup2):
        return abs(tup1[0] - tup2[0]) + abs(tup1[1] - tup2[1])
def pos_add(tup1 , tup2):
    return (tup1[0] + tup2 [0] , tup1[1] + tup2 [1])
def read_map(file_path):
    if file_path is None:
        l = sys.stdin.read()
    else:
        with open(file_path, 'r') as content_file:
            l = content_file.read()

    l = l.split('\n')
    for i in range(len(l)) :
        l[i] = list(l[i])

    agents_pos = [(-1 , -1) for i in Agents]
    fruits_pos = [[] for i in Fruits]
    dim0 = len(l)
    dim1 = len(l[0])

    for i in range(dim0):
        for j in range(dim1):
            if l[i][j] in Agents:
                agents_pos[Agents.index(l[i][j])]=(i,j)
                l[i][j] = Blank
            elif l[i][j] is Wall:
                continue
            elif l[i][j] is Blank:
                continue
            elif l[i][j] in Fruits:
                fruits_pos[Fruits.index(l[i][j])].append((i,j))
                l[i][j] = Blank
            else :
                raise Exception(f"found unexpected char {l[i][j]} in  map") 
    return l , fruits_pos , agents_pos , dim0 , dim1
# __________________________________________________________________________________________________
class State():
    def __init__(self , fruits_pos , agents_pos ,cost = 0):
        self.cost = cost
        self.fruits_pos = fruits_pos
        self.agents_pos = agents_pos
        # self.priority = self.cost
        self.priority = self.cost + self.longest()
    def __hash__(self):
        tup = ()
        for i in range(len(self.agents_pos)):
            tup += self.agents_pos[i]
        for i in range(len(self.fruits_pos)):
            for j in range(len(self.fruits_pos[i])):
                tup += self.fruits_pos[i][j]
        return hash(tup)

    def longest(self):
        m = 0
        for i in range(len(self.agents_pos)):
            for f in range(len(self.fruits_pos)):
                if (f+1) in Agent_restricted_fruit[i]:
                    continue
                for pos in self.fruits_pos[f]:
                    temp= manh_dist(self.agents_pos[i] , pos)
                    m = max(m , temp)
        return m        

    def longer(self):
        s = 0
        for i in range(len(self.agents_pos)):
            count = 0
            m = 0
            for f in range(len(self.fruits_pos)):
                if (f+1) in Agent_restricted_fruit[i]:
                    continue
                for pos in self.fruits_pos[f]:
                    temp= manh_dist(self.agents_pos[i] , pos)
                    m = max(m , temp)
                    count += 1
            s+= m + count -1        
        return s/len(Agents)

    def num_fruits(self):
        count = 0
        for fruit in self.fruits_pos:
            count += len(fruit)
        return count

    def manhatan(self):
        man = 0
        count = 0
        for i in range(len(self.agents_pos)):
            for f in range(len(self.fruits_pos)):
                man_f = 0
                if (f+1) in Agent_restricted_fruit[i]:
                    continue
                for pos in self.fruits_pos[f]:
                    man_f += manh_dist(self.agents_pos[i] , pos)
                    count += 1
                man += man_f        
        return man/(2*count)

    def __lt__(self , other) : 
        return self.priority < other.priority
    def __str__(self):
        # copy map
        new_map = copy.deepcopy(RAW_MAP)
        # place agents
        for i in range(len(self.agents_pos)):
            if not self.agents_pos[i] == (-1 , -1):
                x , y = self.agents_pos[i]
                new_map[x][y] = Agents[i]
        # place fruits if any...
        for i , l in enumerate(self.fruits_pos):
            for pos in l:
                if not pos == (-1 , -1):
                    x , y = pos
                    new_map[x][y] = Fruits[i]
        for i in range(len(new_map)) : 
            new_map[i] = "".join(new_map[i])
        s = ""
        for i in range(len(new_map)):
            s += new_map[i]
            s += '\n'
        return s

    def __eq__ (self , other) : 
        # fruits be the same
        return hash(self) == hash(other)

    def move_cost(self , move):
        return 1
    
    def make_move(self, agent , move):
        agent_pos = self.agents_pos[Agents.index(agent)]
        new_cost = self.cost + self.move_cost(move)
        new_pos = pos_add(move.value , agent_pos)
        # update agent position
        agents_pos = copy.deepcopy(self.agents_pos)
        agents_pos[Agents.index(agent)] = new_pos
        # update fruits position
        fruits_pos = copy.deepcopy(self.fruits_pos)
        for i in range(len(fruits_pos)):
            for j in range(len(fruits_pos[i])):
                if fruits_pos[i][j] == new_pos:
                    fruits_pos[i][j] = (-1 , -1)
                    break
        return State(fruits_pos , agents_pos , new_cost)   

    def make_child(self , agent , move):
        agent_pos = self.agents_pos[Agents.index(agent)]
        if agent_pos == (-1 , -1) : 
            return None
        if not self.can_move(agent , move) : 
            return None
        return self.make_move(agent , move)

    def expand(self):
        childs = []
        for agent in Agents : 
            for move in Move:
               child = self.make_child(agent ,move)
               if child is not None : 
                   childs.append(child)
        return childs

    def can_move(self , agent , move):
        if agent not in Agents : 
            raise Exception(f"unexpected request form agent:{agent}")
        new_pos = pos_add(move.value , self.agents_pos[Agents.index(agent)])
        x , y = new_pos
        # if is wall
        if RAW_MAP[x][y] == Wall:
            return False
        # if is other agents position
        for i in self.agents_pos : 
            if (x , y) == i : 
                return False
        # if is out of boundry
        if x >= DIM0 or x < 0 or y < 0 or y >= DIM1 : 
            return False
        # agent can not eat the fruit
        for i in range(len(self.fruits_pos)):
            if ((x , y) in self.fruits_pos[i]) and ((i+1) in Agent_restricted_fruit[Agents.index(agent)]):
                return False
        return True

    def is_goal(self):
        for i in self.fruits_pos :
            for j in i:
                if not j == (-1 , -1):
                    return False
        return True

# ___________________________________________________________________________________________________
def BFS(init_state):
    met = {}
    Q = []
    Q.append(init_state)
    met.update({init_state:1})
    while len(Q):
        frontier = Q.pop(0)
        # met.update({frontier:1})

        print(f"nodes met : {len(met)}" , end = "")
        print('\r' , end = "")

        if frontier.is_goal() :
            print(frontier.cost)
            print('\n') 
            return frontier , len(met)
        childs = frontier.expand()
        for child in childs : 
            if child not in met:
                Q.append(child)
                met.update({child:1})
    print('\n')
    return None , len(met)
# __________________________________________________________________________________________________
def DFS(init_state , depth):
    '''
    Q is lifo queue or stack
        for initial state Q should contain initial state
    met is dictionary containing all the visited nodes
        for initial state met should contain initial state
    depth is maximum cost of node
    '''
    Q = []
    met = {}
    Q.append(init_state)
    met.update({init_state:1})

    while len(Q):
        frontier = Q.pop(-1)

        # print(f"nodes met : {len(met)}" , end = "")
        # print('\r' , end = "")

        if frontier.is_goal() : 
            # print('\n')
            return frontier , met
        if frontier.cost == depth :
            continue
        childs = frontier.expand()
        for child in childs : 
            if child not in met:
                Q.append(child)
                met.update({child:1})
    return None , met  
# __________________________________________________________________________________________________
def IDS(init_state):
    depth = 0
    while(True):
        node , met = DFS(init_state , depth)
        if node is not None : 
            print("goal found with cost : " , node.cost)
            return node , len(met)
        print(f"search with depth {depth} unsuccessfull")
        depth += 1

# __________________________________________________________________________________________________
def AS(init_state):
    met = {}
    pending = {}
    Q = []
    # heapq.heappush(Q , init_state)
    Q.append(init_state)
    pending.update({init_state:1})
    while len(Q):
        print(f"nodes met : {len(met)}" , end = "")
        print('\r' , end = "")

        # frontier = heapq.heappop(Q)
        frontier = Q.pop(Q.index(min(Q)))

        pending.pop(frontier)
        met.update({frontier:1})


        if frontier.is_goal() :
            print('\n') 
            print(frontier.cost)
            return frontier , len(met)
        childs = frontier.expand()
        for child in childs : 
            if child not in met:
                if child not in pending:
                    Q.append(child)
                    pending.update({child : 1})
                else :
                    if child < Q[Q.index(child)]:
                        Q[Q.index(child)] = child
    print('\n')
    return None , len(met)
# ___________________________________________________________________________________________________
def do_BFS(file_path = None):
    global RAW_MAP , DIM0 , DIM1
    RAW_MAP , fruits_pos , agents_pos ,DIM0 , DIM1 = read_map(file_path)
    init_state = State(fruits_pos , agents_pos)
    # print(init_state)
    # BFS method
    goal , node_met = BFS(init_state)
    # print(goal)
    # print(f"goal actual cost: {goal.cost}")
    # print(f"number of node met in BFS: {node_met}")
    return goal , node_met
# ______________________________________________________________________________________________________
def do_IDS(file_path = None):
    global RAW_MAP , DIM0 , DIM1
    RAW_MAP , fruits_pos , agents_pos ,DIM0 , DIM1 = read_map(file_path)
    init_state = State(fruits_pos , agents_pos)
    # print(init_state)
    goal , node_met = IDS(init_state)
    # print(goal)
    # print(f"goal actual cost: {goal.cost}")
    # print(f"number of node met in IDS: {node_met}")
    return goal , node_met

# ______________________________________________________________________________________________________
def do_AS(file_path = None ):
    global RAW_MAP , DIM0 , DIM1
    RAW_MAP , fruits_pos , agents_pos ,DIM0 , DIM1 = read_map(file_path)
    init_state = State(fruits_pos , agents_pos)
    # print(init_state)
    # A* algorithem
    goal , node_met = AS(init_state)
    # print(goal)
    # print(f"goal actual cost: {goal.cost}")
    # print(f"number of node met in A*: {node_met}")
    return goal , node_met
# ______________________________________________________________________________________________________
def t_code(function , init_state , r):
    s = 0
    for i in range(r):
        start = time.time()
        function(init_state)
        end = time.time()
        s += end - start
    return s/r  

if __name__ == "__main__":

    global RAW_MAP , DIM0 , DIM1
    RAW_MAP , fruits_pos , agents_pos ,DIM0 , DIM1 = read_map(None)
    init_state = State(fruits_pos , agents_pos)

    # print("bfs_time : ")
    # print(t_code(BFS , init_state , 3))

    # print("ids_time : ")
    # print(t_code(IDS , init_state , 3))

    print("as_time : ")
    print(t_code(AS , init_state , 1))

    # s = sys.argv[1]
    # name = sys.argv[2]
    # if s == "AS":
    #     elapsed_time = timeit.timeit(do_AS,number=3)/3
    #     print(elapsed_time)
    # elif s == "BFS":
    #     elapsed_time = timeit.timeit(do_BFS,number=3)/3
    #     print(elapsed_time)
    # elif s == "IDS":
    #     elapsed_time = timeit.timeit(do_IDS,number=3)/3
    #     print(elapsed_time)
    # else : 
    #     print("dude watch it!")        
    
    