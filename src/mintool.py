import os
import tkinter as tk
from tkinter import ttk


app = tk.Tk()
app.title('测试')
fr = tk.Frame(app, width=200, height=200)
fr.pack()


"""
    一、右键的菜单功能
"""


def cut(editor):
    editor.event_generate("<<Cut>>")


def copy(editor):
    editor.event_generate("<<Copy>>")


def paste(editor):
    editor.event_generate('<<Paste>>')


def rightKey(widget, event, editor):
    """功能：cut copy paste"""
    menubar = tk.Menu(widget, tearoff=False)  # 创建一个菜单
    menubar.delete(0, tk.END)
    menubar.add_command(label='剪切', command=lambda: cut(editor))
    menubar.add_command(label='复制', command=lambda: copy(editor))
    menubar.add_command(label='粘贴', command=lambda: paste(editor))
    menubar.post(event.x_root, event.y_root)


def menuRK(root, widget):
    """部件添加右键功能"""
    widget.bind("<Button-3>", lambda x: rightKey(root, x, widget))


# e = tk.Entry(fr)
# e.pack()
# # menuRK(fr, e)
# menuRK(app, e)


"""
    二、添加下拉列表
"""


def getValue(widget, *args):
    """可增加代码"""
    print(widget.get())
    # print(v.get())


def spinner(widget):
    """窗口添加下拉列表"""
    v = tk.StringVar()
    sp = ttk.Combobox(widget, textvariable=v)
    sp["values"] = ("1", "2", "3", "4")
    sp.current(0)          # 设置默认值
    sp.bind("<<ComboboxSelected>>", lambda x: getValue(sp))
    sp.pack()


spinner(fr)


"""
    三、添加回车功能
"""


def enter(widget):
    """部件添加回车功能"""
    widget.bind("<Return>", lambda x: getValue(widget))


v = tk.StringVar()
entry = tk.Entry(fr, textvariable=v)
entry.pack()
enter(entry)
# menuRK(fr, entry)


"""
    四、添加左键功能
"""
spin = ttk.Combobox(fr)
spin["values"] = ("1", "2", "3", "4")
spin.bind("<Button-1>", lambda x: getValue(spin))
spin.pack()


app.mainloop()
pass
