import io
import re
import time
import math
import contextlib
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from code_generator import generate_intermediate_code

from lexer import tokenize
from parser import syntax_check
from semantic import semantic_check
from python_generator import generate_python_code

# ==========================================
# COLOR PALETTES
# ==========================================

BLUE = "#38BDF8"
BLUE_DARK = "#0284C7"
VIOLET = "#A855F7"
PINK = "#EC4899"
GREEN = "#10B981"
RED = "#F43F5E"
AMBER = "#FBBF24"

DARK = {
    "BG": "#070B14",
    "SURFACE": "#0E1525",
    "CARD": "#141E33",
    "ELEVATED": "#1B2842",
    "EDITOR": "#080D18",
    "GUTTER": "#0B1221",
    "BORDER": "#233252",
    "WHITE": "#F8FAFC",
    "GRAY": "#94A3B8",
    "TEXT": "#E2E8F0",
    "OUTPUT": "#34D399",
    "TAB": "#141E33",
    "KW": "#38BDF8",
    "STR": "#FBBF24",
    "NUM": "#C084FC",
    "CMT": "#64748B",
    "LINE_HL": "#121D33",
    "STAGE_FLOOR": "#162238"
}

LIGHT = {
    "BG": "#E9EFF8",
    "SURFACE": "#FFFFFF",
    "CARD": "#F8FAFC",
    "ELEVATED": "#EEF2F7",
    "EDITOR": "#F8FAFC",
    "GUTTER": "#E2E8F0",
    "BORDER": "#CBD5E1",
    "WHITE": "#0F172A",
    "GRAY": "#475569",
    "TEXT": "#1E293B",
    "OUTPUT": "#059669",
    "TAB": "#E2E8F0",
    "KW": "#0284C7",
    "STR": "#B45309",
    "NUM": "#7E22CE",
    "CMT": "#64748B",
    "LINE_HL": "#E2E8F0",
    "STAGE_FLOOR": "#DCE6F5"
}

dark_mode = True
fun_mode = True
colors = DARK.copy()

KEYWORDS = {
    "agar", "warna", "khatam", "lo", "dikhao", "jama",
    "karo", "ko", "aur", "number", "text", "print",
    "se", "ho", "bara", "chota", "barabar", "jabtak"
}

# ==========================================
# ROUNDED CARD HELPER (CANVAS)
# ==========================================

def draw_rounded_rect(canvas, x1, y1, x2, y2, r=16, **kwargs):
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class RoundedCard(tk.Canvas):
    """Sleek rounded container card using Canvas."""

    def __init__(self, parent, radius=16, bg_color="#141E33", border_color="#233252", **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, bg=parent["bg"], **kwargs)
        self.radius = radius
        self.bg_color = bg_color
        self.border_color = border_color
        self.inner = tk.Frame(self, bg=bg_color)
        self.win_id = self.create_window(0, 0, window=self.inner, anchor="nw")
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        w = max(self.winfo_width(), 20)
        h = max(self.winfo_height(), 20)
        self.delete("card_bg")
        draw_rounded_rect(
            self,
            1,
            1,
            w - 1,
            h - 1,
            r=self.radius,
            fill=self.bg_color,
            outline=self.border_color,
            width=1.5,
            tags="card_bg"
        )
        self.tag_lower("card_bg")
        pad = 2
        self.coords(self.win_id, pad, pad)
        self.itemconfigure(self.win_id, width=max(w - pad * 2, 10), height=max(h - pad * 2, 10))

    def set_palette(self, bg_color, border_color, parent_bg):
        self.configure(bg=parent_bg)
        self.bg_color = bg_color
        self.border_color = border_color
        self.inner.configure(bg=bg_color)
        self._redraw()

# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()
root.title("ROMANADE STUDIO  ✦  Roman Urdu Compiler")
root.geometry("1380x890")
root.minsize(1100, 740)
root.configure(bg=colors["BG"])

# ==========================================
# TOP HERO HEADER
# ==========================================

header_wrap = tk.Frame(root, bg=colors["BG"])
header_wrap.pack(fill="x", padx=20, pady=(14, 8))

header_card = RoundedCard(header_wrap, radius=18, bg_color=colors["SURFACE"], border_color=colors["BORDER"], height=78)
header_card.pack(fill="x")
header_card.pack_propagate(False)

h_inner = header_card.inner

emblem_canvas = tk.Canvas(h_inner, width=48, height=48, bg=colors["SURFACE"], highlightthickness=0)
emblem_canvas.pack(side="left", padx=(18, 12), pady=14)
draw_rounded_rect(emblem_canvas, 2, 2, 46, 46, r=13, fill=BLUE_DARK, outline=BLUE, width=2)
emblem_canvas.create_text(24, 24, text="RC", fill="white", font=("Segoe UI", 15, "bold"))

title_col = tk.Frame(h_inner, bg=colors["SURFACE"])
title_col.pack(side="left", pady=12)

top_line = tk.Frame(title_col, bg=colors["SURFACE"])
top_line.pack(anchor="w")

brand_lbl = tk.Label(
    top_line,
    text="ROMANADE",
    font=("Segoe UI", 18, "bold"),
    bg=colors["SURFACE"],
    fg=colors["WHITE"]
)
brand_lbl.pack(side="left")

chip_lbl = tk.Label(
    top_line,
    text="  ✦ ANIMATED COMPILER IDE  ",
    font=("Segoe UI", 8, "bold"),
    bg=VIOLET,
    fg="white",
    pady=2
)
chip_lbl.pack(side="left", padx=(10, 0), pady=(3, 0))

tagline_lbl = tk.Label(
    title_col,
    text="Roman Urdu Commands → Lexical • Syntax • Semantic • Intermediate Code • Python",
    font=("Segoe UI", 9),
    bg=colors["SURFACE"],
    fg=colors["GRAY"]
)
tagline_lbl.pack(anchor="w", pady=(1, 0))

