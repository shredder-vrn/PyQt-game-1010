import random
import sys
from enum import Enum
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGridLayout, QMessageBox, QFrame, QDialog,
                             QSpinBox, QColorDialog, QFormLayout, QCheckBox, QComboBox)
from PyQt5.QtCore import (Qt, QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
                          QSequentialAnimationGroup, QTimer, QPoint)
from PyQt5.QtGui import (QColor, QPainter, QBrush, QFont, QIcon, QPalette, QPen,
                         QRadialGradient, QLinearGradient, QCursor)


class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2

    @staticmethod
    def get_state_name(state):
        return "Игра" if state == GameState.PLAYING else "Конец игры"


class Game:
    # Классовые константы
    BASE_SCORE_PER_BLOCK = 10
    BONUS_MULTIPLIER = 5

    @classmethod
    def get_default_settings(cls):
        return {
            'size': 10,
            'uniform_color': False,
            'block_color': (100, 200, 150)
        }

    def __init__(self, size=None, uniform_color=None, block_color=None):
        settings = self.get_default_settings()
        self._size = size if size is not None else settings['size']
        self._uniform_color = uniform_color if uniform_color is not None else settings['uniform_color']
        self._block_color = block_color or settings['block_color']
        self.reset_game()

    def reset_game(self):
        self._board = [[0 for _ in range(self._size)] for _ in range(self._size)]
        self._colors = [[None for _ in range(self._size)] for _ in range(self._size)]
        self._score = 0
        self._state = GameState.PLAYING
        self._pieces = []
        self._piece_colors = []
        self._generate_pieces_set()

    @property
    def size(self):
        return self._size

    @property
    def board(self):
        return self._board

    @property
    def colors(self):
        return self._colors

    @property
    def score(self):
        return self._score

    @property
    def state(self):
        return self._state

    @property
    def pieces(self):
        return self._pieces

    @property
    def piece_colors(self):
        return self._piece_colors

    @staticmethod
    def get_all_shapes():
        return [
            [[1]], [[1, 1]], [[1, 1, 1]], [[1, 1], [1, 1]],
            [[1, 1, 1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1, 0], [0, 1, 1]],
            [[1, 1, 1], [0, 1, 0]], [[1, 1, 1, 1, 1]], [[1], [1], [1], [1], [1]],
            [[1, 0], [1, 1], [0, 1]], [[1, 1, 1], [0, 1, 0], [0, 1, 0]],
            [[1, 1, 1, 1], [0, 0, 0, 1]], [[1, 1, 1], [1, 0, 1]],
            [[1, 1], [1, 0], [1, 1]], [[1, 0, 1], [1, 1, 1]],
            [[1, 1, 1, 1, 1, 1]], [[1], [1], [1], [1], [1], [1]],
            [[1, 1, 1], [1, 1, 1]], [[1, 1], [1, 1], [1, 1]]
        ]

    def _generate_pieces_set(self):
        self._pieces = []
        self._piece_colors = []

        for _ in range(3):  # Всегда 3 фигуры в наборе
            shape = random.choice(self.get_all_shapes())
            # Случайный поворот/отражение
            for _ in range(random.randint(0, 3)):
                shape = [list(row) for row in zip(*shape[::-1])]
            self._pieces.append(shape)
            self._piece_colors.append(
                self._block_color if self._uniform_color else self._random_color()
            )

    @staticmethod
    def _random_color():
        return (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )

    def can_place_piece(self, piece_index, row, col):
        if piece_index < 0 or piece_index >= len(self._pieces):
            return False

        piece = self._pieces[piece_index]
        piece_height = len(piece)
        piece_width = len(piece[0]) if piece_height > 0 else 0

        if (row < 0 or col < 0 or
                row + piece_height > self._size or
                col + piece_width > self._size):
            return False

        for r in range(piece_height):
            for c in range(piece_width):
                if piece[r][c] and self._board[row + r][col + c]:
                    return False
        return True

    def place_piece(self, piece_index, row, col):
        if not self.can_place_piece(piece_index, row, col):
            return False

        piece = self._pieces[piece_index]
        color = self._piece_colors[piece_index]

        blocks_placed = sum(sum(row) for row in piece)
        self._score += blocks_placed * self.BASE_SCORE_PER_BLOCK

        for r in range(len(piece)):
            for c in range(len(piece[r])):
                if piece[r][c]:
                    self._board[row + r][col + c] = 1
                    self._colors[row + r][col + c] = color

        self._pieces.pop(piece_index)
        self._piece_colors.pop(piece_index)

        lines_cleared = self._check_lines()
        if lines_cleared > 0:
            self._score += lines_cleared * self._size * self.BONUS_MULTIPLIER

        if not self._pieces:
            self._generate_pieces_set()

        if not self._has_available_moves():
            self._state = GameState.GAME_OVER

        return True

    def _check_lines(self):
        lines_cleared = 0

        rows_to_clear = [r for r in range(self._size) if all(self._board[r])]
        cols_to_clear = [c for c in range(self._size)
                         if all(self._board[row][c] for row in range(self._size))]

        for r in rows_to_clear:
            self._board[r] = [0] * self._size
            self._colors[r] = [None] * self._size

        for c in cols_to_clear:
            for row in range(self._size):
                self._board[row][c] = 0
                self._colors[row][c] = None

        return len(rows_to_clear) + len(cols_to_clear)

    def _has_available_moves(self):
        for piece_index, piece in enumerate(self._pieces):
            for r in range(self._size):
                for c in range(self._size):
                    if self.can_place_piece(piece_index, r, c):
                        return True
        return False


