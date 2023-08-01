
from time import time
from copy import deepcopy
from random import choice
import numpy as np
from math import sqrt,log


class SmartAgent():
    
    def __init__(self):
        self.autoplay=True
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

    def step(self, chess_board, my_pos, adv_pos, max_step):
        start=time()
        root = MCTtree(board=chess_board, action=(0,0,0), my_pos=my_pos, adv_pos=adv_pos, max_step=max_step, parent=None)
        root.add_p_actions(my_pos, adv_pos)
        return root.best_move(start)

class MCTtree:
    def __init__(self, board, action, my_pos, adv_pos, max_step, parent=None):
        self.terminal = False
        self.moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        self.my_pos = my_pos
        self.adv_pos = adv_pos
        self.max_step = max_step
        self.father={}
        self.board = board
        self.action = action #(x,y,dir)
        self.parent = parent
        self.n = 0
        self.w = 0
        self.p_a = []
        self.visited_children=[]
    
    
    def add_p_actions(self, my_pos, adv_pos):
        moves = np.where(self.board == False)
        valid_moves = self.valid_move_generation(self.board, my_pos, adv_pos, self.max_step)
        self.p_a = [(moves[0][i],moves[1][i],moves[2][i])
                    for i in valid_moves[0]
                    if self.check_valid_step(my_pos,np.array((moves[0][i],moves[1][i])),
                                                                         moves[2][i],adv_pos,self.max_step)]
            
    def valid_move_generation(self, board, my_pos, adv_pos, max_step):
        moves = np.where(board == False)
        valid_moves = np.where(abs(moves[0] - my_pos[0]) + abs(moves[1] - my_pos[1]) <= max_step)
        return valid_moves

    
    def best_child(self):
        uct_list = [(c.w / c.n + sqrt(2 * log(self.n) / c.n)) for c in self.visited_children if c.n != 0]
        return self.visited_children[np.argmax(uct_list)]


    def play_simulation(self,board, action):
        size = len(self.board)
        opposites = {0: 2, 1: 3, 2: 0, 3: 1}
        r,c,d=action[0],action[1],action[2]
        board[r,c,d] = True
        move=self.moves[d]
        if r + move[0]>=0 and r + move[0] < size and c + move[1] < size and c + move[1]>=0:
            board[r + move[0], c + move[1], opposites[d]] = True
        return board
        
    def selection(self,d):
        cur = self
        while len(cur.p_a)==0 and not cur.terminal:
            best_node = cur.best_child()
            d+=1
            cur = best_node
        satisfied = False     
        while not satisfied:
            if len(cur.p_a)<=2:
                rd_a = cur.p_a.pop()
                break
            else:
                rd_a = cur.p_a.pop()
                if sum(cur.board[rd_a[0],rd_a[1]]) >= 2:
                    satisfied = False
                else:
                    satisfied = True
        copy_b = deepcopy(cur.board)
        new_board = cur.play_simulation(copy_b,rd_a)
        new_child = MCTtree(board=new_board, action=rd_a, my_pos=cur.adv_pos,
                            adv_pos=np.array((rd_a[0],rd_a[1])), max_step=self.max_step, parent=cur)
        new_child.add_p_actions(my_pos = new_child.my_pos, adv_pos = new_child.adv_pos)
        if len(new_child.p_a) == 0:
            new_child.terminal = True
            if d%2 == 1:
                new_child.backpropagation(1,d)
            else:
                new_child.backpropagation(0,d)
            self.selection(0)
        else:
            cur.visited_children.append(new_child)
            d+=1
        return (new_child,d)

    def simulation(self,d):
        cur_board = deepcopy(self.board)
        if d%2 == 1:
            my_pos = self.adv_pos
            adv_pos = self.my_pos
            turn = 1
        else:
            my_pos = self.my_pos
            adv_pos = self.adv_pos
            turn = 0
            
        over, s1, s2 = self.check_endgame(cur_board, my_pos, adv_pos)
        while not over:
            if turn == 1:
                x = choice(self.valid_move_generation(cur_board, adv_pos, my_pos, self.max_step)[0])
                actions = np.where(cur_board == False)
                cur_board = self.play_simulation(cur_board, (actions[0][x],actions[1][x], actions[2][x]))
                adv_pos = np.array((actions[0][x],actions[1][x]))
                turn = 0
            else:
                x = choice(self.valid_move_generation(cur_board, my_pos, adv_pos, self.max_step)[0])
                actions = np.where(cur_board == False)
                cur_board = self.play_simulation(cur_board, (actions[0][x],actions[1][x], actions[2][x]))
                my_pos = np.array((actions[0][x],actions[1][x]))
                turn = 1
            over, s1, s2 = self.check_endgame(cur_board, my_pos, adv_pos)
        if s1>s2:
            return 1
        else:
            return 0
    
    def backpropagation(self, result, d):
        cur = self
        while d!=-1:
            cur.n += 1
            if d%2 == result:
                cur.w += 1
            d -= 1
            cur=cur.parent
            
    def check_valid_step(self, start_pos, end_pos, barrier_dir,adv_pos, max_step):
        r, c = end_pos
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        state_queue = [(start_pos, 0)]
        visited = {tuple(start_pos)}
        is_reached = False
        while state_queue and not is_reached:
            cur_pos, cur_step = state_queue.pop(0)
            r,c = cur_pos
            if cur_step == self.max_step:
                break
            for dir, move in enumerate(moves):
                if self.board[r,c,dir]:
                    continue

                next_pos = (cur_pos[0] + move[0],cur_pos[1] + move[1])
                if np.array_equal(next_pos, adv_pos) or tuple(next_pos) in visited:
                    continue
                if np.array_equal(next_pos, end_pos):
                    is_reached = True
                    break

                visited.add(tuple(next_pos))
                state_queue.append((next_pos, cur_step+1))

        return is_reached

                    
    def check_endgame(self,board, my_pos, adv_pos):
        size = len(self.board)
        father = dict()
        for r in range(size):
            for c in range(size):
                father[(r, c)] = (r, c)
        def find(pos):
            if father[pos] != pos:
                father[pos] = find(father[pos])
            return father[pos]
        def union(pos1, pos2):
            father[pos1] = pos2
        for r in range(size):
            for c in range(size):
                for dir, move in enumerate(
                    self.moves[1:3]
                ):  
                    if board[r,c,dir + 1]:
                        continue
                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)
        for r in range(size):
            for c in range(size):
                find((r, c))
        p0_r = find(tuple(my_pos))
        p1_r = find(tuple(adv_pos))
        p0_score = list(father.values()).count(p0_r)
        p1_score = list(father.values()).count(p1_r)
        if p0_r == p1_r:
            return False, p0_score, p1_score
        return True, p0_score, p1_score

    def best_move(self,start):
        while(time()-start < 1.9):
            expanded_node_with_depth = self.selection(0)
            game_result = expanded_node_with_depth[0].simulation(expanded_node_with_depth[1])
            expanded_node_with_depth[0].backpropagation(game_result,expanded_node_with_depth[1])
        optimal = self.best_child().action
        return (optimal[0],optimal[1]),int(optimal[2])
