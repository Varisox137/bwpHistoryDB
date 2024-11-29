# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal, QDate
from qfluentwidgets import MessageBox
# 引入设计好的UI
from register import RegisterInterface
from login import LoginInterface
from main import MainInterface
from edit import EditInterface

# 引入字段类型映射字典、部分字段允许值列表字典
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
# 无视下面一行的报错，app.py文件在后端目录下，在使用了sys.path.append后能够被正确导入
from app import FIELDS_TYPE_MAPPING, FIELDS_VALUE_LISTS
FIELDS_TYPE_MAPPING=FIELDS_TYPE_MAPPING.copy()
FIELDS_VALUE_LISTS=FIELDS_VALUE_LISTS.copy()

# 引入系统模块
import sys
# 引入多线程和时间模块
import threading, time
# 引入数据处理模块
import pandas as pd
# 引入哈希模块
from hashlib import sha256
# 引入网络通信模块
import httpx
client=httpx.Client(timeout=3)
TARGET_HOST='http://localhost:1037'
API_PREFIX=''

def try_get_api_prefix():
    global API_PREFIX
    try:
        print('getting api prefix')
        response=client.get(f'{TARGET_HOST}/get_api_prefix')
        API_PREFIX=response.json()['data']['api_prefix']
        print(f'got api prefix: {API_PREFIX}')
    except:
        API_PREFIX=''

class RegisterWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent_login_window=parent
        self.interface=RegisterInterface()
        self.setCentralWidget(self.interface)
        self.setFixedSize(400, 300)
        self.setWindowTitle('用户注册')
        self.setWindowIcon(QIcon('./appicon.ico'))
        # 绑定注册按钮的点击事件
        self.interface.register_button.clicked.connect(self.__try_register)

    def closeEvent(self, event):
        self.parent_login_window.show()
        print('register window closed')
        event.accept()

    def __try_register(self):
        # 获取输入的用户名和密码
        username=self.interface.username_edit.text()
        password=self.interface.password_edit.text()
        confirm_password=self.interface.confirm_password_edit.text()
        reg_key=self.interface.reg_key_edit.text()
        # 尝试注册
        if not username or not password:
            # 如果用户名或密码为空，则弹出警告窗口
            MessageBox('警告', '用户名或密码不能为空！', self).show(); return False
        elif password!=confirm_password:
            # 如果两次输入的密码不一致，则弹出警告窗口
            MessageBox('警告', '两次输入的密码不一致！', self).show(); return False
        else:
            try_get_api_prefix()
            if not API_PREFIX:
                MessageBox('警告', '无法连接到服务器！', self).show(); return False
            # 清空输入框
            self.interface.username_edit.clear()
            self.interface.password_edit.clear()
            self.interface.reg_key_edit.clear()
            # 尝试注册
            pwd_hash=sha256(password.encode('utf-8')).hexdigest(); del password
            reg_data={'username': username, 'pwd_hash': pwd_hash, 'reg_key': reg_key}
            response=client.post(url=f"{TARGET_HOST}{API_PREFIX}/register", json=reg_data)
            if response.status_code!=200:
                # 获取来自服务器的错误信息
                error_msg=response.json()['message']
                MessageBox('警告', f'注册失败：\n{error_msg}', self).show(); return False
            # 注册成功
            uid=response.json()['data']['new_uid']
            user_type=response.json()['data']['user_type']
            MessageBox('提示', f'注册成功！\n您的uid是：{uid}\n您的用户类型是：{user_type}', self).show()
            self.close()

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.interface=LoginInterface()
        self.setCentralWidget(self.interface)
        self.setFixedSize(400, 300)
        self.setWindowTitle('用户登录')
        self.setWindowIcon(QIcon('./appicon.ico'))
        # 保留两个窗口的引用
        self.register_window=RegisterWindow(self)
        self.main_window=MainWindow(self)
        # 绑定注册按钮的点击事件
        self.interface.register_button.clicked.connect(self.__show_register_window)
        # 绑定登录按钮的点击事件
        self.interface.login_button.clicked.connect(self.__try_login)

    def __show_main_window(self):
        self.main_window.show()
        self.hide()

    def __show_register_window(self):
        self.register_window.show()
        self.hide()

    def __try_login(self):
        # 获取输入的用户名和密码
        username=self.interface.username_edit.text()
        password=self.interface.password_edit.text()
        # 尝试登录
        if not username or not password:
            # 如果用户名或密码为空，则弹出警告窗口
            MessageBox('警告', '用户名或密码不能为空！', self).show(); return False
        else:
            try_get_api_prefix()
            if not API_PREFIX:
                MessageBox( '警告', '无法连接到服务器！', self).show(); return False
            # 清空输入框
            self.interface.username_edit.clear()
            self.interface.password_edit.clear()
            # 尝试登录
            pwd_hash=sha256(password.encode('utf-8')).hexdigest(); del password
            login_data={'username': username, 'pwd_hash': pwd_hash}
            response=client.post(url=f"{TARGET_HOST}{API_PREFIX}/login", json=login_data)
            if response.status_code!=200:
                # 获取来自服务器的错误信息
                error_msg=response.json()['message']
                MessageBox('警告', f'登录失败：\n{error_msg}', self).show(); return False
            # 登录成功
            uid = response.json()['data']['uid']
            user_type=response.json()['data']['user_type']
            self.__post_login_success(user_type, uid)
            self.__show_main_window()

    def __post_login_success(self, user_type:str, uid:int):
        client.headers.update({'Authentication': str(uid)})
        # 建立线程池并定时发送保活请求
        self.logged_in_status=[True, user_type=='admin', uid]
        # 按钮功能的权限控制
        self.main_window.interface.add_button.setEnabled(self.logged_in_status[1])
        self.main_window.interface.import_button.setEnabled(self.logged_in_status[1])
        # 启动保活线程
        self.thread_keeping_alive=threading.Thread(target=self.__keep_alive)
        self.thread_keeping_alive.start()

    def __keep_alive(self):
        if self.logged_in_status[0]:
            uid=self.logged_in_status[2]
            try:
                response=client.post(url=f"{TARGET_HOST}{API_PREFIX}/keep_alive", json={'uid': uid})
                if response.status_code!=204:
                    # 获取来自服务器的错误信息
                    error_msg=response.json()['message']
                    print(f'[{time.strftime("%H:%M:%S", time.localtime())}] '
                          f'keep-alive failed: {error_msg}')
                else:
                    print(f'[{time.strftime("%H:%M:%S", time.localtime())}] '
                          f'keep-alive success')
            except:
                print(f'[{time.strftime("%H:%M:%S", time.localtime())}] '
                      f'keep-alive failed: network error')
            # 定时发送下一次保活请求
            threading.Timer(5, self.__keep_alive).start()

class MainWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent_login_window=parent
        self.interface=MainInterface()
        self.setCentralWidget(self.interface)
        self.setFixedSize(1200, 750)
        self.setWindowTitle('数据库管理系统')
        self.setWindowIcon(QIcon('./appicon.ico'))
        # 绑定查询按钮的点击事件
        self.interface.query_button.clicked.connect(self.__try_query_data)
        # 绑定数据表下拉框的选择事件
        self.interface.tablename_combobox.currentTextChanged.connect(self.__update_field_choice)
        # 绑定新增按钮的点击事件
        self.interface.add_button.clicked.connect(self.__try_add_data)
        # 绑定导入、导出按钮的点击事件
        self.interface.import_button.clicked.connect(self.__try_import_data)
        self.interface.export_button.clicked.connect(self.__try_export_data)
        # 绑定重新登录按钮的点击事件
        self.interface.relogin_button.clicked.connect(self.__try_relogin)

    def closeEvent(self, event):
        print('main window closing......waiting for keep-alive thread to exit')
        self.parent_login_window.logged_in_status=[False, False, 0]
        self.parent_login_window.thread_keeping_alive.join()
        print('logging out......')
        try_get_api_prefix()
        if API_PREFIX:
            client.post(f'{TARGET_HOST}{API_PREFIX}/logout')
            client.headers.pop('Authentication')
        event.accept()

    def __try_query_data(self, table:str=''):
        self.interface.feedback_label.clear()
        self.interface.feedback_label.setText('正在查询数据……')
        # 获取要查询的数据表名、字段名和搜索值
        table_name=table or self.interface.tablename_combobox.currentText()
        field_name=self.interface.field_combobox.currentText()
        search_value=self.interface.search_line_edit.text()
        print(f'{table_name=} {field_name=} {search_value=}')
        # 尝试查询数据
        if not table and not self.interface.tablename_combobox.currentText():
            # 主动查询、table为空，但未选择数据表，则弹出警告窗口
            MessageBox('警告', '请先选择要查询的数据表！', self).show()
            self.interface.feedback_label.setText('最近一次查询失败')
            return False
        else:
            try_get_api_prefix()
            if not API_PREFIX:
                MessageBox('警告', '无法连接到服务器！', self).show()
                self.interface.feedback_label.setText('最近一次查询失败')
                return False
            # 尝试查询数据
            self.interface.search_line_edit.clear()
            query_data={
                'item_model': table_name,
                'query_field': field_name,
                'search_value': search_value
            }
            response=client.post(url=f'{TARGET_HOST}{API_PREFIX}/query', json=query_data)
            if response.status_code!=200:
                # 获取来自服务器的错误信息
                error_msg=response.json()['message']
                MessageBox('警告', f'查询失败：\n{error_msg}', self).show()
                self.interface.feedback_label.setText('最近一次查询失败')
                return False
            # 查询成功，将查询结果填充到表格中
            data=response.json()['data'] # 服务器返回的查询结果
            data_fields, data_list=data['fields'], data['list'] # 后者应当为list[dict]格式
            self.last_queried_table_name=table_name
            self.interface.clear_and_fill_table(data_fields, data_list)
            self.__bind_row_widgets()

    def __bind_row_widgets(self):
        print('binding row widgets......')
        # 绑定表格每行的编辑、删除按钮的点击事件（实际上只需要遍历self.interface.row_operations_buttons二元组列表即可）
        for row, (row_edit_button, row_delete_button)\
                in enumerate(self.interface.row_operations_buttons):
            print(f'binding row {row} buttons')
            row_edit_button.clicked.connect(lambda *args, _row=row: self.__try_edit_data(self.last_queried_table_name, _row))
            row_delete_button.clicked.connect(lambda *args, _row=row: self.__try_delete_data(self.last_queried_table_name, _row))
            row_edit_button.setEnabled(self.parent_login_window.logged_in_status[1])
            row_delete_button.setEnabled(self.parent_login_window.logged_in_status[1])

    def __update_field_choice(self):
        print(f'updating field choice......')
        # 获取当前选择的数据表名
        table_name=self.interface.tablename_combobox.currentText()
        # 查找字段映射表
        table_fields=(list(FIELDS_TYPE_MAPPING.get(table_name, dict()).keys()).copy())
        if 'Default' in table_fields:
            table_fields.remove('Default')
        # 更新下拉框选项
        self.interface.field_combobox.clear()
        self.interface.field_combobox.addItems(['Default']+table_fields)
        self.interface.field_combobox.setPlaceholderText('请选择查询字段')

    def __try_add_data(self):
        table=self.interface.tablename_combobox.currentText()
        print(f'try to add data in table [{table}]')
        if not table:
            # 未选择数据表，则弹出警告窗口
            MessageBox('警告', '请先选择要新增条目的数据表！', self).show(); return False
        self.edit_window=EditWindow(self,
                                    model_name=self.interface.tablename_combobox.currentText(),
                                    edit_mode='add')
        self.edit_window.show()
        self.setEnabled(False)

    def __try_edit_data(self, table:str, row:int):
        print(f'try to edit data on {row=}')
        self.edit_window=EditWindow(self,
                                    model_name=table,
                                    edit_mode='edit',
                                    original_row_data=self.interface.table_data[row])
        self.edit_window.show()
        self.setEnabled(False)

    def __try_delete_data(self, table:str, row:int):
        print(f'try to delete data on {row=}')
        self.edit_window=EditWindow(self,
                                    model_name=table,
                                    edit_mode='delete',
                                    original_row_data=self.interface.table_data[row])
        self.edit_window.show()
        self.setEnabled(False)

    def try_submit_data(self):
        print(f'try to submit operation on data')
        # 遍历输入组件，获取输入值
        item_data=dict()
        for field, get_value_func in self.edit_window.interface.getting_widget_inputs.items():
            value=get_value_func()
            if isinstance(value, QDate):
                date_field=field
                value=value.toString('yyyy-MM-dd')
            print(f'{field}={value}')
            item_data[field]=value
        # 未勾选日期字段时，将其设置为None
        if 'date_enabled' in item_data:
            if not item_data.pop('date_enabled'):
                print(f'clearing date field {date_field}')
                item_data[date_field]=None
        # 尝试提交数据
        try_get_api_prefix()
        if not API_PREFIX:
            MessageBox('警告', '无法连接到服务器！', self.edit_window).show(); return False
        # 尝试提交数据
        submit_data={
            'item_model': self.edit_window.interface.model,
            'item_data': item_data
        }
        if self.edit_window.interface.mode=='add':
            response=client.post(url=f'{TARGET_HOST}{API_PREFIX}/add_item', json=submit_data)
        elif self.edit_window.interface.mode=='edit':
            response=client.post(url=f'{TARGET_HOST}{API_PREFIX}/edit_item', json=submit_data)
        else: # self.edit_window.interface.mode=='delete'
            response=client.post(url=f'{TARGET_HOST}{API_PREFIX}/delete_item', json=submit_data)
        if response.status_code!=204:
            # 获取来自服务器的错误信息
            error_msg=response.json()['message']
            MessageBox('警告', f'提交失败：\n{error_msg}', self.edit_window).show()
            return False
        self.edit_window.close()
        self.__try_query_data(table=self.edit_window.interface.model)

    def __try_import_data(self):
        table=self.interface.tablename_combobox.currentText()
        if not table:
            # 未选择数据表，则弹出警告窗口
            MessageBox('警告', '请先选择要批量导入数据的数据表！', self).show(); return False
        # 弹出打开文件对话框
        dialog=QFileDialog(self, '打开文件', '', 'CSV文件 (*.csv)')
        dialog.setDefaultSuffix('csv')
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_path, _=QFileDialog.getOpenFileName(self, '打开文件', '', 'CSV文件 (*.csv)')
        self.setEnabled(False)
        if not file_path: self.setEnabled(True); return False
        # 尝试解析CSV数据
        try:
            df=pd.read_csv(file_path, encoding='utf-8', na_filter=False)
        except:
            # 解析失败，弹出警告窗口
            MessageBox('警告', '无法解析CSV文件！', self).show()
            self.setEnabled(True); return False
        # 尝试导入数据
        try_get_api_prefix()
        if not API_PREFIX:
            MessageBox('警告', '无法连接到服务器！', self).show()
            self.setEnabled(True); return False
        # 尝试导入数据
        import_data={
            'item_model': table,
            'batch_data': df.to_dict(orient='records')
        }
        response=client.post(url=f'{TARGET_HOST}{API_PREFIX}/batch_update', json=import_data)
        if response.status_code!=200:
            # 获取来自服务器的错误信息
            error_msg=response.json()['message']
            MessageBox('警告', f'数据导入失败：\n{error_msg}', self).show()
            self.setEnabled(True); return False
        # 导入完成，显示每个条目的更新结果
        joined_result_message='\n'.join([f'行 {row} ：{result}' for row, result
                                         in response.json()['data']['item_messages'].items()
                                         ])
        # 弹出更新结果窗口，包含带滚动条视图的长文本框
        result_window=BatchUpdateResultDisplayWindow(self, joined_result_message)
        self.setEnabled(True)
        result_window.show()
        self.__try_query_data(table)

    def __try_export_data(self):
        if not hasattr(self.interface, 'row_checkboxes'):
            # 未查询到数据，则弹出警告窗口
            MessageBox('警告', '请先查询以获取条目数据！', self).show(); return False
        if not any(checkbox.isChecked() for checkbox in self.interface.row_checkboxes):
            # 未选择任何条目，则弹出警告窗口
            MessageBox('警告', '请先选择要导出的条目数据！', self).show(); return False
        # 遍历选中的条目，添加到DataFrame
        columns=list(FIELDS_TYPE_MAPPING[self.last_queried_table_name].keys()).copy()
        columns.remove('Default')
        df=pd.DataFrame(columns=columns)
        for row, checkbox in enumerate(self.interface.row_checkboxes):
            if checkbox.isChecked():
                row_data=self.interface.table_data[row]
                df.loc[len(df)]=[row_data[col] for col in columns]
        # 弹出保存文件对话框
        dialog=QFileDialog(self, '保存文件', '', 'CSV文件 (*.csv)')
        dialog.setDefaultSuffix('csv')
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_path, _=QFileDialog.getSaveFileName(self, '保存文件', '', 'CSV文件 (*.csv)')
        if file_path:
            df.to_csv(file_path, index=False, encoding='utf-8')
            MessageBox('提示', f'导出成功！\n文件路径：{file_path}', self).show()

    def __try_relogin(self):
        # 先尝试登出
        try_get_api_prefix()
        if API_PREFIX:
            client.post(f'{TARGET_HOST}{API_PREFIX}/logout')
            client.headers.pop('Authentication')
            self.parent_login_window.logged_in_status=[False, False, 0]
        # 重新显示登录窗口
        self.parent_login_window.show()
        self.hide()

