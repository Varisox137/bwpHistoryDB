# -*- coding: utf-8 -*-

import sys
from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QSizePolicy, QSpacerItem, QHBoxLayout

from qfluentwidgets import (BodyLabel, SubtitleLabel, PushButton, PrimaryPushButton,
                            LineEdit, TextEdit, DateEdit, ComboBox, CheckBox)

# 引入字段类型映射字典、部分字段允许值列表字典
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
# 无视下面一行的报错，app.py文件在后端目录下，在使用了sys.path.append后能够被正确导入
from app import FIELDS_TYPE_MAPPING, FIELDS_VALUE_LISTS
FIELDS_TYPE_MAPPING=FIELDS_TYPE_MAPPING.copy()
FIELDS_VALUE_LISTS=FIELDS_VALUE_LISTS.copy()

class EditInterface(QWidget):
    def __init__(self, model:str='SS_Version', mode:str='add', data:dict=None):
        assert model in FIELDS_TYPE_MAPPING, 'Invalid model name'
        assert mode in ('add', 'edit', 'delete'), 'Invalid operation mode'
        if mode!='add':
            assert data is not None, 'Original data not provided'
        super().__init__()
        self.setObjectName('EditInterface')
        self.model=model
        self.mode=mode
        self.__setup_ui(data)

    def __setup_ui(self, data:dict=None):
        if data is None: data=dict()
        h_spacer=QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        # 创建主体布局
        main_layout=QVBoxLayout(self)
        main_layout.setObjectName('main_layout')
        main_layout.setContentsMargins(20, 20, 20, 20)
        # # 提示标签
        if self.mode=='delete':
            hint_label=BodyLabel(text='请确认要删除的条目的信息', parent=self)
        else:
            operation='新增' if self.mode=='add' else '修改'
            hint_label=BodyLabel(text=f'请填写要{operation}的条目的信息，前有*号的为必填项', parent=self)
        hint_label.setObjectName('hint_label')
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # # 模型名称标签
        model_name_label=SubtitleLabel(text=self.model, parent=self)
        model_name_label.setObjectName('model_name_label')
        # model_name_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        model_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # # 网格组件和布局
        grid_widget=QWidget(self)
        grid_widget.setObjectName('grid_widget')
        grid_layout=QGridLayout(grid_widget)
        grid_layout.setObjectName('grid_layout')
        grid_layout.setContentsMargins(20, 20, 20, 20)
        # # # 项目名称标签和输入框
        model_field_type_mapping=FIELDS_TYPE_MAPPING[self.model].copy()
        model_field_type_mapping.pop('Default') # 去除默认字段
        self.getting_widget_inputs=dict() # 用于保存各输入组件的值获取方法的字典，dict[str, Callable]
        for row, field in enumerate(model_field_type_mapping.keys()):
            full_field_name=f'{self.model}.{field}'
            label_text=field
            if model_field_type_mapping[field][1]: # 必填字段
                label_text='*'+label_text
            field_label=BodyLabel(text=label_text, parent=grid_widget)
            field_label.setObjectName(f'field_label_{full_field_name}')
            grid_layout.addWidget(field_label, row, 0, 1, 1)
            # # # 判断字段类型并创建相应的输入组件
            if model_field_type_mapping[field][2]=='date':
                # 填写数据更新日期，非必填字段，使用复选框和日期输入框的组合
                date_input_wrapper=QWidget(grid_widget)
                date_input_wrapper.setObjectName(f'date_input_wrapper_{full_field_name}')
                date_input_h_layout=QHBoxLayout(date_input_wrapper)
                date_input_h_layout.setObjectName(f'date_input_h_layout_{full_field_name}')
                date_input_h_layout.setContentsMargins(5, 0, 0, 0)
                # # 提供复选框以选择是否填写日期
                date_checkbox=CheckBox(text='', parent=date_input_wrapper)
                date_checkbox.setObjectName(f'date_checkbox_{full_field_name}')
                date_checkbox.setChecked(False)
                date_checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                # # 日期输入框
                date_edit=DateEdit(parent=date_input_wrapper)
                date_edit.setObjectName(f'date_edit_{full_field_name}')
                date_edit.setDateRange(date(2019, 12, 12), date.today())
                date_edit.setEnabled(False)
                # # 复选框决定是否启用日期输入框
                date_checkbox.stateChanged.connect(lambda state: date_edit.setEnabled(date_checkbox.isChecked()))
                # 设置既有值
                original_value=data.get(field, None)
                if original_value is not None:
                    date_edit.setDate(date.fromisoformat(original_value))
                    date_checkbox.setChecked(True)
                else:
                    date_checkbox.setChecked(False)
                # /
                date_input_h_layout.addWidget(date_checkbox)
                date_input_h_layout.addWidget(date_edit)
                date_input_wrapper.setLayout(date_input_h_layout)
                # 如果是删除模式，则禁止编辑
                if self.mode=='delete':
                    date_input_wrapper.setEnabled(False) # 禁用了父组件，则子组件也会被禁用
                grid_layout.addWidget(date_input_wrapper, row, 1, 1, 1)
                # 也要提供获取复选框状态的方法，只有勾选了才取日期值，否则取None
                self.getting_widget_inputs['date_enabled']=date_checkbox.isChecked
                self.getting_widget_inputs[field]=date_edit.date
            elif full_field_name in FIELDS_VALUE_LISTS:
                # 限制了允许值列表的字段，使用下拉框
                combo_box=ComboBox(parent=grid_widget)
                combo_box.setObjectName(f'combo_box_{full_field_name}')
                combo_box.addItems([str(value) for value in FIELDS_VALUE_LISTS[full_field_name]])
                # 设置既有值
                original_value=data.get(field, None)
                if original_value is not None:
                    combo_box.setCurrentText(str(original_value))
                # 如果是删除模式，则禁止编辑
                if self.mode=='delete':
                    combo_box.setEnabled(False)
                grid_layout.addWidget(combo_box, row, 1, 1, 1)
                self.getting_widget_inputs[field]=combo_box.currentText
            elif field.endswith('_desc'):
                # 能力描述字段，使用多行文本输入框
                text_edit=TextEdit(parent=grid_widget)
                text_edit.setObjectName(f'text_edit_{full_field_name}')
                text_edit.setPlaceholderText('请输入描述文本')
                text_edit.setMinimumHeight(100)
                # 设置既有值
                original_value=data.get(field, None)
                if original_value is not None:
                    text_edit.setPlainText(original_value)
                # 如果是删除模式，则禁止编辑
                if self.mode=='delete':
                    text_edit.setEnabled(False)
                grid_layout.addWidget(text_edit, row, 1, 1, 1)
                self.getting_widget_inputs[field]=text_edit.toPlainText
            else:
                # 其他字段类型，使用普通输入框
                line_edit=LineEdit(parent=grid_widget)
                line_edit.setObjectName(f'line_edit_{full_field_name}')
                line_edit.setPlaceholderText('请输入内容')
                line_edit.setClearButtonEnabled(True)
                # 设置既有值
                original_value=data.get(field, None)
                if original_value is not None:
                    line_edit.setText(str(original_value))
                # 如果是编辑模式且该字段是主键字段，则禁止编辑
                if self.mode=='edit' and full_field_name in (
                        'SS.ssid', 'SS_Version.ssvid', 'Card.cid', 'Card_Version.cvid'
                ):
                    line_edit.setEnabled(False)
                # 如果是删除模式，则禁止编辑
                if self.mode=='delete':
                    line_edit.setEnabled(False)
                grid_layout.addWidget(line_edit, row, 1, 1, 1)
                self.getting_widget_inputs[field]=line_edit.text
        # # 网格布局列宽设置
        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(1, 5)
        # # 提交按钮
        self.submit_button=PrimaryPushButton(text='提交', parent=self)
        self.submit_button.setObjectName('submit_button')
        # /
        main_layout.addItem(h_spacer) # 填充固定高度的空白
        main_layout.addWidget(hint_label)
        main_layout.addItem(h_spacer)
        main_layout.addWidget(model_name_label)
        main_layout.addWidget(grid_widget)
        main_layout.addWidget(self.submit_button)
        self.setLayout(main_layout)
    
if __name__=='__main__':
    app=QApplication(sys.argv)
    edit_interface=EditInterface()
    edit_interface.show()
    sys.exit(app.exec())