class SettingsDialog(QDialog):
    @staticmethod
    def get_default_color():
        return QColor(100, 200, 150)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки игры")
        self.setFixedSize(350, 250)
        self.selected_color = self.get_default_color()
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout()

        # Размер сетки
        self.size_spin = QSpinBox()
        self.size_spin.setRange(5, 15)
        self.size_spin.setValue(10)
        layout.addRow("Размер сетки:", self.size_spin)

        # Цвет блоков
        self.uniform_color_check = QCheckBox("Одинаковый цвет блоков")
        layout.addRow(self.uniform_color_check)

        self.color_btn = QPushButton("Выбрать цвет блока")
        self.color_btn.clicked.connect(self._choose_color)
        self._update_color_button()
        layout.addRow("Цвет блока:", self.color_btn)

        # Тема приложения
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Тёмная", "dark")
        self.theme_combo.addItem("Светлая", "light")
        layout.addRow("Тема приложения:", self.theme_combo)

        # Кнопки OK/Отмена
        buttons = QHBoxLayout()
        ok_btn = QPushButton("ОК")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)

        layout.addRow(buttons)
        self.setLayout(layout)

    def _choose_color(self):
        color = QColorDialog.getColor(self.selected_color, self)
        if color.isValid():
            self.selected_color = color
            self._update_color_button()

    def _update_color_button(self):
        self.color_btn.setStyleSheet(
            f"background-color: {self.selected_color.name()};"
            "border: 1px solid #777;"
            "padding: 5px;"
        )