right_hdr = tk.Frame(h_inner, bg=colors["SURFACE"])
right_hdr.pack(side="right", padx=18)

def make_pill_btn(parent, text, cmd, bg, fg):
    return tk.Button(
        parent,
        text=text,
        command=cmd,
        bg=bg,
        fg=fg,
        activebackground=bg,
        activeforeground=fg,
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        padx=13,
        pady=7,
        cursor="hand2",
        bd=0
    )

def toggle_fun_mode():
    global fun_mode
    fun_mode = not fun_mode
    fun_btn.config(
        text="🎉 Vibe: Desi Fun" if fun_mode else "🎓 Vibe: Pro Lab",
        bg=PINK if fun_mode else colors["ELEVATED"],
        fg="white" if fun_mode else colors["WHITE"]
    )
    status_label.config(
        text="● Desi Fun Mode ON — Zara dekho token girl kya karti hai!" if fun_mode else "● Pro Lab Mode ON — Ready for compilation",
        fg=PINK if fun_mode else BLUE
    )

fun_btn = make_pill_btn(right_hdr, "🎉 Vibe: Desi Fun", toggle_fun_mode, PINK, "white")
fun_btn.pack(side="left", padx=(0, 8))

theme_btn = make_pill_btn(right_hdr, "☀ Light", lambda: toggle_theme(), colors["ELEVATED"], colors["WHITE"])
theme_btn.pack(side="left")

# ==========================================
# LIVE PIPELINE + TELEMETRY STRIP
# ==========================================

pipe_wrap = tk.Frame(root, bg=colors["BG"])
pipe_wrap.pack(fill="x", padx=20, pady=(0, 8))

pipe_card = RoundedCard(pipe_wrap, radius=15, bg_color=colors["SURFACE"], border_color=colors["BORDER"], height=48)
pipe_card.pack(fill="x")
pipe_card.pack_propagate(False)

p_inner = pipe_card.inner

tk.Label(
    p_inner,
    text="FLOW",
    font=("Segoe UI", 8, "bold"),
    bg=colors["SURFACE"],
    fg=colors["GRAY"]
).pack(side="left", padx=(16, 10))

STAGES = [
    ("01", "Lexical"),
    ("02", "Syntax"),
    ("03", "Semantic"),
    ("04", "TAC"),
    ("05", "Python")
]

stage_pills = []
stage_connectors = []

for idx, (num, label) in enumerate(STAGES):
    pill = tk.Label(
        p_inner,
        text=f" {num} · {label} ",
        font=("Segoe UI", 9, "bold"),
        bg=colors["ELEVATED"],
        fg=colors["GRAY"],
        pady=3
    )
    pill.pack(side="left", padx=2, pady=9)
    stage_pills.append(pill)

    if idx < len(STAGES) - 1:
        conn = tk.Label(
            p_inner,
            text="›",
            font=("Segoe UI", 12, "bold"),
            bg=colors["SURFACE"],
            fg=colors["GRAY"]
        )
        conn.pack(side="left", padx=2)
        stage_connectors.append(conn)

stats_frame = tk.Frame(p_inner, bg=colors["SURFACE"])
stats_frame.pack(side="right", padx=16)

def make_stat_badge(parent, title, val):
    box = tk.Frame(parent, bg=colors["ELEVATED"], padx=9, pady=2)
    box.pack(side="left", padx=4)
    k = tk.Label(box, text=f"{title}: ", font=("Segoe UI", 8, "bold"), bg=colors["ELEVATED"], fg=colors["GRAY"])
    k.pack(side="left")
    v = tk.Label(box, text=val, font=("Consolas", 9, "bold"), bg=colors["ELEVATED"], fg=BLUE)
    v.pack(side="left")
    return box, k, v

stat_lines_box, stat_lines_k, stat_lines_v = make_stat_badge(stats_frame, "LINES", "0")
stat_toks_box, stat_toks_k, stat_toks_v = make_stat_badge(stats_frame, "TOKENS", "0")
stat_time_box, stat_time_k, stat_time_v = make_stat_badge(stats_frame, "TIME", "0ms")

def paint_stages(mode="idle", active_idx=-1):
    for i, pill in enumerate(stage_pills):
        if mode == "idle":
            pill.config(bg=colors["ELEVATED"], fg=colors["GRAY"])
        elif mode == "step":
            if i < active_idx:
                pill.config(bg=GREEN, fg="#042F1E" if dark_mode else "white")
            elif i == active_idx:
                pill.config(bg=BLUE, fg="white")
            else:
                pill.config(bg=colors["ELEVATED"], fg=colors["GRAY"])
        elif mode == "done":
            pill.config(bg=GREEN, fg="#042F1E" if dark_mode else "white")
        elif mode == "err":
            if i < active_idx:
                pill.config(bg=GREEN, fg="#042F1E" if dark_mode else "white")
            elif i == active_idx:
                pill.config(bg=RED, fg="white")
            else:
                pill.config(bg=colors["ELEVATED"], fg=colors["GRAY"])

# ==========================================
# ACTION TOOLBAR
# ==========================================

toolbar = tk.Frame(root, bg=colors["BG"])
toolbar.pack(fill="x", padx=20, pady=(0, 8))

def make_action_btn(parent, text, cmd, bg, fg="white", hover=None):
    btn = tk.Button(
        parent,
        text=text,
        command=cmd,
        bg=bg,
        fg=fg,
        activebackground=hover or bg,
        activeforeground=fg,
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        padx=15,
        pady=7,
        cursor="hand2",
        bd=0
    )
    if hover:
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

# ==========================================
# ANIMATED TOKEN GIRL STAGE
# ==========================================

stage_wrap = tk.Frame(root, bg=colors["BG"])
stage_wrap.pack(fill="x", padx=20, pady=(0, 8))

