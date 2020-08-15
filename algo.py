STATES_COLOR = {
    "open":     "gainsboro",
    "wall":     "black",
    "start":    "seagreen",
    "end":      "orangered",
    "queue":    "orange",
    "searched": "khaki",
    "path":     "slateblue"
}


class Grid:
    def __init__(self, dim_x, dim_y, send_func):
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.send_func = send_func
        self.nodes = list()
        self.start = None
        self.end = None

    def send_to_main(self, node):
        msg = node.get_cell_id() + " " + node.get_state()
        self.send_func(msg)

    def make_nodes_list(self, l):
        self.nodes = l

    def change_start_node(self, node):
        self.start = node

    def change_end_node(self, node):
        self.end = node

    def find_neighbors(self, node):
        i, j = node.get_pos()
        neigbor_list = list()
        for row, col in [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]:
            if (0 <= row < self.dim_y) and (0 <= col < self.dim_x) and (self.nodes[row][col].state != STATES_COLOR["wall"]):
                neigbor_list.append(self.nodes[row][col])
        return neigbor_list

    def backtrack(self, came_from):
        current = self.end
        while current in came_from:
            current = came_from[current]
            current.change_state("path")
            self.send_to_main(current)
        self.start.change_state("start")
        self.send_to_main(self.start)
        self.end.change_state("end")
        self.send_to_main(self.end)

    def run_bfs(self):
        came_from = dict()

        queue = list()
        queue.append(self.start)
        queue_set = {self.start}

        while queue:
            current = queue.pop(0)
            queue_set.remove(current)

            for neighbor in self.find_neighbors(current):
                if neighbor == self.start or neighbor.state == STATES_COLOR["searched"]: continue
                came_from[neighbor] = current

                if neighbor == self.end:
                    self.backtrack(came_from)
                    return True

                if neighbor not in queue_set:
                    queue.append(neighbor)
                    queue_set.add(neighbor)
                    neighbor.change_state("queue")
                    self.send_to_main(neighbor)
            if current != self.start:
                current.change_state("searched")
                self.send_to_main(current)
        return False

    def run_a_star(self):
        def compute_h(node1, node2):
            i1, j1 = node1.get_pos()
            i2, j2 = node2.get_pos()
            return abs(i1 - i2) + abs(j1 - j2)

        count = 0
        came_from = dict()

        queue = list()
        queue.append((0, count, self.start))
        queue_set = {self.start}
        
        g_score = {node: self.dim_x + self.dim_y + 1 for row in self.nodes for node in row}
        f_score = g_score.copy()

        g_score[self.start] = 0
        f_score[self.start] = compute_h(self.start, self.end)

        while queue:
            item = min(queue)
            current = item[2]
            queue.remove(item)
            queue_set.remove(current)

            for neighbor in self.find_neighbors(current):
                g_temp = g_score[current] + 1
                if g_temp < g_score[neighbor]:
                    came_from[neighbor] = current
                    if neighbor == self.end:
                        self.backtrack(came_from)
                        return True

                    g_score[neighbor] = g_temp
                    f_score[neighbor] = g_temp + compute_h(neighbor, self.end)
                    if neighbor not in queue_set:
                        count += 1
                        queue.append((f_score[neighbor], count, neighbor))
                        queue_set.add(neighbor)
                        neighbor.change_state("queue")
                        self.send_to_main(neighbor)
            if current != self.start:
                current.change_state("searched")
                self.send_to_main(current)
        return False


class Node:
    def __init__(self, cell_id, row, col):
        self.cell_id = cell_id
        self.row = row
        self.col = col
        self.change_state("open")

    def change_state(self, state):
        self.state = STATES_COLOR[state]

    def get_cell_id(self):
        return self.cell_id

    def get_state(self):
        return self.state

    def get_pos(self):
        return self.row, self.col

    def __lt__(self, other):
        return False
