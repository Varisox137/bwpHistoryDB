# -*- coding: utf-8 -*-

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QSizePolicy, QSpacerItem

from qfluentwidgets import BodyLabel, PrimaryPushButton, LineEdit, PasswordLineEdit

class RegisterInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RegisterInterface")
        self.__setup_ui()

    def __setup_ui(self):
        v_spacer=QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        # 创建主体布局
        main_layout=QVBoxLayout(self)
        main_layout.setObjectName('main_layout')
        main_layout.setContentsMargins(20, 20, 20, 20)
        # # 提示信息
        hint_label=BodyLabel(text='请填写注册信息，邀请码为选填项', parent=self)
        hint_label.setObjectName('hint_label')
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # # 网格组件和布局
        grid_widget=QWidget(self)
        grid_widget.setObjectName('grid_widget')
        grid_layout=QGridLayout(self)
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
        # # # 确认密码提示标签和输入框
        confirm_password_label=BodyLabel(text='确认密码', parent=grid_widget)
        confirm_password_label.setObjectName('confirm_password_label')
        self.confirm_password_edit=PasswordLineEdit(grid_widget)
        self.confirm_password_edit.setObjectName('confirm_password_edit')
        self.confirm_password_edit.setPlaceholderText('Confirm Password')
        self.confirm_password_edit.setClearButtonEnabled(True)
        # # # 注册邀请码提示标签和输入框
        reg_key_label=BodyLabel(text='邀请码', parent=grid_widget)
        reg_key_label.setObjectName('reg_key_label')
        self.reg_key_edit=LineEdit(grid_widget)
        self.reg_key_edit.setObjectName('reg_key_edit')
        self.reg_key_edit.setPlaceholderText('Invite Code')
        self.reg_key_edit.setClearButtonEnabled(True)
        # # /
        grid_layout.addWidget(username_label, 0, 0, 1, 1)
        grid_layout.addWidget(self.username_edit, 0, 1, 1, 1)
        grid_layout.addWidget(password_label, 1, 0, 1, 1)
        grid_layout.addWidget(self.password_edit, 1, 1, 1, 1)
        grid_layout.addWidget(confirm_password_label, 2, 0, 1, 1)
        grid_layout.addWidget(self.confirm_password_edit, 2, 1, 1, 1)
        grid_layout.addWidget(reg_key_label, 3, 0, 1, 1)
        grid_layout.addWidget(self.reg_key_edit, 3, 1, 1, 1)
        grid_widget.setLayout(grid_layout)
        # # 注册按钮
        self.register_button=PrimaryPushButton(text='注册', parent=self)
        self.register_button.setObjectName('register_button')
        # /
        main_layout.addSpacerItem(v_spacer)
        main_layout.addWidget(hint_label)
        main_layout.addSpacerItem(v_spacer)
        main_layout.addWidget(grid_widget)
        main_layout.addSpacerItem(v_spacer)
        main_layout.addWidget(self.register_button)
    
if __name__=='__main__':
    app=QApplication(sys.argv)
    ui=RegisterInterface()
    ui.show()
    sys.exit(app.exec())