stage_card = RoundedCard(stage_wrap, radius=16, bg_color=colors["SURFACE"], border_color=colors["BORDER"], height=122)
stage_card.pack(fill="x")
stage_card.pack_propagate(False)

stage_canvas = tk.Canvas(stage_card.inner, height=118, bg=colors["SURFACE"], highlightthickness=0, bd=0)
stage_canvas.pack(fill="both", expand=True, padx=8, pady=2)

class TokenGirlStage:
    """
    Animated cartoon girl carrying token badges along a compiler track.
    """

    def __init__(self, canvas):
        self.canvas = canvas
        self.girl_x = 95.0
        self.target_x = 95.0
        self.walk_phase = 0.0
        self.mood = "idle"  # 'idle' | 'walking' | 'parsing' | 'happy' | 'error'
        self.caption = "Hi! Main Romanade Token Girl hoon — Compile dabao!"
        self.tokens_preview = ["TOK", "KW", "ID", "NUM"]
        self.token_offset = 0.0
        self._tick_id = None
        self._start_loop()

    def set_tokens(self, tokens):
        cleaned = []
        for t in (tokens or [])[:6]:
            s = str(t).strip()
            # Short label for mini token badge
            parts = re.findall(r"[A-Za-z0-9_]+", s)
            short = parts[0][:6] if parts else "TOK"
            cleaned.append(short)
        if cleaned:
            self.tokens_preview = cleaned

    def set_state(self, mood, target_ratio=0.12, caption=None):
        self.mood = mood
        w = max(self.canvas.winfo_width(), 600)
        usable_w = max(w - 220, 200)
        self.target_x = 75 + usable_w * max(0.0, min(1.0, target_ratio))
        if caption:
            self.caption = caption

    def _start_loop(self):
        self._animate()

    def _animate(self):
        # Smooth horizontal interpolation toward target_x
        dx = self.target_x - self.girl_x
        if abs(dx) > 1.2:
            self.girl_x += dx * 0.14
            self.walk_phase += 0.38
        else:
            self.girl_x = self.target_x
            if self.mood in ("walking", "parsing"):
                self.walk_phase += 0.25
            else:
                self.walk_phase += 0.08

        self.token_offset = (self.token_offset + (2.4 if self.mood in ("walking", "parsing") else 0.7)) % 140

        self.draw()
        self._tick_id = self.canvas.after(33, self._animate)

    def draw(self):
        c = self.canvas
        c.delete("all")

        w = max(c.winfo_width(), 600)
        h = max(c.winfo_height(), 116)
        floor_y = h - 22

        # Track / ground
        c.create_rectangle(14, floor_y, w - 14, h - 6, fill=colors["STAGE_FLOOR"], outline=colors["BORDER"], width=1)

        # Floating token badges moving along track
        for i, tok_lbl in enumerate(self.tokens_preview):
            tx = 150 + i * 54 + (self.token_offset % 45) - 22
            if tx < w - 50:
                ty = floor_y - 16 - (i % 2) * 14
                badge_bg = AMBER if i % 2 == 0 else BLUE_DARK
                badge_fg = "#1E1B06" if i % 2 == 0 else "white"
                draw_rounded_rect(c, tx - 20, ty - 9, tx + 20, ty + 9, r=6, fill=badge_bg, outline="")
                c.create_text(tx, ty, text=tok_lbl[:6], fill=badge_fg, font=("Consolas", 7, "bold"))

        # Speech / status bubble above stage
        bubble_x = min(max(self.girl_x + 55, 160), w - 210)
        draw_rounded_rect(c, bubble_x - 115, 6, bubble_x + 115, 28, r=9, fill=colors["CARD"], outline=colors["BORDER"], width=1)
        c.create_text(bubble_x, 17, text=self.caption[:46], fill=colors["WHITE"], font=("Segoe UI", 8, "bold"))

        # Draw Cartoon Girl at (self.girl_x, floor_y)
        gx = self.girl_x
        bob = abs(math.sin(self.walk_phase)) * 5.0
        gy = floor_y - bob

        swing = math.sin(self.walk_phase) * 9.0

        # Ponytail / hair back
        c.create_oval(gx - 22, gy - 66, gx - 6, gy - 44, fill="#4C1D95", outline="")
        # Pink hair bow
        c.create_polygon(gx - 12, gy - 69, gx - 20, gy - 75, gx - 18, gy - 63, fill=PINK, outline="")
        c.create_polygon(gx - 12, gy - 69, gx - 4, gy - 75, gx - 6, gy - 63, fill=PINK, outline="")
        c.create_oval(gx - 15, gy - 72, gx - 9, gy - 66, fill=AMBER, outline="")

        # Legs (animated stride)
        leg_l_x = gx - 5 + swing
        leg_r_x = gx + 5 - swing
        c.create_line(gx - 4, gy - 20, leg_l_x, floor_y - 2, fill="#FDBA74", width=4, capstyle="round")
        c.create_line(gx + 4, gy - 20, leg_r_x, floor_y - 2, fill="#FDBA74", width=4, capstyle="round")
        # Cute shoes
        c.create_oval(leg_l_x - 4, floor_y - 5, leg_l_x + 5, floor_y, fill=PINK, outline="")
        c.create_oval(leg_r_x - 4, floor_y - 5, leg_r_x + 5, floor_y, fill=PINK, outline="")

        # Dress / Hoodie body
        c.create_polygon(
            gx - 11, gy - 42,
            gx + 11, gy - 42,
            gx + 15, gy - 19,
            gx - 15, gy - 19,
            fill=VIOLET,
            outline=""
        )

        # Head
        head_r = 14
        head_cy = gy - 55
        c.create_oval(gx - head_r, head_cy - head_r, gx + head_r, head_cy + head_r, fill="#FED7AA", outline="#FDBA74", width=1.5)
        # Bangs
        c.create_arc(gx - head_r, head_cy - head_r, gx + head_r, head_cy + head_r, start=10, extent=160, fill="#4C1D95", outline="")

        # Expressive eyes & mouth based on mood
        if self.mood == "error":
            # Shocked X eyes & wavy mouth
            c.create_line(gx - 7, head_cy - 2, gx - 2, head_cy + 3, fill="#0F172A", width=1.8)
            c.create_line(gx - 2, head_cy - 2, gx - 7, head_cy + 3, fill="#0F172A", width=1.8)
            c.create_line(gx + 2, head_cy - 2, gx + 7, head_cy + 3, fill="#0F172A", width=1.8)
            c.create_line(gx + 7, head_cy - 2, gx + 2, head_cy + 3, fill="#0F172A", width=1.8)
            c.create_oval(gx - 3, head_cy + 6, gx + 3, head_cy + 11, outline=RED, width=1.5)
        elif self.mood == "happy":
            # Happy ^ ^ eyes & big smile
            c.create_arc(gx - 8, head_cy - 3, gx - 2, head_cy + 3, start=0, extent=180, style="arc", outline="#0F172A", width=1.8)
            c.create_arc(gx + 2, head_cy - 3, gx + 8, head_cy + 3, start=0, extent=180, style="arc", outline="#0F172A", width=1.8)
            c.create_arc(gx - 5, head_cy + 3, gx + 5, head_cy + 9, start=180, extent=180, style="arc", outline="#0F172A", width=1.8)
            # Sparkle star
            c.create_text(gx + 22, head_cy - 10, text="✦", fill=AMBER, font=("Segoe UI", 12, "bold"))
        else:
            # Cute round eyes + rosy cheeks + smile
            c.create_oval(gx - 7, head_cy - 2, gx - 3, head_cy + 3, fill="#0F172A", outline="")
            c.create_oval(gx + 3, head_cy - 2, gx + 7, head_cy + 3, fill="#0F172A", outline="")
            c.create_oval(gx - 10, head_cy + 3, gx - 6, head_cy + 6, fill="#FDA4AF", outline="")
            c.create_oval(gx + 6, head_cy + 3, gx + 10, head_cy + 6, fill="#FDA4AF", outline="")
            c.create_arc(gx - 4, head_cy + 4, gx + 4, head_cy + 8, start=180, extent=180, style="arc", outline="#0F172A", width=1.5)

        # Arms carrying a token crate forward
        arm_lift = math.sin(self.walk_phase * 1.5) * 3
        c.create_line(gx + 6, gy - 38, gx + 20, gy - 30 + arm_lift, fill="#FED7AA", width=4, capstyle="round")

        # Token crate held by girl
        crate_x = gx + 24
        crate_y = gy - 29 + arm_lift
        draw_rounded_rect(c, crate_x - 12, crate_y - 9, crate_x + 12, crate_y + 9, r=5, fill=AMBER, outline="#D97706", width=1.5)
        c.create_text(crate_x, crate_y, text="TOK", fill="#1E1B06", font=("Consolas", 7, "bold"))

