# -*- coding: utf-8 -*-

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy, QSpacerItem

from qfluentwidgets import BodyLabel, PushButton, PrimaryPushButton, LineEdit, PasswordLineEdit

class LoginInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('LoginInterface')
        self.__setup_ui()

    def __setup_ui(self):
        h_spacer=QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        v_spacer=QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        # 创建主体布局
        main_layout=QVBoxLayout(self)
        main_layout.setObjectName('main_layout')
        main_layout.setContentsMargins(20, 20, 20, 20)
        # # 创建提示栏组件和布局
        hint_widget=QWidget(self)
        hint_widget.setObjectName('hint_widget')
        hint_layout=QHBoxLayout(hint_widget)
        hint_layout.setObjectName('hint_layout')
        # # # 提示标签
        hint_label=BodyLabel(text='请登录以使用数据库系统', parent=hint_widget) # text, parent
        hint_label.setObjectName('hint_label')
        hint_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # # # 注册按钮
        self.register_button=PushButton(text='用户注册', parent=hint_widget)
        self.register_button.setObjectName('register_button')
        self.register_button.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        # # /
        hint_layout.addItem(h_spacer)
        hint_layout.addWidget(hint_label)
        hint_layout.addItem(h_spacer)
        hint_layout.addWidget(self.register_button)
        hint_layout.addItem(h_spacer)
        hint_widget.setLayout(hint_layout)
        # # 网格组件和布局
        grid_widget=QWidget(self)
        grid_widget.setObjectName('grid_widget')
        grid_layout=QGridLayout(grid_widget)
        grid_layout.setObjectName('grid_layout')
        grid_layout.setContentsMargins(20, 20, 20, 20)
        # # # 用户名提示标签和输入框
        username_label=BodyLabel(text='用户名', parent=grid_widget)
        username_label.setObjectName('username_label')
        self.username_edit=LineEdit(grid_widget)
        self.username_edit.setObjectName('username_edit')
        self.username_edit.setPlaceholderText('Username')
        self.username_edit.setClearButtonEnabled(True)
        # # # 密码提示标签和输入框
        password_label=BodyLabel(text='密码', parent=grid_widget)
        password_label.setObjectName('password_label')
        self.password_edit=PasswordLineEdit(grid_widget)
        self.password_edit.setObjectName('password_edit')
        self.password_edit.setPlaceholderText('Password')
        self.password_edit.setClearButtonEnabled(True)
        # # /
        grid_layout.addWidget(username_label, 0, 0, 1, 1)
        grid_layout.addWidget(self.username_edit, 0, 1, 1, 1)
        grid_layout.addItem(v_spacer, 1, 0, 1, 1)
        grid_layout.addWidget(password_label, 2, 0, 1, 1)
        grid_layout.addWidget(self.password_edit, 2, 1, 1, 1)
        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(1, 5)
        grid_widget.setLayout(grid_layout)
        # # 登录按钮
        self.login_button=PrimaryPushButton(text='登录', parent=self)
        self.login_button.setObjectName('login_button')
        # /
        main_layout.addItem(v_spacer)
        main_layout.addWidget(hint_widget)
        main_layout.addItem(v_spacer)
        main_layout.addWidget(grid_widget)
        main_layout.addItem(v_spacer)
        main_layout.addWidget(self.login_button)
        self.setLayout(main_layout)
    
if __name__=='__main__':
    app=QApplication(sys.argv)
    ui=LoginInterface()
    ui.show()
    sys.exit(app.exec())