class BlockWidget(QWidget):
    BLOCK_SIZE = 35
    GLOW_DURATION = 800

    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(self.BLOCK_SIZE, self.BLOCK_SIZE)
        self.scale = 1.0
        self.opacity = 1.0
        self.rotation = 0
        self.shake_offset = 0
        self.glow = 0
        self.last_placed = False
        self._setup_animations()

    def _setup_animations(self):
        self.pulse_anim = QPropertyAnimation(self, b"glow")
        self.pulse_anim.setDuration(self.GLOW_DURATION)
        self.pulse_anim.setLoopCount(-1)
        self.pulse_anim.setKeyValueAt(0, 0.3)
        self.pulse_anim.setKeyValueAt(0.5, 1.0)
        self.pulse_anim.setKeyValueAt(1, 0.3)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.color:
            r, g, b = self.color
            if self.last_placed or self.glow > 0:
                grad = QRadialGradient(17, 17, 20)
                glow_color = QColor(255, 100, 100, int(200 * self.glow))
                grad.setColorAt(0, glow_color)
                grad.setColorAt(0.7, QColor(r, g, b))
                grad.setColorAt(1, QColor(r, g, b).darker(150))
                painter.setBrush(QBrush(grad))
            else:
                painter.setBrush(QBrush(QColor(r, g, b)))

            painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
            painter.save()
            painter.translate(17, 17)
            painter.rotate(self.rotation)
            painter.scale(self.scale, self.scale)
            painter.translate(-17, -17)
            painter.drawRoundedRect(2, 2, 31, 31, 5, 5)
            painter.restore()
        else:
            painter.setBrush(QBrush(QColor(60, 60, 60)))
            painter.setPen(QPen(QColor(80, 80, 80), 1))
            painter.drawRoundedRect(2, 2, 31, 31, 5, 5)

    def animate_place(self):
        self.last_placed = True
        self.pulse_anim.start()

        group = QParallelAnimationGroup()

        scale_anim = QPropertyAnimation(self, b"scale")
        scale_anim.setDuration(400)
        scale_anim.setStartValue(0.3)
        scale_anim.setEndValue(1.0)
        scale_anim.setEasingCurve(QEasingCurve.OutBack)
        group.addAnimation(scale_anim)

        rotate_anim = QPropertyAnimation(self, b"rotation")
        rotate_anim.setDuration(600)
        rotate_anim.setStartValue(-180)
        rotate_anim.setEndValue(0)
        rotate_anim.setEasingCurve(QEasingCurve.OutElastic)
        group.addAnimation(rotate_anim)

        glow_anim = QPropertyAnimation(self, b"glow")
        glow_anim.setDuration(self.GLOW_DURATION)
        glow_anim.setStartValue(1.0)
        glow_anim.setEndValue(0.0)
        glow_anim.setEasingCurve(QEasingCurve.OutCubic)
        group.addAnimation(glow_anim)

        group.start()
        QTimer.singleShot(1500, lambda: setattr(self, 'last_placed', False))

    def animate_clear(self):
        group = QParallelAnimationGroup()

        shake = QPropertyAnimation(self, b"shake_offset")
        shake.setDuration(500)
        shake.setKeyValueAt(0, 0)
        shake.setKeyValueAt(0.1, -5)
        shake.setKeyValueAt(0.2, 5)
        shake.setKeyValueAt(0.3, -5)
        shake.setKeyValueAt(0.4, 5)
        shake.setKeyValueAt(0.5, 0)
        group.addAnimation(shake)

        fade = QPropertyAnimation(self, b"opacity")
        fade.setDuration(500)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        group.addAnimation(fade)

        scale = QPropertyAnimation(self, b"scale")
        scale.setDuration(500)
        scale.setStartValue(1.0)
        scale.setEndValue(0.5)
        group.addAnimation(scale)

        group.start()