girl_stage = TokenGirlStage(stage_canvas)

# ==========================================
# MAIN SPLIT WORKSPACE
# ==========================================

workspace = tk.Frame(root, bg=colors["BG"])
workspace.pack(fill="both", expand=True, padx=20, pady=(0, 8))

workspace.grid_columnconfigure(0, weight=1, uniform="pane")
workspace.grid_columnconfigure(1, weight=1, uniform="pane")
workspace.grid_rowconfigure(0, weight=1)

# --- LEFT: SOURCE EDITOR CARD ---
left_wrap = tk.Frame(workspace, bg=colors["BG"])
left_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

editor_card = RoundedCard(left_wrap, radius=18, bg_color=colors["SURFACE"], border_color=colors["BORDER"])
editor_card.pack(fill="both", expand=True)

e_inner = editor_card.inner

e_top = tk.Frame(e_inner, bg=colors["SURFACE"])
e_top.pack(fill="x", padx=16, pady=(12, 8))

e_title = tk.Label(
    e_top,
    text="✎  ROMAN URDU EDITOR",
    font=("Segoe UI", 11, "bold"),
    bg=colors["SURFACE"],
    fg=colors["WHITE"]
)
e_title.pack(side="left")

cursor_lbl = tk.Label(
    e_top,
    text="Ln 1, Col 1",
    font=("Consolas", 9),
    bg=colors["SURFACE"],
    fg=colors["GRAY"]
)
cursor_lbl.pack(side="right")

code_shell = tk.Frame(e_inner, bg=colors["EDITOR"], padx=2, pady=2)
code_shell.pack(fill="both", expand=True, padx=14, pady=(0, 14))

gutter = tk.Text(
    code_shell,
    width=4,
    padx=8,
    pady=14,
    font=("Consolas", 12),
    bg=colors["GUTTER"],
    fg=colors["GRAY"],
    state="disabled",
    relief="flat",
    takefocus=0,
    cursor="arrow"
)
gutter.pack(side="left", fill="y")

code_area = tk.Text(
    code_shell,
    font=("Consolas", 13),
    bg=colors["EDITOR"],
    fg=colors["TEXT"],
    insertbackground=AMBER,
    selectbackground=BLUE_DARK,
    selectforeground="white",
    relief="flat",
    wrap="none",
    padx=14,
    pady=14,
    undo=True
)
code_area.pack(side="left", fill="both", expand=True)

y_bar = tk.Scrollbar(code_shell, orient="vertical")
y_bar.pack(side="right", fill="y")

x_bar = tk.Scrollbar(e_inner, orient="horizontal", command=code_area.xview)
x_bar.pack(fill="x", padx=14, pady=(0, 12))
code_area.config(xscrollcommand=x_bar.set)

