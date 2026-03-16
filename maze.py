#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import random
import heapq
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QSpinBox, QComboBox, QLabel, QCheckBox)
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt

class MazeSolver:
    def __init__(self, width, height, algorithm="DFS"):
        self.width = width if width % 2 != 0 else width + 1
        self.height = height if height % 2 != 0 else height + 1
        self.grid = [[1] * self.width for _ in range(self.height)]
        self.path = [] # 存储最终路径坐标
        self.explored_nodes = [] # 存储尝试过的位置
        self.generate(algorithm)

    def generate(self, algorithm="DFS"):
        """根据选择的算法生成迷宫"""
        # 重置网格，全为墙
        self.grid = [[1] * self.width for _ in range(self.height)]
        
        if algorithm == "DFS":
            self._generate_dfs(1, 1)
        elif algorithm == "Prim":
            self._generate_prim()
        elif algorithm == "Kruskal":
            self._generate_kruskal()
        elif algorithm == "Wilson":
            self._generate_wilson()

    def _generate_dfs(self, x, y):
        """递归回溯生成迷宫"""
        self.grid[y][x] = 0
        dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < self.width and 0 < ny < self.height and self.grid[ny][nx] == 1:
                self.grid[y + dy // 2][x + dx // 2] = 0
                self._generate_dfs(nx, ny)

    def _generate_prim(self):
        """Prim 算法生成迷宫"""
        start_x, start_y = 1, 1
        self.grid[start_y][start_x] = 0
        walls = []
        
        # 将起点周围的墙加入列表
        for dx, dy in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
            nx, ny = start_x + dx, start_y + dy
            if 0 < nx < self.width and 0 < ny < self.height:
                walls.append((start_x, start_y, nx, ny))
        
        while walls:
            # 随机选择一面墙
            wall_index = random.randint(0, len(walls) - 1)
            x1, y1, x2, y2 = walls.pop(wall_index)
            
            if self.grid[y2][x2] == 1:
                # 打通墙
                self.grid[(y1 + y2) // 2][(x1 + x2) // 2] = 0
                self.grid[y2][x2] = 0
                
                # 将新单元格周围的墙加入列表
                for dx, dy in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                    nx, ny = x2 + dx, y2 + dy
                    if 0 < nx < self.width and 0 < ny < self.height and self.grid[ny][nx] == 1:
                        walls.append((x2, y2, nx, ny))

    def _generate_kruskal(self):
        """Kruskal 算法生成迷宫"""
        parent = {}
        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False

        walls = []
        for y in range(1, self.height, 2):
            for x in range(1, self.width, 2):
                parent[(x, y)] = (x, y)
                if x + 2 < self.width:
                    walls.append((x, y, x + 2, y))
                if y + 2 < self.height:
                    walls.append((x, y, x, y + 2))
        
        random.shuffle(walls)
        
        for x1, y1, x2, y2 in walls:
            if union((x1, y1), (x2, y2)):
                self.grid[y1][x1] = 0
                self.grid[y2][x2] = 0
                self.grid[(y1 + y2) // 2][(x1 + x2) // 2] = 0

    def _generate_wilson(self):
        """Wilson 算法生成迷宫"""
        cells = [(x, y) for y in range(1, self.height, 2) for x in range(1, self.width, 2)]
        unvisited = set(cells)
        
        # 随机选择一个起点加入已访问集合
        start_cell = random.choice(cells)
        unvisited.remove(start_cell)
        self.grid[start_cell[1]][start_cell[0]] = 0
        
        while unvisited:
            # 随机选择一个未访问的单元格开始随机游走
            start = random.choice(list(unvisited))
            path = [start]
            
            while path[-1] in unvisited:
                curr_x, curr_y = path[-1]
                dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
                dx, dy = random.choice(dirs)
                nx, ny = curr_x + dx, curr_y + dy
                
                if 0 < nx < self.width and 0 < ny < self.height:
                    if (nx, ny) in path:
                        # 发现环，擦除环的部分
                        path = path[:path.index((nx, ny)) + 1]
                    else:
                        path.append((nx, ny))
            
            # 将路径上的所有单元格打通
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i+1]
                self.grid[y1][x1] = 0
                self.grid[y2][x2] = 0
                self.grid[(y1 + y2) // 2][(x1 + x2) // 2] = 0
                if (x1, y1) in unvisited:
                    unvisited.remove((x1, y1))
            
            # 最后一个点已经是在迷宫里的，所以不需要打通它（已经在之前的循环中打通了或者是最初的起点）
            # 但是由于循环逻辑，我们需要确保 path[i] 被处理了。
            # 实际上 path[-1] 是已经在已访问集合里的。

    def break_walls(self, count=None):
        """随机拆除墙壁以产生环路"""
        if count is None:
            # 默认拆除约 5% 的墙壁
            count = (self.width * self.height) // 20
        
        walls = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y][x] == 1:
                    # 检查是否是位于两个通道之间的墙
                    # 水平方向
                    if self.grid[y][x-1] == 0 and self.grid[y][x+1] == 0:
                        walls.append((x, y))
                    # 垂直方向
                    elif self.grid[y-1][x] == 0 and self.grid[y+1][x] == 0:
                        walls.append((x, y))
        
        if walls:
            random.shuffle(walls)
            for i in range(min(count, len(walls))):
                wx, wy = walls[i]
                self.grid[wy][wx] = 0

    def solve(self, start, end, algorithm="DFS"):
        """寻路算法入口"""
        self.explored_nodes = [] # 清空尝试记录
        if algorithm == "DFS":
            return self._solve_dfs(start, end)
        else:
            return self._solve_astar(start, end)

    def _solve_dfs(self, start, end):
        """DFS 寻路算法"""
        visited = set()
        self.path = []
        
        def dfs(curr_x, curr_y):
            if (curr_x, curr_y) == end:
                self.path.append((curr_x, curr_y))
                return True
            
            visited.add((curr_x, curr_y))
            self.explored_nodes.append((curr_x, curr_y))
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = curr_x + dx, curr_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx] == 0 and (nx, ny) not in visited:
                        if dfs(nx, ny):
                            self.path.append((curr_x, curr_y))
                            return True
            return False

        dfs(start[0], start[1])
        return self.path

    def _solve_astar(self, start, end):
        """A-Star 寻路算法"""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        start_h = heuristic(start, end)
        open_set = []
        # 使用 (f_score, h_score, node) 作为优先级，h_score 用于在 f_score 相等时进行启发式打破平局
        heapq.heappush(open_set, (start_h, start_h, start))
        came_from = {}
        g_score = {start: 0}
        
        visited_nodes = set()

        while open_set:
            f, h, current = heapq.heappop(open_set)
            
            if current in visited_nodes:
                continue
                
            if current == end:
                self.path = []
                while current in came_from:
                    self.path.append(current)
                    current = came_from[current]
                self.path.append(start)
                return self.path

            visited_nodes.add(current)
            self.explored_nodes.append(current)
            
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if 0 <= neighbor[0] < self.width and 0 <= neighbor[1] < self.height:
                    if self.grid[neighbor[1]][neighbor[0]] == 1 or neighbor in visited_nodes:
                        continue
                    
                    tentative_g_score = g_score[current] + 1
                    
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        h_score = heuristic(neighbor, end)
                        f_score = tentative_g_score + h_score
                        heapq.heappush(open_set, (f_score, h_score, neighbor))
        
        self.path = []
        return self.path

class MazeWidget(QWidget):
    def __init__(self, maze):
        super().__init__()
        self.maze = maze
        self.show_solution = False
        self.setMinimumSize(500, 500)

    def set_maze(self, maze):
        self.maze = maze
        self.update()

    def paintEvent(self, event):
        if not self.maze:
            return
            
        painter = QPainter(self)
        # 确保单元格是正方形，取长宽中的最小值作为边长
        cell_size = min(self.width() / self.maze.width, self.height() / self.maze.height)
        
        # 计算偏移量以使迷宫在窗口中居中
        offset_x = (self.width() - cell_size * self.maze.width) / 2
        offset_y = (self.height() - cell_size * self.maze.height) / 2

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                # 绘制墙和路
                color = QColor(0, 200, 0) if self.maze.grid[y][x] == 1 else Qt.white
                painter.fillRect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size + 1, cell_size + 1, color)

        # 绘制起点和终点
        painter.fillRect(offset_x + 1 * cell_size, offset_y + 1 * cell_size, cell_size, cell_size, Qt.blue) # 起点
        painter.fillRect(offset_x + (self.maze.width-2) * cell_size, offset_y + (self.maze.height-2) * cell_size, cell_size, cell_size, Qt.red) # 终点

        # 绘制寻路过程（尝试过的位置）
        if self.show_solution and self.maze.explored_nodes:
            painter.setBrush(QColor(0, 191, 255)) # 亮蓝色 (DeepSkyBlue)，更加鲜艳
            painter.setPen(Qt.NoPen)
            for ex, ey in self.maze.explored_nodes:
                # 绘制稍微小一点的方块以区分路径
                painter.drawRect(offset_x + ex * cell_size + cell_size/4, offset_y + ey * cell_size + cell_size/4, cell_size/2, cell_size/2)

        # 绘制寻路路径
        if self.show_solution and self.maze.path:
            painter.setBrush(QColor(255, 100, 0)) # 鲜艳的橙色，更加醒目
            painter.setPen(Qt.NoPen) # 去掉边框让路径看起来更连贯
            for px, py in self.maze.path:
                painter.drawRect(offset_x + px * cell_size + cell_size/4, offset_y + py * cell_size + cell_size/4, cell_size/2, cell_size/2)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maze Solver - PySide6")
        self.resize(800, 850) # 设置一个默认的、更接近正方形的初始尺寸
        
        # 布局
        main_layout = QVBoxLayout()
        
        # 控制面板
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("宽度 (奇数):"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(5, 99)
        self.width_spin.setSingleStep(2)
        self.width_spin.setValue(51)
        self.width_spin.valueChanged.connect(self.generate_new_maze)
        control_layout.addWidget(self.width_spin)
        
        control_layout.addWidget(QLabel("高度 (奇数):"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(5, 99)
        self.height_spin.setSingleStep(2)
        self.height_spin.setValue(51)
        self.height_spin.valueChanged.connect(self.generate_new_maze)
        control_layout.addWidget(self.height_spin)
        
        control_layout.addWidget(QLabel("生成算法:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["DFS", "Prim", "Kruskal", "Wilson"])
        self.algo_combo.currentTextChanged.connect(self.generate_new_maze)
        control_layout.addWidget(self.algo_combo)
        
        control_layout.addWidget(QLabel("寻路算法:"))
        self.solve_combo = QComboBox()
        self.solve_combo.addItems(["DFS", "A-Star"])
        self.solve_combo.currentTextChanged.connect(self.update_solution)
        control_layout.addWidget(self.solve_combo)
        
        self.break_walls_cb = QCheckBox("允许环路 (随机拆墙)")
        self.break_walls_cb.stateChanged.connect(self.generate_new_maze)
        control_layout.addWidget(self.break_walls_cb)
        
        self.gen_btn = QPushButton("生成迷宫")
        self.gen_btn.clicked.connect(self.generate_new_maze)
        control_layout.addWidget(self.gen_btn)
        
        main_layout.addLayout(control_layout)
        
        # 迷宫显示区域
        self.maze = None
        self.maze_view = MazeWidget(None)
        main_layout.addWidget(self.maze_view, 1) # 设置 stretch 为 1，使其占据剩余空间
        
        # 底部控制区 (按钮 + 颜色图例)
        bottom_layout = QHBoxLayout()
        
        self.solve_btn = QPushButton("显示/隐藏 路径")
        self.solve_btn.setMinimumWidth(120) # 防止按钮过窄
        self.solve_btn.clicked.connect(self.toggle_solution)
        bottom_layout.addWidget(self.solve_btn)
        
        bottom_layout.addStretch()
        
        def add_legend_item(color, text, is_path=False):
            item_layout = QHBoxLayout()
            item_layout.setSpacing(5)
            color_label = QLabel()
            color_label.setFixedSize(12, 12)
            if is_path:
                color_label.setStyleSheet(f"background-color: {color}; margin: 2px; border-radius: 2px;")
            else:
                color_label.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
            item_layout.addWidget(color_label)
            item_layout.addWidget(QLabel(text))
            bottom_layout.addLayout(item_layout)
            bottom_layout.addSpacing(15)

        add_legend_item("blue", "起点")
        add_legend_item("red", "终点")
        add_legend_item("#00BFFF", "尝试", is_path=True)
        add_legend_item("#FF6400", "路径", is_path=True)
        
        main_layout.addLayout(bottom_layout)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # 状态栏
        self.statusBar().showMessage("准备就绪")
        
        # 初始生成
        self.generate_new_maze()

    def generate_new_maze(self):
        w = self.width_spin.value()
        h = self.height_spin.value()
        
        # 即使输入偶数，MazeSolver 内部也会处理，
        # 但我们这里主动同步下 UI 并提醒用户
        adjusted = False
        if w % 2 == 0:
            w += 1
            self.width_spin.setValue(w)
            adjusted = True
        if h % 2 == 0:
            h += 1
            self.height_spin.setValue(h)
            adjusted = True
            
        if adjusted:
            self.statusBar().showMessage("已自动将尺寸调整为奇数以获得最佳迷宫效果", 3000)
        else:
            self.statusBar().showMessage(f"迷宫生成成功: {w}x{h}", 2000)

        gen_algo = self.algo_combo.currentText()
        solve_algo = self.solve_combo.currentText()
        
        self.maze = MazeSolver(w, h, gen_algo)
        
        if self.break_walls_cb.isChecked():
            self.maze.break_walls()
            
        self.update_solution() # 同时也进行寻路
        
        self.maze_view.set_maze(self.maze)
        self.maze_view.update()

    def update_solution(self):
        if self.maze:
            solve_algo = self.solve_combo.currentText()
            self.maze.solve((1, 1), (self.maze.width - 2, self.maze.height - 2), solve_algo)
            self.maze_view.update()

    def toggle_solution(self):
        self.maze_view.show_solution = not self.maze_view.show_solution
        if self.maze_view.show_solution:
            self.update_solution()
        self.maze_view.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())