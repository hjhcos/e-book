"""
应用实现功能：
1、实现根据目录获取章节内容
2、实现左键文本框隐藏组件
3、实现打开文件显示在文本框里面
4、实现保存单个文件在文本框里面的内容
5、实现搜索框搜索书籍并显示第一节内容
"""
import os
import config
import access
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog as fd

log = config.Log()
logger = log.getLog()

cf = config.Config("config.cfg")
admin = cf.get()[0]
user = cf.get()[1]


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


def clearContent(widget):
    """清除文本内容"""
    widget.config(state=tk.NORMAL)
    widget.delete('1.0', 'end')
    widget.config(state=tk.DISABLED)


def writeContent(widget, content):
    """写入内容"""
    widget.config(state=tk.NORMAL)
    if isinstance(content, str):
        widget.insert(tk.INSERT, content)
    else:
        for co in content:
            widget.insert(tk.INSERT, co)
    widget.config(state=tk.DISABLED)


def openBox(widget):
    """打开文件返回内容"""
    try:
        filename = fd.askopenfilename()
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.readlines()
        clearContent(widget)
        writeContent(widget, content)
    except Exception as e:
        logger.info("openBox()")
        logger.warning(e)


def saveFile(widget):
    """保存内容"""
    try:
        filename = os.path.join('..\\temp', widget.get("1.0"))
        with open(filename+'.txt', 'w', encoding='utf-8') as file:
            file.write(widget.get("1.0", "end"))
    except Exception as e:
        logger.info("saveFile()")
        logger.warning(e)


def setUrlId(widget):
    """更新url_id"""
    url_id = widget.get()
    cf.updata("admin", "url_id", url_id)
    cf.save()


def updataDir(widget01, widget02):
    """更新目录"""
    try:
        widget01.pack()
        widget02.pack_forget()
        widget01['value'] = ["第"+str(serial)+"章" for serial, chapters_name in enumerate(cf.get(user, "chapters_name"))]
    except Exception as e:
        logger.info("updataDir()")
        logger.warning(e)


def changeContent(widget01, widget02):
    """目录链接并更新内容"""
    try:
        chapter_id = int(widget01.get()[1:-1])
        cf.updata(user, "chapter_id", chapter_id)
        cf.save()
        chapter_link = cf.get(user, "chapters_link")[chapter_id]
        clearContent(widget02)
        writeContent(widget02, access.extractContent(chapter_link))
    except Exception as e:
        logger.info("changeContent()")
        logger.warning(e)


def hide(widgets):
    """隐藏组件"""
    try:
        if isinstance(widgets, tuple):
            for widget in widgets:
                widget.pack_forget()
        else:
            widgets.pack_forget()
    except Exception as e:
        logger.info("hide()")
        logger.warning(e)


def display(widgets):
    """显示组件"""
    try:
        if isinstance(widgets, tuple):
            for widget in widgets:
                widget.pack()
        else:
            widgets.pack()
    except Exception as e:
        logger.info("display()")
        logger.warning(e)


def searchBox(widget01, widget02):
    """搜索框的显示以及目录的隐藏"""
    hide(widget02)
    display(widget01)


def searchContent(widget01, widget02, url_id):
    """搜索书籍并显示第一章内容"""
    book_name = widget01.get()
    chapter_id = 0
    book_link = access.bdExtractLink(book_name, url_id.get())
    chapters_list = access.extractChapters(book_link, url_id.get())
    print(chapters_list)
    clearContent(widget02)
    writeContent(widget02, access.extractContent(chapters_list[chapter_id][1]))
    cf.updata(user, "book_name", book_name)
    cf.updata(user, "chapter_id", chapter_id)
    cf.updata(admin, "url_id", url_id.get())
    cf.updata(user, "chapters_link", [link[1] for link in chapters_list])
    cf.updata(user, "chapters_name", [name[0] for name in chapters_list])
    cf.save()


class APP(object):

    def __init__(self, title, win_size="800x600"):
        """初始文件"""
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(win_size)
        # self.root.iconbitmap(".\\my.ico")

    def load(self):
        self.root.update()
        self.root.deiconify()

    def run(self):
        """窗口运行显示"""
        self.root.resizable(0, 0)       # 固定大小
        self.root.mainloop()

    def menuBar(self):
        """菜单栏"""
        self.main_menu = tk.Menu(self.root)
        # 文件(完成)
        file_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label='文件', menu=file_menu)
        file_menu.add_command(label='打开', command=lambda: openBox(self.text))
        file_menu.add_command(label='保存', command=lambda: saveFile(self.text))

        # 编辑(未完成)
        edit_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label='编辑', menu=edit_menu)

        # 网址(完成)
        url_menu = tk.Menu(self.main_menu, tearoff=False)
        url_choice = tk.IntVar()
        self.main_menu.add_cascade(label='网址', menu=url_menu)
        url_choice.set(cf.get(admin, "url_id"))
        url_menu.add_radiobutton(label='www.shizongzui.cc', variable=url_choice, value=0,
                                 command=lambda: setUrlId(url_choice))
        url_menu.add_radiobutton(label='www.luoxia.com', variable=url_choice, value=1,
                                 command=lambda: setUrlId(url_choice))
        url_menu.add_radiobutton(label='www.99csw.com', variable=url_choice, value=2,
                                 command=lambda: setUrlId(url_choice))

        # 目录(完成)
        self.spinter = ttk.Combobox(self.root)
        self.main_menu.add_command(label='目录', command=lambda: updataDir(self.spinter, self.entry))
        self.spinter.bind("<Return>", lambda x: changeContent(self.spinter, self.text))

        # 搜索(完成 百度老是拒绝访问, 已解决)
        self.entry = tk.Entry(self.root)
        self.main_menu.add_command(label='搜索', command=lambda: searchBox(self.entry, self.spinter))
        self.entry.bind("<Return>", lambda x: searchContent(self.entry, self.text, url_choice))

        # 下载(未完成)
        self.main_menu.add_command(label='下载', )

        self.root.config(menu=self.main_menu)
        pass

    def contentBox(self):
        """显示文本内容 初始显示内容(未完成)"""

        self.font = font.Font(family='楷体', size=15)
        self.text = tk.Text(self.root, font=self.font)
        self.text.pack(fill="both", padx=20, pady=20, expand=True)
        wg = (self.spinter, self.entry)
        self.text.bind("<Button-1>", lambda x: hide(wg))
        self.text.bind("<Button-3>", lambda x: menuRK(self.root, self.text))
        chapter_id = cf.get(user, "chapter_id")
        # writeContent(self.text, )
        # self.text.insert(tk.INSERT, )

        self.text.config(state=tk.DISABLED)


def main():
    reader = APP('智能爬取电子书')
    reader.menuBar()
    reader.contentBox()
    reader.run()


if __name__ == '__main__':

    main()