class EditWindow(QMainWindow):
    def __init__(self, parent, model_name:str, edit_mode:str, original_row_data:dict=None):
        super().__init__()
        self.parent_main_window=parent
        self.interface=EditInterface(model_name, edit_mode, original_row_data)
        self.setCentralWidget(self.interface)
        self.setFixedWidth(400)
        operation='新增' if edit_mode=='add' else '修改'
        self.setWindowTitle(f'{operation}条目')
        self.setWindowIcon(QIcon('./appicon.ico'))
        # 绑定提交按钮的点击事件
        self.interface.submit_button.clicked.connect(self.parent_main_window.try_submit_data)

    def closeEvent(self, event):
        self.parent_main_window.setEnabled(True)
        event.accept()

class BatchUpdateResultDisplayWindow(QMainWindow):
    from PyQt6.QtWidgets import QWidget

    class BatchUpdateResultDisplayInterface(QWidget):
        def __init__(self, text:str):
            super().__init__()
            self.setObjectName('BatchUpdateResultDisplayInterface')
            self.text=text
            self.__setup_ui()

        def __setup_ui(self):
            from PyQt6.QtWidgets import QVBoxLayout, QSizePolicy
            from PyQt6.QtCore import Qt
            from qfluentwidgets import BodyLabel, TextEdit, PrimaryPushButton

            main_layout=QVBoxLayout(self)
            main_layout.setContentsMargins(20, 20, 20, 20)
            hint_label=BodyLabel(text='数据导入完成！以下为批量更新结果：', parent=self)
            hint_label.setObjectName('hint_label')
            hint_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_edit=TextEdit(self)
            text_edit.setObjectName('text_edit')
            text_edit.setFixedSize(560, 400)
            text_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            text_edit.setText(self.text)
            text_edit.setReadOnly(True)
            close_button=PrimaryPushButton(text='关闭', parent=self)
            close_button.setObjectName('close_button')
            main_layout.addWidget(hint_label)
            main_layout.addWidget(text_edit)
            main_layout.addWidget(close_button)
            self.setLayout(main_layout)
            close_button.clicked.connect(self.close)

    def __init__(self, parent, text:str):
        super().__init__()
        self.parent_main_window=parent
        self.interface=self.BatchUpdateResultDisplayInterface(text)
        self.setCentralWidget(self.interface)
        self.setFixedWidth(600)
        self.setWindowTitle(f'结果')
        self.setWindowIcon(QIcon('./appicon.ico'))

if __name__ == '__main__':
    app=QApplication(sys.argv)
    start_window=LoginWindow()
    start_window.show()
    sys.exit(app.exec())