def sync_y(*args):
    code_area.yview(*args)
    gutter.yview(*args)

def on_code_y(*args):
    y_bar.set(*args)
    gutter.yview_moveto(args[0])

y_bar.config(command=sync_y)
code_area.config(yscrollcommand=on_code_y)

def refresh_editor_visuals(event=None):
    raw = code_area.get("1.0", "end-1c")
    lines = raw.splitlines()
    n_lines = max(len(lines), 1)
    stat_lines_v.config(text=str(n_lines))

    gutter.config(state="normal")
    gutter.delete("1.0", tk.END)
    gutter.insert("1.0", "\n".join(str(i) for i in range(1, n_lines + 1)))
    gutter.config(state="disabled")
    gutter.yview_moveto(code_area.yview()[0])

    try:
        idx = code_area.index(tk.INSERT)
        ln, col = idx.split(".")
        cursor_lbl.config(text=f"Ln {ln}, Col {int(col) + 1}")
    except Exception:
        pass

    for tag in ("kw", "str", "num", "cmt", "cur_line"):
        code_area.tag_remove(tag, "1.0", tk.END)

    try:
        cur_ln = code_area.index(tk.INSERT).split(".")[0]
        code_area.tag_add("cur_line", f"{cur_ln}.0", f"{cur_ln}.end+1c")
    except Exception:
        pass

    for m in re.finditer(r"#[^\n]*", raw):
        code_area.tag_add("cmt", f"1.0 + {m.start()} chars", f"1.0 + {m.end()} chars")

    for m in re.finditer(r'"[^"\n]*"|\'[^\'\n]*\'', raw):
        code_area.tag_add("str", f"1.0 + {m.start()} chars", f"1.0 + {m.end()} chars")

    for m in re.finditer(r"\b\d+(?:\.\d+)?\b", raw):
        code_area.tag_add("num", f"1.0 + {m.start()} chars", f"1.0 + {m.end()} chars")

    for m in re.finditer(r"\b[A-Za-z_]\w*\b", raw):
        if m.group(0).lower() in KEYWORDS:
            code_area.tag_add("kw", f"1.0 + {m.start()} chars", f"1.0 + {m.end()} chars")

    code_area.tag_config("cur_line", background=colors["LINE_HL"])
    code_area.tag_config("kw", foreground=colors["KW"], font=("Consolas", 13, "bold"))
    code_area.tag_config("str", foreground=colors["STR"])
    code_area.tag_config("num", foreground=colors["NUM"])
    code_area.tag_config("cmt", foreground=colors["CMT"])

code_area.bind("<KeyRelease>", refresh_editor_visuals)
code_area.bind("<ButtonRelease-1>", refresh_editor_visuals)
code_area.bind("<<Modified>>", lambda e: (code_area.edit_modified(False), refresh_editor_visuals()))

# --- RIGHT: COMPILER PHASES & OUTPUT CARD ---
right_wrap = tk.Frame(workspace, bg=colors["BG"])
right_wrap.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

output_card = RoundedCard(right_wrap, radius=18, bg_color=colors["SURFACE"], border_color=colors["BORDER"])
output_card.pack(fill="both", expand=True)

o_inner = output_card.inner

o_top = tk.Frame(o_inner, bg=colors["SURFACE"])
o_top.pack(fill="x", padx=16, pady=(12, 8))

o_title = tk.Label(
    o_top,
    text="⚙  COMPILER PHASES",
    font=("Segoe UI", 11, "bold"),
    bg=colors["SURFACE"],
    fg=colors["WHITE"]
)
o_title.pack(side="left")

result_pill = tk.Label(
    o_top,
    text=" ● STANDBY ",
    font=("Segoe UI", 8, "bold"),
    bg=colors["ELEVATED"],
    fg=colors["GRAY"],
    pady=3
)
result_pill.pack(side="right")

style = ttk.Style()
style.theme_use("clam")
style.configure("Studio.TNotebook", background=colors["SURFACE"], borderwidth=0)
style.configure(
    "Studio.TNotebook.Tab",
    background=colors["TAB"],
    foreground=colors["WHITE"],
    padding=(12, 9),
    font=("Segoe UI", 9, "bold")
)
style.map(
    "Studio.TNotebook.Tab",
    background=[("selected", BLUE_DARK)],
    foreground=[("selected", "white")]
)

notebook = ttk.Notebook(o_inner, style="Studio.TNotebook")
notebook.pack(fill="both", expand=True, padx=14, pady=(0, 8))

phase_boxes = []
phase_frames = []

def add_phase_tab(title):
    fr = tk.Frame(notebook, bg=colors["EDITOR"])
    notebook.add(fr, text=title)
    txt = scrolledtext.ScrolledText(
        fr,
        font=("Consolas", 11),
        bg=colors["EDITOR"],
        fg=colors["OUTPUT"],
        insertbackground=colors["WHITE"],
        relief="flat",
        wrap="none",
        padx=14,
        pady=14
    )
    txt.pack(fill="both", expand=True)
    phase_boxes.append(txt)
    phase_frames.append(fr)
    return txt

lex_box = add_phase_tab("Lexical")
syn_box = add_phase_tab("Syntax")
sem_box = add_phase_tab("Semantic")
tac_box = add_phase_tab("Intermediate")
py_box = add_phase_tab("Python Out")

out_bar = tk.Frame(o_inner, bg=colors["SURFACE"])
out_bar.pack(fill="x", padx=14, pady=(0, 14))

def copy_py():
    src = py_box.get("1.0", tk.END).strip()
    if not src:
        messagebox.showinfo("Empty", "Pehle code compile karein taake Python code ban sake!")
        return
    root.clipboard_clear()
    root.clipboard_append(src)
    girl_stage.set_state("happy", target_ratio=0.92, caption="Python code clipboard mein copy ho gaya!")
    status_label.config(
        text="● Copied! Ab kahin bhi paste kar lo!" if fun_mode else "● Generated Python code copied to clipboard",
        fg=GREEN
    )

