from browser import document, html, bind, worker, alert
from browser.timer import set_interval, clear_interval, set_timeout
from algo import STATES_COLOR
from random import random, randrange


DIM_X = 40
DIM_Y = 30

start_cell = None
end_cell = None

# Construct the worker and send the first message

algo_worker = worker.Worker("worker")
algo_worker.send({"init": (DIM_X, DIM_Y)})

algo = "bfs"
running = False

idx = 0
queue_exe = list()
timer = None


### Initialize HTML grid table ###

for i in range(DIM_Y):
    row = html.TR()
    row_list = []
    for j in range(DIM_X):
        cell = html.TD('', id=f"cell_{i}_{j}", Class="cell", style={"backgroundColor":STATES_COLOR["open"]})
        row <= cell
    document["grid-table"] <= row


def change_status_text(text, bgcolor, textcolor):
    elem = document["status-text"]
    elem.textContent = text
    elem.style.backgroundColor = bgcolor
    elem.style.color = textcolor


def disable_button(button):
    button.disabled = True
    button.style.opacity = 0.6
    button.style.cursor = "not-allowed"


def enable_button(button):
    button.disabled = False
    button.style.opacity = 1.0
    button.style.cursor = "pointer"

change_status_text("Make a starting point", STATES_COLOR["start"], "white")
disable_button(document["run"])


### Binding functions to cells ###

hovering_state = None

@bind(document["main-table"], "mouseleave")
def mouseleave_grid_table(e):
    if not running:
        global hovering_state
        hovering_state = None
        if not start_cell:
            change_status_text("Make a starting point", STATES_COLOR["start"], "white")
        elif not end_cell:
            change_status_text("Make an ending point", STATES_COLOR["end"], "white")
        else:
            change_status_text("Click Run now!", "#555555", "white")

@bind("td.cell", "mouseenter")
def mouseenter_cell(e):
    if not running:
        global hovering_state
        cell = e.currentTarget
        hovering_state = cell.style.backgroundColor
        
        if hovering_state == STATES_COLOR["wall"]:
            change_status_text("Click to remove wall", STATES_COLOR["open"], "black")
        elif cell == start_cell:
            change_status_text("Click to remove this starting point", STATES_COLOR["open"], "black")
        elif cell == end_cell:
            change_status_text("Click to remove this ending point", STATES_COLOR["open"], "black")
        elif not start_cell:
            change_status_text("Click to make cell a starting point", STATES_COLOR["start"], "white")
        elif not end_cell:
            change_status_text("Click to make cell an ending point", STATES_COLOR["end"], "white")
        else:
            change_status_text("Click to make a wall", STATES_COLOR["wall"], "white")

@bind("td.cell", "mousedown")
def mousedown_cell(e):
    if not running:
        global hovering_state, start_cell, end_cell
        cell = e.currentTarget
        if hovering_state == STATES_COLOR["wall"]:
            change_to = "open"
            change_status_text("Click to make a wall", STATES_COLOR["wall"], "white")
        elif cell == start_cell:
            change_to = "open"
            start_cell = None
            change_status_text("Click to make cell a starting point", STATES_COLOR["start"], "white")
        elif cell == end_cell:
            change_to = "open"
            end_cell = None
            change_status_text("Click to make cell an ending point", STATES_COLOR["end"], "white")
        elif not start_cell:
            change_to = "start"
            start_cell = cell
            change_status_text("Click to remove this starting point", STATES_COLOR["open"], "black")
        elif not end_cell:
            change_to = "end"
            end_cell = cell
            change_status_text("Click to remove this ending point", STATES_COLOR["open"], "black")
        else:
            change_to = "wall"
            change_status_text("Click to remove wall", STATES_COLOR["open"], "black")

        click_change_cell(cell, change_to)
        hovering_state = STATES_COLOR[change_to]

        if start_cell and end_cell:
            enable_button(document["run"])
        else:
            disable_button(document["run"])

@bind(document["run"], "click")
def run(e):
    global running
    if not start_cell:
        alert("Must have a starting point")
        return
    elif not end_cell:
        alert("Must have an ending point")
        return
    if algo == "bfs":
        algo_worker.send("run-bfs")
    elif algo == "a_star":
        algo_worker.send("run-a-star")
    running = True
    disable_button(document["run"])
    disable_button(document["randomize"])
    disable_button(document["reset"])
    change_status_text("Looking for the path...", "#555555", "white")

@bind(document["randomize"], "click")
def randomize(e):
    global start_cell, end_cell, running
    running = False

    # Make random starting and ending point
    start_row, start_col = randrange(DIM_Y), randrange(DIM_X)
    end_row, end_col = randrange(DIM_Y), randrange(DIM_X)
    start_cell = document[f"cell_{start_row}_{start_col}"]
    end_cell = document[f"cell_{end_row}_{end_col}"]

    # Make random walls
    wall_proba = 0.2

    for i in range(DIM_Y):
        for j in range(DIM_X):
            if (i, j) == (start_row, start_col):
                click_change_cell(start_cell, "start")
                continue
            elif (i, j) == (end_row, end_col):
                click_change_cell(end_cell, "end")
                continue
            num = random()
            cell = document[f"cell_{i}_{j}"]
            if num < wall_proba:
                click_change_cell(cell, "wall")
            else:
                click_change_cell(cell, "open")
    change_status_text("Click Run now!", "#555555", "white")
    enable_button(document["run"])
            

@bind(document["reset"], "click")
def reset_grid(e):
    def do():
        global start_cell, end_cell
        start_cell = None
        end_cell = None
        for i in range(DIM_Y):
            for j in range(DIM_X):
                cell = document[f"cell_{i}_{j}"]
                if cell.style.backgroundColor != STATES_COLOR["open"]:
                    click_change_cell(cell, "open")
        change_status_text("Make a starting point", STATES_COLOR["start"], "white")

    global running
    change_status_text("Resetting the grid...", "transparent", "black")
    set_timeout(do, 10)
    disable_button(document["run"])
    running = False

@bind(document["choose-bfs"], "click")
def choose_bfs(e):
    global algo
    document["run"].textContent = "Run BFS"
    algo = "bfs"

@bind(document["choose-a-star"], "click")
def choose_a_star(e):
    global algo
    document["run"].textContent = "Run A*"
    algo = "a_star"

@bind(algo_worker, "message")
def worker_callback(e):
    global queue_exe, timer
    queue_exe.append(e.data)
    if timer is None:
        timer = set_interval(parse_queue_exe, 30)

def click_change_cell(cell, state):
    cell.style.backgroundColor = STATES_COLOR[state]
    algo_worker.send({"change": f"{cell.id} {state}"})

def parse_queue_exe():
    global queue_exe, timer, idx, running
    if not queue_exe:
        return
    if queue_exe[idx] not in ("found", "no way"):
        cell_id, color = queue_exe[idx].split(' ')
        cell = document[cell_id]
        cell.style.backgroundColor = color
        idx += 1
    else:
        results = queue_exe[idx]
        idx = 0
        queue_exe = list()
        clear_interval(timer)
        timer = None
        enable_button(document["reset"])
        enable_button(document["randomize"])
        if results == "found":
            change_status_text("Path found. Click Reset to try again", STATES_COLOR["path"], "white")
        else:
            change_status_text("No path found. Click Reset to try again", "transparent", "black")