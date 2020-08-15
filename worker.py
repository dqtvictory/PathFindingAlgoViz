from browser import self, bind
from algo import Grid, Node

@bind(self, "message")
def message(e):
    # Init
    if "init" in e.data:
        global DIM_X, DIM_Y
        DIM_X, DIM_Y = e.data["init"]
        init_grid()
        return

    # Change node's state
    elif "change" in e.data:
        cell_id, state = e.data["change"].split(' ')
        i, j = map(lambda x: int(x), cell_id.split('_')[1:])
        node = grid.nodes[i][j]
        node.change_state(state)
        if state == "start":
            grid.change_start_node(node)
        elif state == "end":
            grid.change_end_node(node)
        return

    # Execution & response to main script
    if e.data == "run-bfs":
        results = grid.run_bfs()

    elif e.data == "run-a-star":
        results = grid.run_a_star()

    if results:
        self.send("found")
    else:
        self.send("no way")


def init_grid():
    global grid
    grid = Grid(DIM_X, DIM_Y, self.send)
    nodes = list()
    for i in range(DIM_Y):
        row_list = []
        for j in range(DIM_X):
            cell_id = f"cell_{i}_{j}"
            node = Node(cell_id, i, j)
            row_list.append(node)
        nodes.append(row_list)
    grid.make_nodes_list(nodes)