class DraggablePieceWidget(QWidget):
    PIECE_SIZE = 130
    HOVER_SCALE = 1.1
    HOVER_BOUNCE_HEIGHT = -8
    PULSE_DURATION = 1200

    def __init__(self, piece, color, parent=None):
        super().__init__(parent)
        self.piece = piece
        self.color = color
        self.selected = False
        self.hovered = False
        self.dragging = False
        self.drag_offset = QPoint(0, 0)
        self.setFixedSize(self.PIECE_SIZE, self.PIECE_SIZE)
        self.scale = 1.0
        self.y_offset = 0
        self.glow = 0
        self._setup_animations()

    def _setup_animations(self):
        self.pulse_anim = QPropertyAnimation(self, b"glow")
        self.pulse_anim.setDuration(self.PULSE_DURATION)
        self.pulse_anim.setLoopCount(-1)
        self.pulse_anim.setKeyValueAt(0, 0.3)
        self.pulse_anim.setKeyValueAt(0.5, 1.0)
        self.pulse_anim.setKeyValueAt(1, 0.3)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.hovered and not self.dragging:
            painter.setBrush(QBrush(QColor(80, 80, 80, 100)))
            painter.setPen(QPen(QColor(200, 200, 200, 150), 2))
            painter.drawRoundedRect(2, 2, 126, 126, 10, 10)

        if self.selected and not self.dragging:
            glow_width = 4 + 3 * self.glow
            glow_alpha = 100 + int(155 * self.glow)
            pen = QPen(QColor(255, 50, 50, glow_alpha), glow_width)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(2, 2, 126, 126, 10, 10)

        if not self.piece or self.dragging:
            return

        rows = len(self.piece)
        cols = max(len(row) for row in self.piece) if rows > 0 else 0
        cell_size = min(30, 110 / max(cols, 1), 110 / max(rows, 1))

        x_offset = (self.width() - cols * cell_size) / 2
        y_offset = (self.height() - rows * cell_size) / 2 + self.y_offset

        for r in range(rows):
            for c in range(len(self.piece[r])):
                if self.piece[r][c]:
                    x = x_offset + c * cell_size
                    y = y_offset + r * cell_size
                    size = cell_size - 4

                    grad = QRadialGradient(x + size / 2, y + size / 2, size / 2)
                    if self.glow > 0.1:
                        grad.setColorAt(0, QColor(255, 150, 150))
                        grad.setColorAt(0.7, QColor(*self.color))
                    else:
                        grad.setColorAt(0, QColor(*self.color))
                    grad.setColorAt(1, QColor(*self.color).darker(150))

                    painter.setBrush(QBrush(grad))
                    painter.setPen(QPen(QColor(0, 0, 0, 120), 1))
                    painter.drawRoundedRect(int(x), int(y), int(size), int(size), 5, 5)

    def paintDraggedPiece(self, painter, pos):
        rows = len(self.piece)
        cols = max(len(row) for row in self.piece) if rows > 0 else 0
        cell_size = 30

        for r in range(rows):
            for c in range(len(self.piece[r])):
                if self.piece[r][c]:
                    x = pos.x() + c * cell_size - self.drag_offset.x()
                    y = pos.y() + r * cell_size - self.drag_offset.y()
                    size = cell_size - 4

                    grad = QRadialGradient(x + size / 2, y + size / 2, size / 2)
                    grad.setColorAt(0, QColor(*self.color))
                    grad.setColorAt(1, QColor(*self.color).darker(150))

                    painter.setBrush(QBrush(grad))
                    painter.setPen(QPen(QColor(0, 0, 0, 120), 1))
                    painter.drawRoundedRect(int(x), int(y), int(size), int(size), 5, 5)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_offset = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            self.update()

    def mouseMoveEvent(self, event):
        if self.dragging:
            main_window = self.window()
            if hasattr(main_window, 'dragged_piece_pos'):
                main_window.dragged_piece_pos = event.globalPos()
                main_window.dragged_piece = self
                main_window.update()

    def mouseReleaseEvent(self, event):
        if self.dragging and event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)

            main_window = self.window()
            if hasattr(main_window, 'dragged_piece'):
                main_window.handle_piece_drop(event.globalPos())
                main_window.dragged_piece = None
                main_window.update()

    def enterEvent(self, event):
        self.hovered = True
        self.animate_hover()
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.animate_unhover()
        self.update()

    def animate_hover(self):
        if self.dragging:
            return

        group = QParallelAnimationGroup()

        scale = QPropertyAnimation(self, b"scale")
        scale.setDuration(200)
        scale.setStartValue(1.0)
        scale.setEndValue(self.HOVER_SCALE)
        scale.setEasingCurve(QEasingCurve.OutBack)
        group.addAnimation(scale)

        bounce = QPropertyAnimation(self, b"y_offset")
        bounce.setDuration(400)
        bounce.setStartValue(0)
        bounce.setKeyValueAt(0.3, self.HOVER_BOUNCE_HEIGHT)
        bounce.setEndValue(0)
        bounce.setEasingCurve(QEasingCurve.OutBounce)
        group.addAnimation(bounce)

        group.start()

    def animate_unhover(self):
        if self.dragging:
            return

        anim = QPropertyAnimation(self, b"scale")
        anim.setDuration(200)
        anim.setStartValue(self.HOVER_SCALE)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()

    def set_selected(self, selected):
        self.selected = selected
        if selected:
            self.pulse_anim.start()
        else:
            self.pulse_anim.stop()
        self.update()


