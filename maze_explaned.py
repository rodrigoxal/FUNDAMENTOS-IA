import sys

# Classe que representa um nó no grafo de busca
class Node():
    def __init__(self, state, parent, action):
        self.state = state  # Estado atual (posição no labirinto)
        self.parent = parent  # Nó pai (para reconstruir o caminho)
        self.action = action  # Ação tomada para chegar a este nó

# Classe que representa a fronteira usando Pilha (para busca em profundidade - DFS)
class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]  # Remove o último (LIFO - Pilha)
            self.frontier = self.frontier[:-1]
            return node

# Classe que representa a fronteira usando Fila (para busca em largura - BFS)
class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]  # Remove o primeiro (FIFO - Fila)
            self.frontier = self.frontier[1:]
            return node

# Classe que representa o labirinto e sua solução
class Maze():
    def __init__(self, filename):
        # Ler arquivo e armazenar o labirinto
        with open(filename) as f:
            contents = f.read()
        
        # Verificar se há exatamente um ponto de início (A) e um ponto de chegada (B)
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")
        
        # Definir altura e largura do labirinto
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)
        
        # Criar matriz de paredes
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)  # Definir ponto de início
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)  # Definir ponto de chegada
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)  # Caminhos livres
                    else:
                        row.append(True)  # Paredes
                except IndexError:
                    row.append(False)
            self.walls.append(row)
        
        self.solution = None

    # Método para imprimir o labirinto e a solução, se existir
    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")  # Paredes
                elif (i, j) == self.start:
                    print("A", end="")  # Início
                elif (i, j) == self.goal:
                    print("B", end="")  # Destino
                elif solution is not None and (i, j) in solution:
                    print("*", end="")  # Caminho da solução
                else:
                    print(" ", end="")  # Caminhos livres
            print()
        print()

    # Método para encontrar vizinhos válidos de um estado
    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]
        
        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    # Método para resolver o labirinto usando busca em profundidade
    def solve(self):
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()  # Usando pilha (DFS)
        frontier.add(start)
        self.explored = set()
        
        while True:
            if frontier.empty():
                raise Exception("no solution")
            
            node = frontier.remove()
            self.num_explored += 1
            
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return
            
            self.explored.add(node.state)
            
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    # Método para gerar uma imagem do labirinto
    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        img = Image.new("RGBA", (self.width * cell_size, self.height * cell_size), "black")
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    fill = (40, 40, 40)
                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)
                else:
                    fill = (237, 240, 252)
                draw.rectangle([(j * cell_size + cell_border, i * cell_size + cell_border), ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)], fill=fill)
        img.save(filename)

if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1])
m.print()
m.solve()
print("States Explored:", m.num_explored)
m.print()
m.output_image("maze.png", show_explored=True)