def open_console_modal(title, body_text):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("520x340")
    win.configure(bg=colors["SURFACE"])
    win.transient(root)

    tk.Label(
        win,
        text="▶ PYTHON EXECUTION CONSOLE",
        font=("Segoe UI", 11, "bold"),
        bg=colors["SURFACE"],
        fg=GREEN
    ).pack(anchor="w", padx=18, pady=(14, 6))

    box = tk.Text(
        win,
        font=("Consolas", 11),
        bg=colors["EDITOR"],
        fg=colors["OUTPUT"],
        relief="flat",
        padx=14,
        pady=14
    )
    box.pack(fill="both", expand=True, padx=18, pady=(0, 14))
    box.insert("1.0", body_text)
    box.config(state="disabled")

def run_py():
    src = py_box.get("1.0", tk.END).strip()
    if not src:
        messagebox.showwarning("No Output", "Pehle Romanade code compile karein!")
        return

    if "input(" in src:
        msg = (
            "Is code mein user input (input()) shamil hai.\n"
            "Live interactive input ke liye 'Copy Python' daba kar terminal/IDE mein run karein."
        )
        messagebox.showinfo("Interactive Input", msg)
        return

    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(src, {})
        out_str = buf.getvalue().strip() or "[Executed cleanly — no print output]"
        girl_stage.set_state("happy", target_ratio=0.95, caption="Output ready! Dekho console mein!")
        open_console_modal("Romanade Runner", out_str)
    except Exception as ex:
        girl_stage.set_state("error", target_ratio=0.75, caption="Runtime error aa gaya!")
        open_console_modal("Runtime Error", f"Error:\n{ex}")

copy_button = make_action_btn(out_bar, "⧉ Copy Python", copy_py, colors["ELEVATED"], colors["WHITE"], colors["BORDER"])
copy_button.pack(side="left")

run_button = make_action_btn(out_bar, "⚡ Run Python", run_py, GREEN, "#042F1E", "#34D399")
run_button.pack(side="left", padx=8)

# ==========================================
# STATUS FOOTER
# ==========================================

status_wrap = tk.Frame(root, bg=colors["BG"])
status_wrap.pack(fill="x", padx=20, pady=(0, 12))

status_card = RoundedCard(status_wrap, radius=14, bg_color=colors["SURFACE"], border_color=colors["BORDER"], height=40)
status_card.pack(fill="x")
status_card.pack_propagate(False)

s_inner = status_card.inner

status_label = tk.Label(
    s_inner,
    text="● Desi Fun Mode ON — Ready to compile! (Ctrl+Enter)" if fun_mode else "● Ready  |  Press Ctrl+Enter to Compile",
    font=("Segoe UI", 9, "bold"),
    bg=colors["SURFACE"],
    fg=PINK if fun_mode else colors["GRAY"]
)
status_label.pack(side="left", padx=16, pady=9)

ver_label = tk.Label(
    s_inner,
    text="ROMANADE STUDIO  •  BSCS COMPILER",
    font=("Segoe UI", 8, "bold"),
    bg=colors["SURFACE"],
    fg=colors["GRAY"]
)
ver_label.pack(side="right", padx=16)

# ==========================================
# COMPILATION ENGINE (INSTANT + STEP ANIMATED)
# ==========================================

_anim_job = None

def _cancel_anim():
    global _anim_job
    if _anim_job is not None:
        root.after_cancel(_anim_job)
        _anim_job = None

STAGE_CAPTIONS = [
    ("walking", 0.22, "Tokens collect kar rahi hoon..."),
    ("parsing", 0.52, "Parser gate mein grammar check!"),
    ("parsing", 0.68, "Symbol table & types check..."),
    ("walking", 0.82, "Intermediate TAC bana rahi hoon..."),
    ("happy", 0.94, "Wah! Python code bilkul tayyar hai!")
]