class MainWindow(QMainWindow):
    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 700

    @staticmethod
    def create_dark_palette():
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        return palette

    def __init__(self):
        super().__init__()
        self.settings = Game.get_default_settings()
        self.selected_piece = None
        self.message_animation = None
        self.dragged_piece = None
        self.dragged_piece_pos = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Блок Бласт!")
        self.setWindowIcon(QIcon("game.png"))
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        self._setup_info_panel(layout)
        self._setup_game_board(layout)
        self._setup_pieces_panel(layout)
        self._setup_buttons_panel(layout)

        self.init_game()
        self.update_game_state()

    def _setup_info_panel(self, layout):
        info_panel = QFrame()
        info_panel.setFrameShape(QFrame.StyledPanel)
        info_layout = QHBoxLayout()

        self.score_label = QLabel("Очки: 0")
        self.score_label.setFont(QFont("Arial", 14, QFont.Bold))
        info_layout.addWidget(self.score_label)

        self.status_label = QLabel(GameState.get_state_name(GameState.PLAYING))
        self.status_label.setFont(QFont("Arial", 12))
        info_layout.addWidget(self.status_label)

        info_panel.setLayout(info_layout)
        layout.addWidget(info_panel)

    def _setup_game_board(self, layout):
        self.board_grid = QGridLayout()
        self.board_grid.setSpacing(2)
        layout.addLayout(self.board_grid)

    def _setup_pieces_panel(self, layout):
        pieces_panel = QFrame()
        pieces_panel.setFrameShape(QFrame.StyledPanel)
        self.pieces_layout = QHBoxLayout()
        self.pieces_layout.setAlignment(Qt.AlignCenter)
        pieces_panel.setLayout(self.pieces_layout)
        layout.addWidget(pieces_panel)

    def _setup_buttons_panel(self, layout):
        buttons_panel = QFrame()
        buttons_panel.setFrameShape(QFrame.StyledPanel)
        buttons_layout = QHBoxLayout()

        buttons = [
            ("Новая игра", self.new_game),
            ("Настройки", self.show_settings),
            ("Правила", self.show_rules),
            ("О программе", self.show_about)
        ]

        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            buttons_layout.addWidget(btn)

        buttons_panel.setLayout(buttons_layout)
        layout.addWidget(buttons_panel)

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.dragged_piece and self.dragged_piece_pos:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            self.dragged_piece.paintDraggedPiece(painter, self.mapFromGlobal(self.dragged_piece_pos))

    def init_game(self):
        self.game = Game(
            size=self.settings['size'],
            uniform_color=self.settings['uniform_color'],
            block_color=self.settings['block_color']
        )

    def update_board(self):
        for i in reversed(range(self.board_grid.count())):
            self.board_grid.itemAt(i).widget().setParent(None)

        for row in range(self.game.size):
            for col in range(self.game.size):
                cell = BlockWidget(self.game.colors[row][col])
                cell.mousePressEvent = lambda e, r=row, c=col: self.board_click(r, c)
                self.board_grid.addWidget(cell, row, col)

    def update_pieces(self):
        for i in reversed(range(self.pieces_layout.count())):
            self.pieces_layout.itemAt(i).widget().setParent(None)

        for i in range(3):
            piece = self.game.pieces[i] if i < len(self.game.pieces) else []
            color = self.game.piece_colors[i] if i < len(self.game.piece_colors) else None

            piece_widget = DraggablePieceWidget(piece, color)
            piece_widget.mousePressEvent = lambda e, idx=i: self.select_piece(idx)

            if i == self.selected_piece:
                piece_widget.selected = True

            self.pieces_layout.addWidget(piece_widget)

    def select_piece(self, piece_index):
        if self.selected_piece is not None:
            prev_widget = self.pieces_layout.itemAt(self.selected_piece).widget()
            prev_widget.set_selected(False)

        if 0 <= piece_index < len(self.game.pieces):
            self.selected_piece = piece_index
            widget = self.pieces_layout.itemAt(piece_index).widget()
            widget.set_selected(True)
            widget.animate_hover()

    def handle_piece_drop(self, drop_pos):
        if not self.dragged_piece or self.selected_piece is None:
            return

        # Находим виджет клетки, на которую упала фигура
        target_widget = self.childAt(self.mapFromGlobal(drop_pos))

        # Если упали не на клетку, просто сбрасываем выделение
        if not target_widget or not isinstance(target_widget, BlockWidget):
            self.selected_piece = None
            return

        # Находим позицию клетки в grid layout
        index = self.board_grid.indexOf(target_widget)
        if index == -1:
            return

        row, col, _, _ = self.board_grid.getItemPosition(index)

        # Пытаемся разместить фигуру
        if self.game.place_piece(self.selected_piece, row, col):
            piece = self.game.pieces[self.selected_piece] if self.selected_piece < len(self.game.pieces) else []

            for r in range(row, row + len(piece)):
                for c in range(col, col + len(piece[0])):
                    if (r < self.game.size and c < self.game.size and
                            self.game.board[r][c] and
                            (r - row) < len(piece) and
                            (c - col) < len(piece[0]) and
                            piece[r - row][c - col]):
                        widget = self.board_grid.itemAtPosition(r, c).widget()
                        widget.animate_place()

            piece_widget = self.pieces_layout.itemAt(self.selected_piece).widget()
            self.animate_piece_removal(piece_widget)

            self.selected_piece = None
            self.update_game_state()

    def board_click(self, row, col):
        if self.selected_piece is None:
            return

        if self.game.place_piece(self.selected_piece, row, col):
            piece = self.game.pieces[self.selected_piece] if self.selected_piece < len(self.game.pieces) else []

            for r in range(row, row + len(piece)):
                for c in range(col, col + len(piece[0])):
                    if (r < self.game.size and c < self.game.size and
                            self.game.board[r][c] and
                            (r - row) < len(piece) and
                            (c - col) < len(piece[0]) and
                            piece[r - row][c - col]):
                        widget = self.board_grid.itemAtPosition(r, c).widget()
                        widget.animate_place()

            piece_widget = self.pieces_layout.itemAt(self.selected_piece).widget()
            self.animate_piece_removal(piece_widget)

            self.selected_piece = None
            self.update_game_state()

    def animate_piece_removal(self, widget):
        anim = QPropertyAnimation(widget, b"scale")
        anim.setDuration(300)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InBack)
        anim.start()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_1, Qt.Key_2, Qt.Key_3):
            piece_index = event.key() - Qt.Key_1
            self.select_piece(piece_index)
        else:
            super().keyPressEvent(event)

    def update_game_state(self):
        self.score_label.setText(f"Очки: {self.game.score}")
        self.status_label.setText(GameState.get_state_name(self.game.state))

        self.animate_score_update()
        self.update_board()
        self.update_pieces()

        if self.game.state == GameState.GAME_OVER:
            self.show_game_over_message()

    def animate_score_update(self):
        if hasattr(self, 'score_animation'):
            self.score_animation.stop()

        self.score_animation = QSequentialAnimationGroup()

        scale_up = QPropertyAnimation(self.score_label, b"font")
        scale_up.setDuration(150)
        scale_up.setStartValue(QFont("Arial", 14, QFont.Bold))
        scale_up.setEndValue(QFont("Arial", 18, QFont.Bold))

        scale_down = QPropertyAnimation(self.score_label, b"font")
        scale_down.setDuration(150)
        scale_down.setStartValue(QFont("Arial", 18, QFont.Bold))
        scale_down.setEndValue(QFont("Arial", 14, QFont.Bold))

        self.score_animation.addAnimation(scale_up)
        self.score_animation.addAnimation(scale_down)
        self.score_animation.start()

    def show_game_over_message(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Конец игры")
        msg_box.setText(f"Игра окончена!\nВаш результат: {self.game.score}")
        msg_box.setStandardButtons(QMessageBox.Ok)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #333;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 16px;
            }
            QPushButton {
                background-color: #555;
                color: white;
                border: 1px solid #777;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)

        self.message_animation = QPropertyAnimation(msg_box, b"windowOpacity")
        self.message_animation.setDuration(500)
        self.message_animation.setStartValue(0.0)
        self.message_animation.setEndValue(1.0)
        self.message_animation.setEasingCurve(QEasingCurve.InOutQuad)

        msg_box.show()
        self.message_animation.start()

    def new_game(self):
        self.init_game()
        self.selected_piece = None
        self.update_game_state()

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.size_spin.setValue(self.settings['size'])
        dialog.uniform_color_check.setChecked(self.settings['uniform_color'])
        dialog.color_btn.setStyleSheet(
            f"background-color: rgb{self.settings['block_color']}")

        # Устанавливаем текущую тему в комбобокс
        current_theme = "dark" if self.palette().color(QPalette.Window).lightness() < 128 else "light"
        dialog.theme_combo.setCurrentIndex(dialog.theme_combo.findData(current_theme))

        if dialog.exec_() == QDialog.Accepted:
            self.settings['size'] = dialog.size_spin.value()
            self.settings['uniform_color'] = dialog.uniform_color_check.isChecked()
            self.settings['block_color'] = (
                dialog.selected_color.red(),
                dialog.selected_color.green(),
                dialog.selected_color.blue()
            )

            # Применяем выбранную тему
            self.apply_theme(dialog.theme_combo.currentData())
            self.new_game()

    def apply_theme(self, theme_name):
        """Применяет выбранную тему к приложению"""
        palette = QPalette()

        if theme_name == "dark":
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
            palette.setColor(QPalette.HighlightedText, Qt.black)
        else:  # light theme
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.black)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(100, 149, 237))
            palette.setColor(QPalette.HighlightedText, Qt.white)

        self.setPalette(palette)

        # Обновляем стиль кнопок и других элементов
        self.style().unpolish(self)
        self.style().polish(self)

        # Сохраняем текущую тему в настройках
        self.settings['theme'] = theme_name

    def show_rules(self):
        QMessageBox.information(self, "Правила игры", """
        <h2>Правила игры «Блок Бласт!»</h2>
        <p>1. Выберите фигуру снизу (щелчком мыши или клавишей 1-3)</p>
        <p>2. Разместите её на поле (щелчком или перетаскиванием)</p>
        <p>3. Если строка или столбец заполнены — они очищаются</p>
        <p>4. Получайте очки за размещение блоков</p>
        <p>5. Бонусные очки — за очищенные линии</p>
        <p>6. Игра заканчивается, когда нет возможных ходов</p>
        <p><b>Управление:</b></p>
        <ul>
            <li>Щелкните по фигуре или нажмите 1-3 для выбора</li>
            <li>Щелкните по полю или перетащите фигуру для размещения</li>
        </ul>
        """)

    def show_about(self):
        QMessageBox.information(self, "О программе", """
        <h2>Блок Бласт!</h2>
        <p>Автор: Паша :)</p>
        <p>Email: p_shcherbatov@mail.ru</p>
        <p>Telegram: @Shredder_vrn</p>
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Используем Fusion стиль для лучшего отображения тем

    window = MainWindow()

    # Применяем тему по умолчанию (темную)
    window.apply_theme("dark")

    window.show()
    sys.exit(app.exec_())