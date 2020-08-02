"""
重写应用：
1、实现根据目录获取章节内容
2、实现左键文本框隐藏组件
3、实现打开文件内容显示在文本框里面
4、实现保存单个文件在文本框里面的内容
5、实现搜索框搜索书籍并显示第一节内容
6、实现启动自动加载上次的数据
7、实现左右翻页换取章节
8、实现重新加载有加载框
9、当叉掉加载框自动取消加载
"""
import ctypes
import inspect
import time
import mintool
import threading
from config import Log
import tkinter as tk
from tkinter import ttk, font, messagebox


log = Log()
logger = log.getLog()


class APP(object):

    def __init__(self, title='Python TK', win_h=600, win_w=800):
        """初始文件"""
        self.title = title
        self.root = tk.Tk()
        self.root.title(self.title)
        self.win_h, self.win_w = win_h, win_w
        x = int((self.root.winfo_screenwidth() - self.win_w) / 2)
        y = int((self.root.winfo_screenheight() - self.win_h) / 2)
        self.root.geometry("%sx%s+%s+%s" % (self.win_w, self.win_h, x, y))
        # self.root.iconbitmap("my.ico")

    def load(self):
        """重新加载窗口"""
        if messagebox.askokcancel('提示', '请确定删除窗口重新生成'):
            self.root.destroy()
            main()
        else:
            messagebox.showinfo("提示", "已取消操作")

    def run(self):
        """窗口运行显示"""
        self.root.resizable(0, 0)
        self.root.mainloop()

    def menuBar(self):
        """菜单栏"""

        self.main_menu = tk.Menu(self.root, tearoff=False)
        # 文件(完成)
        file_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label='文件', menu=file_menu)
        file_menu.add_command(label='打开', command=lambda: mintool.openBox(self.text))
        file_menu.add_command(label='保存', command=lambda: mintool.saveFile(self.text))

        # 网址(完成)
        url_menu = tk.Menu(self.main_menu, tearoff=False)
        url_choice = tk.IntVar()
        self.main_menu.add_cascade(label='网址', menu=url_menu)
        url_choice.set(mintool.cf.get(mintool.admin, "url_id"))
        url_menu.add_radiobutton(label='www.shizongzui.cc', variable=url_choice, value=0,
                                 command=lambda: mintool.setUrlId(url_choice))
        url_menu.add_radiobutton(label='www.luoxia.com', variable=url_choice, value=1,
                                 command=lambda: mintool.setUrlId(url_choice))
        url_menu.add_radiobutton(label='www.99csw.com', variable=url_choice, value=2,
                                 command=lambda: mintool.setUrlId(url_choice))

        # 目录(完成)
        self.spinter = ttk.Combobox(self.root)

        self.main_menu.add_command(label='目录', command=lambda: mintool.updateDir(self.spinter, self.entry))
        self.spinter.bind("<Return>", lambda x: mintool.changeContent(self.spinter, self.text))

        # 搜索(完成 百度老是拒绝访问, 已解决)
        self.entry = tk.Entry(self.root)
        self.main_menu.add_command(label='搜索', command=lambda: mintool.searchBox(self.entry, self.spinter))
        self.entry.bind("<Return>", lambda x: mintool.searchContent(self.entry, self.text, url_choice))

        # 下载(完成)
        try:
            self.main_menu.add_command(label='下载', command=lambda: mintool.downloadBook(self.root, self.title))
        except Exception as e:
            logger.warning(e)

        # 重新加载
        self.main_menu.add_command(label='重新加载', command=lambda: self.load())

        self.root.config(menu=self.main_menu)

    def contentBox(self):
        """显示文本内容"""
        try:
            self.font = font.Font(family='楷体', size=15)
            self.text = tk.Text(self.root, font=self.font, width="750", height="25")
            self.text.pack(ipady=30)
            wg = (self.spinter, self.entry)
            self.text.bind("<Button-1>", lambda x: mintool.hide(wg))
            self.text.bind("<Button-3>", lambda x: mintool.menuRK(self.root, self.text))
            # mintool.loadContent(self.text)
            mintool.directionKey(self.text)

        except Exception as e:
            logger.warning(e)

        self.text.config(state=tk.DISABLED)


def main(title="智能爬取电子书"):
    reader = APP(title)
    reader.menuBar()
    reader.contentBox()
    reader.run()


if __name__ == '__main__':

    main()
