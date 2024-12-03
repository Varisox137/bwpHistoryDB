# -*- coding: utf-8 -*-

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout,
                             QSizePolicy, QSpacerItem, QHeaderView, QTableWidgetItem,)

from qfluentwidgets import TableWidget
from qfluentwidgets import BodyLabel, PushButton, ComboBox, SearchLineEdit, CheckBox
from qfluentwidgets import setCustomStyleSheet

from custom_stylesheets import *

# 引入字段类型映射字典
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
# 无视下面一行的报错，app.py文件在后端目录下，在使用了sys.path.append后能够被正确导入
from app import FIELDS_TYPE_MAPPING
FIELDS_TYPE_MAPPING=FIELDS_TYPE_MAPPING.copy()

class MainInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('MainInterface')
        self.__setup_ui()

    def __setup_ui(self):
        h_spacer=QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        # 主体布局
        main_layout=QVBoxLayout(self)
        main_layout.setObjectName('main_layout')
        main_layout.setContentsMargins(20, 20, 20, 20)
        # # 上操作栏组件和布局
        main_operations_widget=QWidget(self)
        main_operations_widget.setObjectName('main_operations_widget')
        main_operations_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_operations_layout=QHBoxLayout(main_operations_widget)
        main_operations_layout.setObjectName('main_operations_layout')
        # # # 全选复选框
        self.select_all_checkbox=CheckBox(main_operations_widget)
        self.select_all_checkbox.setObjectName('select_all_checkbox')
        self.select_all_checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.select_all_checkbox.setText('全选')
        self.select_all_checkbox.setTristate(True)
        self.select_all_checkbox.clicked.connect(self.__update_checkboxes_from_select_all)
        # # # 查询按钮
        self.query_button=PushButton(main_operations_widget)
        self.query_button.setObjectName('query_button')
        self.query_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.query_button.setText('查询')
        setCustomStyleSheet(self.query_button, QUERY_BUTTON_STYLE, QUERY_BUTTON_STYLE)
        # # # 数据表下拉框
        self.tablename_combobox=ComboBox(main_operations_widget)
        self.tablename_combobox.setObjectName('tablename_combobox')
        self.tablename_combobox.setFixedWidth(130)
        self.tablename_combobox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.tablename_combobox.addItems(['']+list(FIELDS_TYPE_MAPPING.keys()))
        self.tablename_combobox.setPlaceholderText('请选择数据表')
        # # # 查询字段下拉框
        self.field_combobox=ComboBox(main_operations_widget)
        self.field_combobox.setObjectName('field_combobox')
        self.field_combobox.setFixedWidth(150)
        self.field_combobox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.field_combobox.addItems(['不指定字段'])
        self.field_combobox.setPlaceholderText('请选择查询字段')
        # # # 搜索框
        self.search_line_edit=SearchLineEdit(self)
        self.search_line_edit.setObjectName('search_line_edit')
        self.search_line_edit.setFixedWidth(300)
        self.search_line_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.search_line_edit.setPlaceholderText('请输入搜索内容')
        self.search_line_edit.setClearButtonEnabled(True)
        # # # 多个按钮：新增、导入、导出
        self.add_button=PushButton(self)
        self.add_button.setObjectName('add_button')
        self.add_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.add_button.setText('新增')
        setCustomStyleSheet(self.add_button, ADD_BUTTON_STYLE, ADD_BUTTON_STYLE)
        self.import_button=PushButton(self)
        self.import_button.setObjectName('import_button')
        self.import_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        setCustomStyleSheet(self.import_button, IMPORT_BUTTON_STYLE, IMPORT_BUTTON_STYLE)
        self.import_button.setText('导入')
        self.export_button=PushButton(self)
        self.export_button.setObjectName('export_button')
        self.export_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.export_button.setText('导出')
        setCustomStyleSheet(self.export_button, EXPORT_BUTTON_STYLE, EXPORT_BUTTON_STYLE)
        # # /
        main_operations_layout.addWidget(self.select_all_checkbox)
        main_operations_layout.addWidget(self.query_button)
        main_operations_layout.addWidget(self.tablename_combobox)
        main_operations_layout.addWidget(self.field_combobox)
        main_operations_layout.addWidget(self.search_line_edit)
        main_operations_layout.addItem(h_spacer)
        main_operations_layout.addWidget(self.add_button)
        main_operations_layout.addWidget(self.import_button)
        main_operations_layout.addWidget(self.export_button)
        main_operations_widget.setLayout(main_operations_layout)
        # # 表格视图布局
        self.table_widget=TableWidget(self)
        self.table_widget.setObjectName('table_widget')
        self.table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_widget.setBorderRadius(8)
        self.table_widget.setBorderVisible(True)
        self.table_widget.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # # 下方操作栏组件和布局
        bottom_operations_widget=QWidget(self)
        bottom_operations_widget.setObjectName('bottom_operations_widget')
        bottom_operations_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bottom_operations_layout=QHBoxLayout(bottom_operations_widget)
        bottom_operations_layout.setObjectName('bottom_operations_layout')
        # # # 重新登录按钮
        self.relogin_button=PushButton(bottom_operations_widget)
        self.relogin_button.setObjectName('relogin_button')
        self.relogin_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.relogin_button.setText('重新登录')
        setCustomStyleSheet(self.relogin_button, DELETE_BUTTON_STYLE, DELETE_BUTTON_STYLE)
        # # # 操作反馈标签
        self.feedback_label=BodyLabel(bottom_operations_widget)
        self.feedback_label.setObjectName('feedback_label')
        self.feedback_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # # /
        bottom_operations_layout.addWidget(self.relogin_button)
        bottom_operations_layout.addItem(h_spacer)
        bottom_operations_layout.addWidget(self.feedback_label)
        bottom_operations_widget.setLayout(bottom_operations_layout)
        # /
        main_layout.addWidget(main_operations_widget)
        main_layout.addWidget(self.table_widget)
        main_layout.addWidget(bottom_operations_widget)
        # 如果正在测试窗口，则设置表格数据样例
        if __name__=='__main__':
            self.__set_table_test_data()

    def __set_table_test_data(self):
        test_fields=['id', 'name', 'field', 'description', 'time']
        test_data=[
            {'id': 1, 'name': 'Abigail', 'field': 'DEPT', 'description': 'Department', 'time': '2000-01-01'},
            {'id': 2, 'name': 'Bob', 'field': 'SUPP', 'description': 'Supplier', 'time': '2020-12-31'},
            {'id': 3, 'name': 'Chris', 'field': 'EMP', 'description': 'Employee', 'time': '2024-08-31'},
        ]
        self.clear_and_fill_table(test_fields, test_data*10)

    def clear_and_fill_table(self, fields:list[str], data:list[dict]):
        self.table_widget.clearContents()
        self.table_widget.clear()
        self.table_data=data
        # 检查数据列表非空且内部数据字典非空
        data=[entry for entry in data if entry]
        # 无论是否有数据，都设置表格头部、数据行数、行复选框和行操作按钮的列表
        self.table_widget.setColumnCount(len(fields)+2)
        # # 设置表头的列名
        self.table_widget.setHorizontalHeaderLabels(['selection']+fields+['operations'])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # # 打印表头宽度
        header_width=sum(
            self.table_widget.columnWidth(i) for i in range(self.table_widget.columnCount())
        )
        print('field widths:', end=' ')
        [print(self.table_widget.columnWidth(i),end=' ') for i in range(self.table_widget.columnCount())]
        print(f'\n{header_width=}, {self.table_widget.width()=}')
        # 填充表格数据
        self.table_widget.setRowCount(len(data))
        self.row_checkboxes=list() # 内部存储复选框
        self.row_operations_buttons=list() # 内部以[(PushButton[edit], PushButton[delete])]形式存储行操作按钮
        if data and data[0]:
            for row, entry in enumerate(data):
                # 首列为复选框
                row_checkbox=CheckBox(self.table_widget)
                row_checkbox.setObjectName(f'row_checkbox_{row}')
                row_checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                row_checkbox.clicked.connect(self.__update_select_all_from_checkboxes)
                self.table_widget.setCellWidget(row, 0, row_checkbox)
                self.row_checkboxes.append(row_checkbox)
                # 中间列为数据
                for col, field in enumerate(fields):
                    cell_item=QTableWidgetItem(str(entry.get(field, ''))) # set text
                    cell_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table_widget.setItem(row, col+1, cell_item)
                # 最后一列为操作按钮，复合形成一个组件
                row_operations_widget=QWidget(self.table_widget)
                row_operations_widget.setObjectName(f'row_operations_widget_{row}')
                row_operations_layout=QHBoxLayout(row_operations_widget)
                row_operations_layout.setObjectName(f'row_operations_layout_{row}')
                row_operations_layout.setContentsMargins(5, 5, 5, 5)
                # # 行编辑按钮
                row_edit_button=PushButton(row_operations_widget)
                row_edit_button.setObjectName(f'row_edit_button_{row}')
                row_edit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                row_edit_button.setText('编辑')
                setCustomStyleSheet(row_edit_button, EDIT_BUTTON_STYLE, EDIT_BUTTON_STYLE)
                # # 行删除按钮
                row_delete_button=PushButton(row_operations_widget)
                row_delete_button.setObjectName(f'row_delete_button_{row}')
                row_delete_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                row_delete_button.setText('删除')
                setCustomStyleSheet(row_delete_button, DELETE_BUTTON_STYLE, DELETE_BUTTON_STYLE)
                # /
                row_operations_layout.addWidget(row_edit_button)
                row_operations_layout.addWidget(row_delete_button)
                row_operations_widget.setLayout(row_operations_layout)
                self.table_widget.setCellWidget(row, len(fields)+1, row_operations_widget)
                self.row_operations_buttons.append((row_edit_button, row_delete_button))
        # 更新操作反馈
        self.feedback_label.setText(f'共获取到 {len(data)} 条记录')

    def __update_checkboxes_from_select_all(self):
        if self.select_all_checkbox.checkState()==Qt.CheckState.PartiallyChecked:
            self.select_all_checkbox.setCheckState(Qt.CheckState.Checked)
        if hasattr(self, 'row_checkboxes'):
            for checkbox in self.row_checkboxes:
                checkbox.setChecked(self.select_all_checkbox.isChecked())

    def __update_select_all_from_checkboxes(self):
        any_checked=any(checkbox.isChecked() for checkbox in self.row_checkboxes)
        all_checked=all(checkbox.isChecked() for checkbox in self.row_checkboxes)
        if all_checked:
            if self.select_all_checkbox.checkState()!=Qt.CheckState.Checked:
                self.select_all_checkbox.setCheckState(Qt.CheckState.Checked)
        elif any_checked:
            if self.select_all_checkbox.checkState()!=Qt.CheckState.PartiallyChecked:
                self.select_all_checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
        else:
            if self.select_all_checkbox.checkState()!=Qt.CheckState.Unchecked:
                self.select_all_checkbox.setCheckState(Qt.CheckState.Unchecked)

if __name__=='__main__':
    app=QApplication(sys.argv)
    ui=MainInterface()
    ui.show()
    sys.exit(app.exec())
