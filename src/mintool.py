import os
import access
from time import sleep
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from config import Config


cf = Config("config.cfg")
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
    menu_bar = tk.Menu(widget, tearoff=False)  # 创建一个菜单
    menu_bar.delete(0, tk.END)
    menu_bar.add_command(label='剪切', command=lambda: cut(editor))
    menu_bar.add_command(label='复制', command=lambda: copy(editor))
    menu_bar.add_command(label='粘贴', command=lambda: paste(editor))
    menu_bar.post(event.x_root, event.y_root)


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
    widget.yview(cf.get(user, "text_yview"))
    widget.config(state=tk.DISABLED)
    sleep(10)


def openBox(widget):
    """打开文件返回内容"""
    try:
        filename = filedialog.askopenfilename()
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.readlines()
        clearContent(widget)
        writeContent(widget, content)
    except Exception as e:
        raise ValueError(f"{__file__}:\n{e}")


def saveFile(widget):
    """保存内容"""
    try:
        file_path = filedialog.asksaveasfilename(title=u'保存文件')
        if file_path is not None:
            with open(file=file_path, mode='w', encoding='utf-8') as fd:
                fd.write(widget.get('1.0', tk.END))
    except Exception as e:
        raise FileNotFoundError(f"{__file__}:\n{e}")


def setUrlId(widget):
    """更新url_id"""
    url_id = widget.get()
    cf.updata("admin", "url_id", url_id)
    cf.save()


def hide(widgets):
    """隐藏组件"""
    try:
        if isinstance(widgets, tuple):
            for widget in widgets:
                widget.pack_forget()
        else:
            widgets.pack_forget()
    except Exception as e:
        raise ValueError(f"{__file__}:\n{e}")


def display(widgets):
    """显示组件"""
    try:
        if isinstance(widgets, tuple):
            for widget in widgets:
                widget.pack()
        else:
            widgets.pack()
    except Exception as e:
        raise ValueError(f"{__file__}:\n{e}")


def updateDir(widget01, widget02):
    """更新目录

    :param widget01: need to display of widget
    :param widget02: need to hide of widget
    :return:
    """
    try:
        display(widget01)
        hide(widget02)
        widget01['value'] = ["第"+str(serial)+"章" for serial, chapters_name in enumerate(cf.get(user, "chapters_name"))]
    except Exception as e:
        raise ValueError(f"{__file__}:\n{e}")


def changeContent(widget01, widget02):
    """目录链接并更新内容

    :param widget01: chapter's widget
    :param widget02: display content of widget
    """
    try:
        cf.updata(user, "text_yview", -1)
        chapter_id = int(widget01.get()[1:-1])
        chapter_link = cf.get(user, "chapters_link")[chapter_id]
        clearContent(widget02)
        writeContent(widget02, access.extractContent(chapter_link))
        cf.updata(user, "chapter_id", chapter_id)
        cf.save()
    except Exception as e:
        raise ValueError(f"{__file__}:\n{e}")


def searchBox(widget01, widget02):
    """搜索框的显示以及目录的隐藏

    :param widget01: need to hide of widget
    :param widget02: need to display of widget
    """
    hide(widget02)
    display(widget01)


def searchContent(widget01, widget02, url_id):
    """搜索书籍并显示第一章内容

    :param url_id:
    :param widget01: input content widget
    :param widget02: display content widget
    """
    book_name = widget01.get()
    chapter_id = 0
    book_link = access.bdExtractLink(book_name, url_id.get())
    chapters_list = access.extractChapters(book_link, url_id.get())
    clearContent(widget02)
    writeContent(widget02, access.extractContent(chapters_list[chapter_id][1]))
    cf.updata(user, "text_yview", -1)
    cf.updata(user, "book_name", book_name)
    cf.updata(user, "chapter_id", chapter_id)
    cf.updata(admin, "url_id", url_id.get())
    cf.updata(user, "chapters_link", [link[1] for link in chapters_list])
    cf.updata(user, "chapters_name", [name[0] for name in chapters_list])
    cf.updata(user, "download_id", 0)
    cf.save()


def downloadBook(widget, title="Python TK"):
    """下载书籍"""
    if messagebox.askokcancel('提示', '请确定下载'):
        sub_win = tk.Toplevel(widget)
        sub_win.title(f"{title}-> 下载")
        sub_win.geometry('420x20+100+30')
        label = tk.Label(sub_win, text='下载进度:')
        label.pack(side=tk.LEFT)
        canvas = tk.Canvas(sub_win, width=280, height=10, bg="white")
        canvas.pack(side=tk.LEFT)
        fill_line = canvas.create_rectangle(2, 2, 0, 10, fill="green")

        chapters_link = cf.get(user, "chapters_link")
        chapters_name = cf.get(user, "chapters_name")
        download_id = cf.get(user, "download_id")
        book_name = cf.get(user, "book_name")

        if len(chapters_link) != len(chapters_name):
            raise ValueError(f"The number of links({len(chapters_link)}) and chapters({len(chapters_name)}) is not equal. ")

        cha_len = len(chapters_name)

        if download_id != 0:
            sleep(0.2)
            if not messagebox.askokcancel('提示', '是否继续之前的下载'):
                download_id = 0
        n = 0
        la_con = f"第{download_id}章 {chapters_name[download_id]}"
        la = tk.Label(sub_win, text=la_con)
        la.pack()
        for download_id in range(download_id, cha_len):
            n += (280/cha_len)
            la["text"] = f"第{download_id+1}章"
            access.save(access.extractContent(chapters_link[download_id]), book_name, la["text"])
            cf.updata(user, "download_id", download_id)
            cf.save()
            canvas.coords(fill_line, (0, 0, n, 10))
            sub_win.update()
            sleep(2)
        sub_win.destroy()
        tk.messagebox.showinfo(message='下载完成!')
    else:
        sleep(0.2)
        tk.messagebox.showinfo(message='已取消下载!')

    pass


def loadContent(widget):
    """加载内容"""
    chapter_id = cf.get(user, "chapter_id")
    chapter_link = cf.get(user, "chapters_link")[chapter_id]
    writeContent(widget, access.extractContent(chapter_link))


def changeChapter(widget, *args):
    """改变章节
    """
    args = args[0]
    if not isinstance(widget, tk.Text):
        raise Exception(f"{widget} is not tkinter.Text")
    chapter_id = cf.get(user, "chapter_id")
    text_yview = cf.get(user, "text_yview")
    if args in ["Right", "Left"]:
        if "Right" == args:
            cf.updata(user, "chapter_id", chapter_id+1)
        elif "Left" == args:
            cf.updata(user, "chapter_id", chapter_id-1)
        cf.save()
        loadContent(widget)
    elif args in ["Up", "Down"]:
        print(args, text_yview)
        if "Up" == args:
            cf.updata(user, "text_yview", text_yview-1)
        elif "Down" == args:
            cf.updata(user, "text_yview", text_yview+1)
        cf.save()
    else:
        raise ValueError("not detection")


def directionKey(widget):
    """下一章 上一章

    :param widget:
    """
    widget.bind("<Right>", lambda x: changeChapter(widget, "Right"))
    widget.bind("<Left>", lambda x: changeChapter(widget, "Left"))
    widget.bind("<Up>", lambda x: changeChapter(widget, "Up"))
    widget.bind("<Down>", lambda x: changeChapter(widget, "Down"))


