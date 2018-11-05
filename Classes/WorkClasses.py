import json
import os
import shutil
import time
import re

import wx

from Classes import Threads
from Functions import function


class AzurLaneWork(object):
    """a class only to deal with the tex for azur lane"""

    def __init__(self, form, setting, default, start_path=os.getcwd()):
        self.form = form

        self.__dialog = None

        # Azur lane values
        self.tex_name = []
        self.mesh_name = []
        self.tex_name_china = []
        self.mesh_name_china = []

        self.tex_list_path_dir = {}
        self.mesh_list_path_dir = {}

        self.choice = None
        try:
            with open('files\\names.json', 'r')as file:
                self.names = json.load(file)
        except FileNotFoundError:
            self.names = {}

        self.pass_finish = True

        self.able_restore = 0

        self.able_restore_list = []

        self.unable_restore_list_showed = []
        self.unable_restore_list = []

        self.passed_show = []
        self.passed_list = []

        self.save_path = ''
        self.save_path_list = []

        self.start_path = start_path

        self._searched_tex = []
        self._searched_mesh = []
        self._search_skip = []
        self._search_unable = []

        self.form.m_choice_pass.Enable(False)
        self.form.m_choice_unable.Enable(False)

        self.tex_search = False
        self.mesh_search = False
        self.skip_search = False
        self.unable_search = False

        self.search_mesh_show = []
        self.search_tex_show = []
        self.search_skip_show = []
        self.search_unable_show = []

        self.search_mesh_index = []
        self.search_tex_index = []
        self.search_pass_index = []
        self.search_unable_index = []

        self.restore_list = []

        self.setting = setting["azur_lane"]

        self.full = setting["full"]

        self.default = default["azur_lane"]

        self.lock = default['lock']

        self.pattern_tex = re.compile(self.setting['tex_limit'])
        self.pattern_mesh = re.compile(self.setting['mesh_limit'])

        self.restore = Threads.RestoreThread(1, 'restore', self.restore_list, self.form, self.names,
                                             self.mesh_list_path_dir, self.tex_list_path_dir, self.save_path,
                                             self.setting, full=self.full, unable_restore_list=self.unable_restore_list)

        # file load method

    def is_choice(self):
        return self.choice

    def is_able(self):
        return self.able_restore_list != []

    def load_tex(self):
        if self.lock:
            address = self.default['default_tex_dir']
        else:
            address = os.getcwd()
        self.__dialog = wx.FileDialog(self.form, "打开", address, "AzurLane.png",
                                      "*.PNG", style=wx.FD_MULTIPLE)

        if self.__dialog.ShowModal() == wx.ID_OK:

            self.form.m_staticText_load_tex.SetLabel("开始")
            self.form.m_gauge_tex_load.SetValue(0)
            paths = self.__dialog.GetPaths()
            if not len(paths) == 0:
                num = 0
                for path in paths:
                    num += 1
                    if self.pattern_tex.match(path) is not None:
                        name = path.split('\\')[-1].split('.')[0]
                    else:
                        continue

                    if name not in self.tex_name:
                        self.tex_name.append(name)
                        self.tex_list_path_dir[name] = path
                        try:
                            self.tex_name_china.append(f"{num}）{self.names[name]}——{name}")
                            self._searched_tex.append(f"{self.names[name]}{name}")
                        except KeyError:
                            self.tex_name_china.append(f"{num}）{name}——{name}")
                            self._searched_tex.append(f"{name}")

                    self.form.m_gauge_tex_load.SetValue(function.re_int(100 * (num / len(paths))))
                self.form.m_staticText_load_tex.SetLabel("完成")
            self.form.m_listBox_tex.Set(self.tex_name_china)

        if self.able_export():
            self.form.m_menuItem_all.Enable(True)
        else:
            self.form.m_menuItem_all.Enable(False)
        if len(self.unable_restore_list) >= 1:
            self.form.m_menuItem_copy_only.Enable(True)
        else:
            self.form.m_menuItem_copy_only.Enable(False)

    def load_mesh(self):
        if self.lock:
            address = self.default['default_mesh_dir']
        else:
            address = os.getcwd()
        self.__dialog = wx.FileDialog(self.form, "打开", address,
                                      wildcard="*.OBJ", style=wx.FD_MULTIPLE)

        if self.__dialog.ShowModal() == wx.ID_OK:
            self.form.m_staticText_mesh_load.SetLabel("开始")
            self.form.m_gauge_mesh_load.SetValue(0)
            paths = self.__dialog.GetPaths()
            if not len(paths) == 0:
                num = 0
                for path in paths:

                    num += 1
                    if self.pattern_mesh.match(path) is not None:
                        name = path.split('\\')[-1].split('.')[0].replace('-mesh', '')
                    else:
                        continue

                    if name not in self.mesh_name:
                        self.mesh_list_path_dir[name] = path
                        self.mesh_name.append(name)
                        try:
                            self.mesh_name_china.append(f"{num}）{self.names[name]}——{name}")
                            self._searched_mesh.append(f"{self.names[name]}{name}")
                        except KeyError:
                            self.mesh_name_china.append(f"{num}）{name}——{name}")
                            self._searched_mesh.append(f"{name}")

                    self.form.m_gauge_tex_load.SetValue(function.re_int(100 * (num / len(paths))))
                self.form.m_staticText_mesh_load.SetLabel("完成")

        self.form.m_listBox_mesh.Set(self.mesh_name_china)
        if self.able_export():
            self.form.m_menuItem_all.Enable(True)
        else:
            self.form.m_menuItem_all.Enable(False)
        if len(self.unable_restore_list) >= 1:
            self.form.m_menuItem_copy_only.Enable(True)
        else:
            self.form.m_menuItem_copy_only.Enable(False)

    def load_mesh_fold(self):
        if self.lock:
            address = self.default['default_mesh_dir']
        else:
            address = os.getcwd()

        self.__dialog = wx.DirDialog(self.form, "打开", address,
                                     style=wx.DD_NEW_DIR_BUTTON | wx.DD_CHANGE_DIR | wx.DD_DEFAULT_STYLE |
                                           wx.DD_DIR_MUST_EXIST)

        if self.__dialog.ShowModal() == wx.ID_OK:
            paths = self.__dialog.GetPath()
            self.form.m_staticText_mesh_load.SetLabel("开始")
            self.form.m_gauge_mesh_load.SetValue(0)

            paths = function.all_file_path(paths)[1]
            self.form.m_gauge_mesh_load.SetValue(25)
            num = 0
            for path in paths.keys():
                if self.pattern_mesh.match(path) is not None:
                    name = path.split('\\')[-1].split('.')[0].replace('-mesh', '')
                else:
                    continue
                if name not in self.mesh_name:
                    self.mesh_list_path_dir[name] = paths[path]
                    self.mesh_name.append(name)
                    try:
                        self.mesh_name_china.append(f"{num}）{self.names[name]}——{name}")
                        self._searched_mesh.append(f"{self.names[name]}{name}")
                    except KeyError:
                        self.mesh_name_china.append(f"{num}）{name}——{name}")
                        self._searched_mesh.append(f"{name}")

                num += 1
                self.form.m_gauge_mesh_load.SetValue(25 + function.re_int(75 * (num / len(paths.keys()))))
            self.form.m_staticText_mesh_load.SetLabel("完成")
            self.form.m_listBox_mesh.Set(self.mesh_name_china)
        if self.able_export():
            self.form.m_menuItem_all.Enable(True)
        else:
            self.form.m_menuItem_all.Enable(False)
        if len(self.unable_restore_list) >= 1:
            self.form.m_menuItem_copy_only.Enable(True)
        else:
            self.form.m_menuItem_copy_only.Enable(False)

    def load_tex_fold(self):
        if self.lock:
            address = self.default['default_tex_dir']
        else:
            address = os.getcwd()

        self.__dialog = wx.DirDialog(self.form, "打开", address,
                                     style=wx.DD_NEW_DIR_BUTTON | wx.DD_CHANGE_DIR | wx.DD_DEFAULT_STYLE
                                           | wx.DD_DIR_MUST_EXIST)
        info = self.__dialog.ShowModal()
        if info == wx.ID_OK:
            self.form.m_staticText_load_tex.SetLabel("开始")
            paths = self.__dialog.GetPath()

            paths = function.all_file_path(paths)[1]
            self.form.m_gauge_tex_load.SetValue(25)
            num = 0
            for path in paths.keys():
                path_old = path
                if self.pattern_tex.match(path) is not None:
                    path = path.split('\\')[-1].split('.')[0]
                else:
                    continue

                if path not in self.tex_name:
                    self.tex_list_path_dir[path] = paths[path_old]
                    self.tex_name.append(path)
                    try:
                        self.tex_name_china.append(f"{num}）{self.names[path]}——{path}")
                        self._searched_tex.append(f"{self.names[path]}{path}")
                    except KeyError:
                        self.tex_name_china.append(f"{num}）{path}——{path}")
                        self._searched_tex.append(f"{path}")
                num += 1
                self.form.m_gauge_tex_load.SetValue(25 + function.re_int(75 * (num / len(paths.keys()))))
        self.form.m_staticText_load_tex.SetLabel("完成")

        self.form.m_listBox_tex.Set(self.tex_name_china)
        if self.able_export():
            self.form.m_menuItem_all.Enable(True)
        else:
            self.form.m_menuItem_all.Enable(False)
        if len(self.unable_restore_list) >= 1:
            self.form.m_menuItem_copy_only.Enable(True)
        else:
            self.form.m_menuItem_copy_only.Enable(False)

    def load_tex_and_mesh(self):
        self.__dialog = wx.DirDialog(self.form, "打开", os.getcwd(),
                                     style=wx.DD_NEW_DIR_BUTTON | wx.DD_CHANGE_DIR | wx.DD_DEFAULT_STYLE |
                                           wx.DD_DIR_MUST_EXIST)

        if self.__dialog.ShowModal() == wx.ID_OK:
            paths = self.__dialog.GetPath()
            self.form.m_staticText_load_tex.SetLabel('开始')
            self.form.m_staticText_mesh_load.SetLabel('开始')

            paths = function.all_file_path(paths)[1]

            self.form.m_gauge_tex_load.SetValue(25)
            self.form.m_gauge_mesh_load.SetValue(25)
            tex_num = mesh_num = 0
            for path in paths.keys():
                # Mesh
                if self.pattern_mesh.match(path) is not None:
                    path_old = path
                    path = path.split('\\')[-1].split('.')[0].replace('-mesh', '')

                    if path not in self.mesh_name:
                        self.mesh_list_path_dir[path] = paths[path_old]
                        self.mesh_name.append(path)
                        try:
                            self.mesh_name_china.append(f"{mesh_num}）{self.names[path]}——{path}")
                            self._searched_mesh.append(f"{self.names[path]}{path}")
                        except KeyError:
                            self.mesh_name_china.append(f"{mesh_num}）{path}——{path}")
                            self._searched_mesh.append(f"{path}")

                    mesh_num += 1
                    self.form.m_gauge_mesh_load.SetValue(25 + function.re_int(75 * (mesh_num / len(paths.keys()))))

                # texture2D
                elif self.pattern_tex.match(path) is not None:
                    path_old = path
                    path = path.split('\\')[-1].split('.')[0]
                    if path not in self.tex_name:
                        self.mesh_list_path_dir[path] = paths[path_old]
                        self.mesh_name.append(path)
                        try:
                            self.tex_name_china.append(f"{tex_num}）{self.names[path]}——{path}")
                            self._searched_tex.append(f"{self.names[path]}{path}")
                        except KeyError:
                            self.tex_name_china.append(f"{tex_num}）{path}——{path}")
                            self._searched_tex.append(f"{path}")
                    tex_num += 1
                    self.form.m_gauge_tex_load.SetValue(25 + function.re_int(75 * (tex_num / len(paths.keys()))))
                else:
                    continue

            self.form.m_gauge_tex_load.SetValue(100)
            self.form.m_gauge_mesh_load.SetValue(100)

            self.form.m_listBox_tex.Set(self.tex_name_china)
            self.form.m_listBox_mesh.Set(self.mesh_name_china)
        if self.able_export():
            self.form.m_menuItem_all.Enable(True)
        else:
            self.form.m_menuItem_all.Enable(False)

        if len(self.unable_restore_list) >= 1:
            self.form.m_menuItem_copy_only.Enable(True)
        else:
            self.form.m_menuItem_copy_only.Enable(False)

        # choice

    # choice
    def mesh_choice(self):

        if self.mesh_search:
            self.choice = self.mesh_name[self.search_mesh_index[self.form.m_listBox_mesh.GetSelection()]]
        else:
            self.choice = self.mesh_name[self.form.m_listBox_mesh.GetSelection()]
        if self.choice in self.tex_name:
            self.form.m_menuItem_choice.Enable(True)
            show = Threads.QuickRestore(self.choice, self.tex_list_path_dir, self.mesh_list_path_dir, self.form,
                                        self.start_path, full=self.full)
            show.start()

    def tex_choice(self):
        if self.tex_search:
            self.choice = self.tex_name[self.search_tex_index[self.form.m_listBox_tex.GetSelection()]]
        else:
            self.choice = self.tex_name[self.form.m_listBox_tex.GetSelection()]
        if self.choice in self.mesh_name:
            self.form.m_menuItem_choice.Enable(True)
            show = Threads.QuickRestore(self.choice, self.tex_list_path_dir, self.mesh_list_path_dir, self.form,
                                        self.start_path, self.full)
            show.start()

    def open_file(self):
        if self.unable_search:
            index = self.search_unable_index[self.form.m_listBox_unable.GetSelection()]
        else:
            index = self.form.m_listBox_unable.GetSelection()
        path = self.tex_list_path_dir[self.unable_restore_list[index]]
        os.system("start %s" % path)

    def open_pass(self):
        name = ''
        if self.skip_search:
            index = self.search_pass_index[self.form.m_listBox_info.GetSelection()]
        else:
            index = self.form.m_listBox_info.GetSelection()
        for guide in self.names.keys():
            if guide == self.passed_list[index]:
                name = f"{self.names[guide]}.png"
        try:
            path = self.save_path_list[1][name]
        except KeyError:
            name = name[:-4] + ".PNG"
            path = self.save_path_list[1][name]
        os.system(u"start " + path)

        # export

    # export
    def export_choice(self):
        self.__dialog = wx.FileDialog(self.form, "保存", os.getcwd(), self.names[self.choice], "*.png", style=wx.FD_SAVE)

        if self.__dialog.ShowModal() == wx.ID_OK:
            self.form.m_gauge_all.SetValue(0)
            self.save_path = self.__dialog.GetPath()

            shutil.copy(f"{self.start_path}\\temp.png", self.save_path)

        self.form.m_gauge_all.SetValue(100)
        if self.form.m_checkBox_autoopen.GetValue():
            os.system("start %s" % self.save_path)

    def export_all(self, path):
        if self.setting["new_dir"]:
            path += r"\碧蓝航线-导出"

        os.makedirs(path, exist_ok=True)

        self.restart()
        self.save_path = path
        self.form.m_gauge_all.SetValue(0)

        self.able_restore_list = list(set(self.able_restore_list))

        if self.full["skip_had"]:
            self.save_path_list = function.all_file_path(self.save_path)

            num = 1
            able_restore = self.able_restore_list
            for able in self.able_restore_list:
                try:
                    text = f"{self.names[able]}.png"
                    text2 = f"{self.names[able]}.PNG"
                except KeyError:
                    text = f"{able}.png"
                    text2 = "{able}.PNG"
                if text in self.save_path_list[1].keys() or \
                        text2 in self.save_path_list[1].keys():
                    self.passed_show.append('%s——%s,第%d个' % (self.names[able], able, num))
                    self.passed_list.append(able)
                    self._search_skip.append(f"{able}{self.names[able]}")
                    num += 1
                    able_restore.remove(able)
            self.able_restore_list = able_restore
        self.form.m_listBox_info.Clear()
        self.form.m_listBox_info.Set(self.passed_show)

        self.restore.update_list(self.able_restore_list, self.unable_restore_list)
        self.restore.add_save_path(self.save_path)
        if self.restore.is_alive():
            self.restore.stop_(True)
            while self.restore.is_alive():
                time.sleep(1)
            self.restore.start()
        else:
            self.restore.start()

    def copy_file(self):
        self.__dialog = wx.DirDialog(self.form, "保存", os.getcwd(),
                                     style=wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR | wx.DD_NEW_DIR_BUTTON
                                           | wx.DD_DEFAULT_STYLE)
        if self.__dialog.ShowModal() == wx.ID_OK:
            path = self.__dialog.GetPath()
            num = 0
            self.form.m_gauge_all.SetValue(0)
            for name in self.unable_restore_list:
                num += 1

                shutil.copyfile(self.tex_list_path_dir[name], f'{path}\\{self.names[name]}.png')

                self.form.m_gauge_all.SetValue(function.re_int(100 * (num / len(self.unable_restore_list))))

            if self.form.m_checkBox_autoopen.GetValue():
                os.system(self.save_path)

        # search

    # search
    def search_mesh(self):
        value = self.form.m_searchCtrl_mesh.GetValue()
        if value != '':
            indexes = function.find(value, self._searched_mesh)

            self.mesh_search = True

            self.search_mesh_show.clear()
            self.search_mesh_index.clear()

            for index in indexes:
                self.search_mesh_show.append(self.mesh_name_china[index])
                self.search_mesh_index.append(index)

            self.form.m_listBox_mesh.Clear()
            self.form.m_listBox_mesh.Set(self.search_mesh_show)
        else:
            self.mesh_search = False
            self.form.m_listBox_mesh.Clear()
            self.form.m_listBox_mesh.Set(self.mesh_name_china)

    def search_tex(self):
        value = self.form.m_searchCtrl_tex.GetValue()
        if value != '':
            indexes = function.find(value, self._searched_tex)
            self.tex_search = True

            self.search_tex_show.clear()
            self.search_tex_index.clear()

            for index in indexes:
                self.search_tex_show.append(self.tex_name_china[index])
                self.search_tex_index.append(index)

            self.form.m_listBox_tex.Clear()
            self.form.m_listBox_tex.Set(self.search_tex_show)
        else:
            self.tex_search = False
            self.form.m_listBox_tex.Clear()
            self.form.m_listBox_tex.Set(self.tex_name_china)

    def search_pass(self):
        value = self.form.m_searchCtrl_pass.GetValue()
        if value != '':
            indexes = function.find(value, self._search_skip)

            self.skip_search = True

            self.search_pass_index.clear()
            self.search_skip_show.clear()

            for index in indexes:
                self.search_skip_show.append(self.passed_show[index])
                self.search_pass_index.append(index)

            self.form.m_listBox_info.Clear()
            self.form.m_listBox_info.Set(self.search_skip_show)
        else:
            self.skip_search = False
            self.form.m_listBox_info.Clear()
            self.form.m_listBox_info.Set(self.passed_show)

    def search_unable(self):
        value = self.form.m_searchCtrl_unable.GetValue()
        if value != "":
            indexes = function.find(value, self._search_unable)

            self.unable_search = True

            self.search_unable_index.clear()
            self.search_unable_show.clear()

            for index in indexes:
                self.search_unable_show.append(self.unable_restore_list_showed[index])
                self.search_unable_index.append(index)

            self.form.m_listBox_unable.Clear()
            self.form.m_listBox_unable.Set(self.search_unable_show)
        else:
            self.unable_search = False
            self.form.m_listBox_unable.Clear()
            self.form.m_listBox_unable.Set(self.unable_restore_list_showed)

        # else

    def able_export(self):
        for name in self.mesh_name:
            if name in self.tex_name:
                self.able_restore += 1
                self.able_restore_list.append(name)
        if self.able_restore >= 1:
            num = 0
            self.unable_restore_list = []
            self.unable_restore_list_showed.clear()
            for name in self.tex_name:
                if name not in self.mesh_name and name.split(' ')[0] != "UISprite":
                    num += 1
                    try:
                        self.unable_restore_list_showed.append("%d） %s" % (num, self.names[name]))
                    except KeyError:
                        self.unable_restore_list_showed.append("%d） %s" % (num, name))
                    self.unable_restore_list.append(name)
                    try:
                        self._search_unable.append(f"{name}{self.names[name]}")
                    except KeyError:
                        self._search_unable.append(f"{name}{name}")

            self.form.m_listBox_unable.Clear()
            self.form.m_listBox_unable.Set(self.unable_restore_list_showed)

        if len(self.tex_name) >= 1:
            self.form.m_menuItem_add.Enable(True)
        else:
            self.form.m_menuItem_add.Enable(False)

        return self.able_restore >= 1

    def restart(self):

        self.passed_show = []
        self.passed_list = []
        self._search_skip.clear()

        for name in self.mesh_name:
            if name in self.tex_name:
                self.able_restore += 1
                self.able_restore_list.append(name)

        self.restore = Threads.RestoreThread(1, 'restore', self.restore_list, self.form, self.names,
                                             self.mesh_list_path_dir, self.tex_list_path_dir, self.save_path,
                                             self.setting, full=self.full, unable_restore_list=self.unable_restore_list)

        self.form.m_staticText_all.SetLabel("总进度：%s %%" % '0')
        self.form.m_gauge_all.SetValue(0)

    def update_setting(self, setting, default):
        self.setting = setting["azur_lane"]

        self.full = setting["full"]

        self.default = default["azur_lane"]

        self.lock = default['lock']

        self.pattern_tex = re.compile(self.setting['tex_limit'])
        self.pattern_mesh = re.compile(self.setting['mesh_limit'])