def compile_code(animated=False):
    _cancel_anim()
    code = code_area.get("1.0", tk.END).strip()

    if not code:
        girl_stage.set_state("error", target_ratio=0.15, caption="Editor khali hai! Kuch likho na...")
        messagebox.showwarning(
            "Empty Code",
            "Editor khali hai! Koi Roman Urdu code likhein ya Example load karein." if fun_mode else "Please enter Romanade source code first."
        )
        return

    for b in phase_boxes:
        b.delete("1.0", tk.END)

    paint_stages("idle")
    girl_stage.set_state("walking", target_ratio=0.18, caption="Kaam shuru! Tokens utha rahi hoon...")
    t0 = time.perf_counter()
    stage_idx = 0

    try:
        # Phase 1: Lexical
        stage_idx = 0
        tokens = tokenize(code)
        girl_stage.set_tokens(tokens)
        stat_toks_v.config(text=str(len(tokens)))
        for i, tok in enumerate(tokens, 1):
            lex_box.insert(tk.END, f"{i:02d}  │  {tok}\n")

        # Phase 2: Syntax
        stage_idx = 1
        syn_res = syntax_check(code)
        syn_box.insert(tk.END, "STATUS : VALID GRAMMAR\n" + "─" * 34 + f"\n\n{syn_res}\n")

        # Phase 3: Semantic
        stage_idx = 2
        sym_tab = semantic_check(code)
        if sym_tab:
            sem_box.insert(tk.END, f"{'IDENTIFIER':<18} {'DATA TYPE':<12}\n" + "─" * 32 + "\n")
            for var, dtype in sym_tab.items():
                sem_box.insert(tk.END, f"{var:<18} {dtype:<12}\n")
        else:
            sem_box.insert(tk.END, "Symbol table is empty (no variables declared).\n")

        # Phase 4: Intermediate Code
        stage_idx = 3
        tac = generate_intermediate_code(code)
        if isinstance(tac, str):
            tac_box.insert(tk.END, tac + "\n")
        else:
            for i, inst in enumerate(tac, 1):
                tac_box.insert(tk.END, f"t{i:02d}:  {inst}\n")

        # Phase 5: Python Code
        stage_idx = 4
        py_out = generate_python_code(code)
        py_box.insert(tk.END, py_out + "\n")

        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        stat_time_v.config(text=f"{max(elapsed_ms, 1)}ms")

        def finish_success():
            paint_stages("done")
            girl_stage.set_state("happy", target_ratio=0.94, caption="Zabardast! Sab 5 phases pass!")
            result_pill.config(text=" ● PASSED ", bg=GREEN, fg="#042F1E")
            status_label.config(
                text=f"● Zabardast! 5/5 phases paas ho gaye ({max(elapsed_ms, 1)} ms)!" if fun_mode
                else f"● Compilation successful in {max(elapsed_ms, 1)} ms",
                fg=GREEN
            )
            notebook.select(4)

        if animated:
            def step_tick(k):
                global _anim_job
                if k < len(STAGES):
                    paint_stages("step", active_idx=k)
                    notebook.select(k)
                    mood_k, ratio_k, cap_k = STAGE_CAPTIONS[k]
                    girl_stage.set_state(mood_k, target_ratio=ratio_k, caption=cap_k)
                    result_pill.config(text=f" ● PHASE {k + 1}/5 ", bg=BLUE, fg="white")
                    _anim_job = root.after(420, lambda: step_tick(k + 1))
                else:
                    finish_success()

            step_tick(0)
        else:
            finish_success()

    except Exception as err:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        stat_time_v.config(text=f"{max(elapsed_ms, 1)}ms")
        paint_stages("err", active_idx=stage_idx)
        err_ratio = 0.25 + stage_idx * 0.14
        girl_stage.set_state("error", target_ratio=min(err_ratio, 0.85), caption=f"Oops! {STAGES[stage_idx][1]} mein error!")
        result_pill.config(text=" ● ERROR ", bg=RED, fg="white")

        phase_boxes[stage_idx].insert(tk.END, f"✖ Error in {STAGES[stage_idx][1]} Phase:\n\n{err}\n")
        notebook.select(stage_idx)

        status_label.config(
            text=f"● Arre! {STAGES[stage_idx][1]} mein garbar aayi hai: {err}" if fun_mode
            else f"● Failed at {STAGES[stage_idx][1]}: {err}",
            fg=RED
        )
        messagebox.showerror("Compiler Error", str(err))

def clear_all():
    _cancel_anim()
    code_area.delete("1.0", tk.END)
    for b in phase_boxes:
        b.delete("1.0", tk.END)
    paint_stages("idle")
    girl_stage.set_state("idle", target_ratio=0.10, caption="Naya code likho, main ready hoon!")
    stat_toks_v.config(text="0")
    stat_time_v.config(text="0ms")
    result_pill.config(text=" ● STANDBY ", bg=colors["ELEVATED"], fg=colors["GRAY"])
    refresh_editor_visuals()
    status_label.config(
        text="● Editor saaf! Naya Roman Urdu code likhein!" if fun_mode else "● Ready",
        fg=PINK if fun_mode else colors["GRAY"]
    )

# ==========================================
# EXAMPLES PICKER MODAL
# ==========================================

def open_examples():
    samples = {
        "1. Jama Karo (Addition)": """age lo
age2 lo
age aur age2 ko jama karo
jawab dikhao""",

        "2. Agar / Warna / Khatam": """marks = 88
agar marks 50 se bara ho
"Mubarak! Pass ho gaye" dikhao
warna
"Mehnat aur karo" dikhao
khatam""",

        "3. Text Input": """text lo naam
naam dikhao""",

        "4. Old Number Syntax": """number lo num
print karo num""",

        "5. Direct Math": """a = 15
b = 25
answer = a + b
print karo answer""",

        "6. String Variable": """city = "Khairpur"
print karo city"""
    }

    win = tk.Toplevel(root)
    win.title("Romanade Samples")
    win.geometry("540x480")
    win.configure(bg=colors["SURFACE"])
    win.resizable(False, False)
    win.transient(root)

    tk.Label(
        win,
        text="✦ PICK A SAMPLE PROGRAM",
        font=("Segoe UI", 15, "bold"),
        bg=colors["SURFACE"],
        fg=colors["WHITE"]
    ).pack(pady=(20, 4))

    tk.Label(
        win,
        text="Double-click karein ya Load dabayein",
        font=("Segoe UI", 9),
        bg=colors["SURFACE"],
        fg=colors["GRAY"]
    ).pack(pady=(0, 12))

    lb = tk.Listbox(
        win,
        font=("Segoe UI", 11),
        bg=colors["EDITOR"],
        fg=colors["TEXT"],
        selectbackground=BLUE_DARK,
        selectforeground="white",
        relief="flat",
        activestyle="none"
    )
    lb.pack(fill="both", expand=True, padx=22, pady=6)

    for k in samples:
        lb.insert(tk.END, k)

    def apply_sample():
        sel = lb.curselection()
        if not sel:
            return
        name = lb.get(sel[0])
        _cancel_anim()
        code_area.delete("1.0", tk.END)
        code_area.insert("1.0", samples[name])
        for b in phase_boxes:
            b.delete("1.0", tk.END)
        paint_stages("idle")
        girl_stage.set_state("walking", target_ratio=0.16, caption=f"{name} load ho gaya!")
        stat_toks_v.config(text="0")
        stat_time_v.config(text="0ms")
        result_pill.config(text=" ● STANDBY ", bg=colors["ELEVATED"], fg=colors["GRAY"])
        refresh_editor_visuals()
        status_label.config(text=f"● Loaded: {name}", fg=BLUE)
        win.destroy()

    make_action_btn(win, "LOAD INTO EDITOR", apply_sample, BLUE_DARK, "white", BLUE).pack(pady=16)
    lb.bind("<Double-Button-1>", lambda e: apply_sample())

