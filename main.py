import tkinter as tk
from tkinter import ttk


class ReversiGUI(tk.Tk):
    COLORS = {
        '.': {"bg": "white", "fg": "black", "text": "."},
        'B': {"bg": "black", "fg": "white", "text": "B"},
        'W': {"bg": "#e4e4e4", "fg": "black", "text": "W"},
        # 合法手ハイライト（Black / White で色分け）
        'HB': {"bg": "#90ee90", "fg": "black", "text": "."},  # Black用：薄い緑
        'HW': {"bg": "#add8e6", "fg": "black", "text": "."},  # White用：薄い水色
    }

    def __init__(self):
        super().__init__()
        self.title("Reversi Move Counter")
        self.resizable(False, False)

        self.size_var = tk.IntVar(value=8)
        self.board = []
        self.cell_buttons = []

        self._build_controls()
        self._build_board()
        self._update_board_size()

    def _build_controls(self):
        control_frame = ttk.Frame(self, padding=10)
        control_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(control_frame, text="Board size (4-30):").grid(row=0, column=0, sticky="w")
        size_spin = ttk.Spinbox(
            control_frame,
            from_=4,
            to=30,
            width=5,
            textvariable=self.size_var,
            command=self._update_board_size
        )
        size_spin.grid(row=0, column=1, padx=(5, 10))

        ttk.Button(control_frame, text="Reset", command=self._update_board_size).grid(row=0, column=2, padx=5)

        # 黒／白の合法手カウントボタン
        ttk.Button(
            control_frame,
            text="Black moves",
            command=lambda: self._count_moves('B')
        ).grid(row=0, column=3, padx=5)

        ttk.Button(
            control_frame,
            text="White moves",
            command=lambda: self._count_moves('W')
        ).grid(row=0, column=4, padx=5)

        # 結果ラベル
        self.black_result_label = ttk.Label(control_frame, text="Black can play: 0")
        self.black_result_label.grid(row=0, column=5, padx=(10, 0))

        self.white_result_label = ttk.Label(control_frame, text="White can play: 0")
        self.white_result_label.grid(row=0, column=6, padx=(10, 0))

        info = "Click a cell to toggle between empty (.), black (B), and white (W)."
        ttk.Label(control_frame, text=info).grid(
            row=1, column=0, columnspan=7, pady=(8, 0), sticky="w"
        )

    def _build_board(self):
        self.board_frame = ttk.Frame(self, padding=10)
        self.board_frame.grid(row=1, column=0)

    def _update_board_size(self):
        size = max(4, min(30, self.size_var.get()))
        self.size_var.set(size)

        self.board = [['.' for _ in range(size)] for _ in range(size)]
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.cell_buttons = []

        for r in range(size):
            row_buttons = []
            for c in range(size):
                button = tk.Button(
                    self.board_frame,
                    width=2,
                    height=1,
                    command=lambda r=r, c=c: self._cycle_cell(r, c),
                    relief=tk.RIDGE,
                )
                button.grid(row=r, column=c, padx=1, pady=1)
                row_buttons.append(button)
            self.cell_buttons.append(row_buttons)

        self._refresh_board()
        self.black_result_label.config(text="Black can play: 0")
        self.white_result_label.config(text="White can play: 0")

    def _cycle_cell(self, r, c):
        current = self.board[r][c]
        next_value = {'.': 'B', 'B': 'W', 'W': '.'}[current]
        self.board[r][c] = next_value
        self._refresh_cell(r, c)

    def _refresh_board(self):
        size = len(self.board)
        for r in range(size):
            for c in range(size):
                self._refresh_cell(r, c)

    def _refresh_cell(self, r, c):
        value = self.board[r][c]
        style = self.COLORS[value]
        button = self.cell_buttons[r][c]
        button.configure(text=style["text"], bg=style["bg"], fg=style["fg"])

    def _clear_highlights(self):
        """以前のハイライト（合法手）を消す"""
        highlight_bgs = {
            self.COLORS['HB']["bg"],
            self.COLORS['HW']["bg"],
        }
        for r in range(len(self.board)):
            for c in range(len(self.board)):
                btn = self.cell_buttons[r][c]
                if btn["bg"] in highlight_bgs:
                    self._refresh_cell(r, c)

    def _count_moves(self, player):
        """player: 'B' or 'W' の合法手を数えてハイライト"""
        self._clear_highlights()

        count = 0
        size = len(self.board)

        # プレイヤーごとにハイライト色を切り替え
        highlight_style = self.COLORS['HB'] if player == 'B' else self.COLORS['HW']

        for r in range(size):
            for c in range(size):
                if self._can_place(r, c, player):
                    count += 1
                    btn = self.cell_buttons[r][c]
                    btn.configure(
                        bg=highlight_style["bg"],
                        fg=highlight_style["fg"],
                        text=highlight_style["text"],
                    )

        if player == 'B':
            self.black_result_label.config(text=f"Black can play: {count}")
        else:
            self.white_result_label.config(text=f"White can play: {count}")

    def _can_place(self, r, c, player):
        """player が (r, c) に打てるかどうか判定"""
        if self.board[r][c] != '.':
            return False

        opponent = 'W' if player == 'B' else 'B'

        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ]

        def in_board(row, col):
            size = len(self.board)
            return 0 <= row < size and 0 <= col < size

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            # 隣が相手石でないとこの方向はダメ
            if not in_board(nr, nc) or self.board[nr][nc] != opponent:
                continue

            # 相手石を1個以上はさんで自分の石があればOK
            while True:
                nr += dr
                nc += dc
                if not in_board(nr, nc):
                    break
                if self.board[nr][nc] == '.':
                    break
                if self.board[nr][nc] == player:
                    return True

        return False


def main():
    app = ReversiGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