# ==========================================
# THEME SWITCHER
# ==========================================

def toggle_theme():
    global dark_mode, colors
    dark_mode = not dark_mode
    colors = DARK.copy() if dark_mode else LIGHT.copy()

    root.configure(bg=colors["BG"])
    header_wrap.configure(bg=colors["BG"])
    pipe_wrap.configure(bg=colors["BG"])
    toolbar.configure(bg=colors["BG"])
    stage_wrap.configure(bg=colors["BG"])
    workspace.configure(bg=colors["BG"])
    left_wrap.configure(bg=colors["BG"])
    right_wrap.configure(bg=colors["BG"])
    status_wrap.configure(bg=colors["BG"])

    header_card.set_palette(colors["SURFACE"], colors["BORDER"], colors["BG"])
    pipe_card.set_palette(colors["SURFACE"], colors["BORDER"], colors["BG"])
    stage_card.set_palette(colors["SURFACE"], colors["BORDER"], colors["BG"])
    editor_card.set_palette(colors["SURFACE"], colors["BORDER"], colors["BG"])
    output_card.set_palette(colors["SURFACE"], colors["BORDER"], colors["BG"])
    status_card.set_palette(colors["SURFACE"], colors["BORDER"], colors["BG"])

    stage_canvas.configure(bg=colors["SURFACE"])
    emblem_canvas.configure(bg=colors["SURFACE"])
    title_col.configure(bg=colors["SURFACE"])
    top_line.configure(bg=colors["SURFACE"])
    brand_lbl.configure(bg=colors["SURFACE"], fg=colors["WHITE"])
    tagline_lbl.configure(bg=colors["SURFACE"], fg=colors["GRAY"])
    right_hdr.configure(bg=colors["SURFACE"])

    p_inner.configure(bg=colors["SURFACE"])
    for c in stage_connectors:
        c.configure(bg=colors["SURFACE"], fg=colors["GRAY"])
    stats_frame.configure(bg=colors["SURFACE"])
    for box, k, v in (
        (stat_lines_box, stat_lines_k, stat_lines_v),
        (stat_toks_box, stat_toks_k, stat_toks_v),
        (stat_time_box, stat_time_k, stat_time_v),
    ):
        box.configure(bg=colors["ELEVATED"])
        k.configure(bg=colors["ELEVATED"], fg=colors["GRAY"])
        v.configure(bg=colors["ELEVATED"], fg=BLUE)

    e_top.configure(bg=colors["SURFACE"])
    e_title.configure(bg=colors["SURFACE"], fg=colors["WHITE"])
    cursor_lbl.configure(bg=colors["SURFACE"], fg=colors["GRAY"])
    e_inner.configure(bg=colors["SURFACE"])
    code_shell.configure(bg=colors["EDITOR"])
    gutter.configure(bg=colors["GUTTER"], fg=colors["GRAY"])
    code_area.configure(bg=colors["EDITOR"], fg=colors["TEXT"], selectbackground=BLUE_DARK)

    o_top.configure(bg=colors["SURFACE"])
    o_title.configure(bg=colors["SURFACE"], fg=colors["WHITE"])
    o_inner.configure(bg=colors["SURFACE"])
    out_bar.configure(bg=colors["SURFACE"])
    copy_button.configure(bg=colors["ELEVATED"], fg=colors["WHITE"])

    for fr in phase_frames:
        fr.configure(bg=colors["EDITOR"])
    for b in phase_boxes:
        b.configure(bg=colors["EDITOR"], fg=colors["OUTPUT"], insertbackground=colors["WHITE"])

    style.configure("Studio.TNotebook", background=colors["SURFACE"])
    style.configure("Studio.TNotebook.Tab", background=colors["TAB"], foreground=colors["WHITE"])
    style.map("Studio.TNotebook.Tab", background=[("selected", BLUE_DARK)], foreground=[("selected", "white")])

    s_inner.configure(bg=colors["SURFACE"])
    status_label.configure(bg=colors["SURFACE"])
    ver_label.configure(bg=colors["SURFACE"], fg=colors["GRAY"])

    theme_btn.configure(
        text="☀ Light" if dark_mode else "☾ Dark",
        bg=colors["ELEVATED"],
        fg=colors["WHITE"]
    )
    paint_stages("idle")
    girl_stage.draw()
    refresh_editor_visuals()

# ==========================================
# TOOLBAR BUTTONS
# ==========================================

make_action_btn(toolbar, "▶  COMPILE", lambda: compile_code(animated=False), BLUE_DARK, "white", BLUE).pack(side="left", padx=(0, 8))
make_action_btn(toolbar, "✨  STEP PLAY", lambda: compile_code(animated=True), VIOLET, "white", PINK).pack(side="left", padx=(0, 8))
make_action_btn(toolbar, "＋  SAMPLES", open_examples, colors["ELEVATED"], colors["WHITE"], colors["BORDER"]).pack(side="left")
make_action_btn(toolbar, "✕  CLEAR", clear_all, "#881337", "white", RED).pack(side="right")

# ==========================================
# SHORTCUTS & STARTER CODE
# ==========================================

root.bind("<Control-Return>", lambda e: compile_code(animated=False))
root.bind("<Control-l>", lambda e: clear_all())

code_area.insert(
    "1.0",
    'marks = 88\nagar marks 50 se bara ho\n"Mubarak! Pass ho gaye" dikhao\nwarna\n"Mehnat aur karo" dikhao\nkhatam'
)
refresh_editor_visuals()

root.mainloop()


























