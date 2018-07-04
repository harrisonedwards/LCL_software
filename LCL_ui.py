# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Desktop\LCL_software\LCL.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 689)
        MainWindow.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(-90, 200, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.target_screenshot_button = QtWidgets.QPushButton(self.centralwidget)
        self.target_screenshot_button.setGeometry(QtCore.QRect(3, 3, 71, 31))
        self.target_screenshot_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.target_screenshot_button.setObjectName("target_screenshot_button")
        self.non_target_screenshot_button = QtWidgets.QPushButton(self.centralwidget)
        self.non_target_screenshot_button.setGeometry(QtCore.QRect(73, 3, 71, 31))
        self.non_target_screenshot_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.non_target_screenshot_button.setObjectName("non_target_screenshot_button")
        self.misc_screenshot_button = QtWidgets.QPushButton(self.centralwidget)
        self.misc_screenshot_button.setGeometry(QtCore.QRect(3, 33, 71, 31))
        self.misc_screenshot_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.misc_screenshot_button.setObjectName("misc_screenshot_button")
        self.comment_box = QtWidgets.QTextEdit(self.centralwidget)
        self.comment_box.setGeometry(QtCore.QRect(4, 83, 131, 41))
        self.comment_box.setObjectName("comment_box")
        self.comment_box_label = QtWidgets.QLabel(self.centralwidget)
        self.comment_box_label.setGeometry(QtCore.QRect(6, 63, 71, 16))
        self.comment_box_label.setObjectName("comment_box_label")
        self.user_comment_button = QtWidgets.QPushButton(self.centralwidget)
        self.user_comment_button.setGeometry(QtCore.QRect(3, 123, 131, 23))
        self.user_comment_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.user_comment_button.setObjectName("user_comment_button")
        self.magnification_combobox = QtWidgets.QComboBox(self.centralwidget)
        self.magnification_combobox.setGeometry(QtCore.QRect(10, 170, 51, 22))
        self.magnification_combobox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.magnification_combobox.setEditable(False)
        self.magnification_combobox.setCurrentText("")
        self.magnification_combobox.setObjectName("magnification_combobox")
        self.magnification_label = QtWidgets.QLabel(self.centralwidget)
        self.magnification_label.setGeometry(QtCore.QRect(9, 150, 71, 16))
        self.magnification_label.setObjectName("magnification_label")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(145, 3, 851, 681))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.laser_controls_groupbox = QtWidgets.QGroupBox(self.centralwidget)
        self.laser_controls_groupbox.setGeometry(QtCore.QRect(0, 260, 120, 201))
        self.laser_controls_groupbox.setObjectName("laser_controls_groupbox")
        self.start_flashlamp_pushbutton = QtWidgets.QPushButton(self.laser_controls_groupbox)
        self.start_flashlamp_pushbutton.setGeometry(QtCore.QRect(10, 20, 101, 23))
        self.start_flashlamp_pushbutton.setObjectName("start_flashlamp_pushbutton")
        self.stop_flashlamp_pushbutton = QtWidgets.QPushButton(self.laser_controls_groupbox)
        self.stop_flashlamp_pushbutton.setGeometry(QtCore.QRect(10, 50, 101, 23))
        self.stop_flashlamp_pushbutton.setObjectName("stop_flashlamp_pushbutton")
        self.fire_qswitch_pushbutton = QtWidgets.QPushButton(self.laser_controls_groupbox)
        self.fire_qswitch_pushbutton.setGeometry(QtCore.QRect(10, 80, 101, 23))
        self.fire_qswitch_pushbutton.setObjectName("fire_qswitch_pushbutton")
        self.qswitch_delay_doublespin_box = QtWidgets.QDoubleSpinBox(self.laser_controls_groupbox)
        self.qswitch_delay_doublespin_box.setGeometry(QtCore.QRect(10, 127, 101, 22))
        self.qswitch_delay_doublespin_box.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.qswitch_delay_doublespin_box.setDecimals(0)
        self.qswitch_delay_doublespin_box.setMinimum(50.0)
        self.qswitch_delay_doublespin_box.setMaximum(10000.0)
        self.qswitch_delay_doublespin_box.setSingleStep(5.0)
        self.qswitch_delay_doublespin_box.setProperty("value", 200.0)
        self.qswitch_delay_doublespin_box.setObjectName("qswitch_delay_doublespin_box")
        self.Qswitch_delay_label = QtWidgets.QLabel(self.laser_controls_groupbox)
        self.Qswitch_delay_label.setGeometry(QtCore.QRect(10, 108, 101, 16))
        self.Qswitch_delay_label.setObjectName("Qswitch_delay_label")
        self.attenuator_label = QtWidgets.QLabel(self.laser_controls_groupbox)
        self.attenuator_label.setGeometry(QtCore.QRect(10, 150, 101, 16))
        self.attenuator_label.setObjectName("attenuator_label")
        self.attenuator_doublespin_box = QtWidgets.QDoubleSpinBox(self.laser_controls_groupbox)
        self.attenuator_doublespin_box.setGeometry(QtCore.QRect(10, 170, 101, 22))
        self.attenuator_doublespin_box.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.attenuator_doublespin_box.setDecimals(2)
        self.attenuator_doublespin_box.setMinimum(0.0)
        self.attenuator_doublespin_box.setMaximum(100.0)
        self.attenuator_doublespin_box.setSingleStep(0.1)
        self.attenuator_doublespin_box.setProperty("value", 0.6)
        self.attenuator_doublespin_box.setObjectName("attenuator_doublespin_box")
        self.lysed_screenshot_button = QtWidgets.QPushButton(self.centralwidget)
        self.lysed_screenshot_button.setGeometry(QtCore.QRect(73, 33, 71, 31))
        self.lysed_screenshot_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lysed_screenshot_button.setObjectName("lysed_screenshot_button")
        self.step_size_doublespin_box = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.step_size_doublespin_box.setGeometry(QtCore.QRect(10, 220, 71, 22))
        self.step_size_doublespin_box.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.step_size_doublespin_box.setDecimals(0)
        self.step_size_doublespin_box.setMinimum(5.0)
        self.step_size_doublespin_box.setMaximum(10000.0)
        self.step_size_doublespin_box.setSingleStep(5.0)
        self.step_size_doublespin_box.setProperty("value", 5.0)
        self.step_size_doublespin_box.setObjectName("step_size_doublespin_box")
        self.step_size_label = QtWidgets.QLabel(self.centralwidget)
        self.step_size_label.setGeometry(QtCore.QRect(10, 200, 81, 16))
        self.step_size_label.setObjectName("step_size_label")
        self.noise_filter_checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.noise_filter_checkbox.setGeometry(QtCore.QRect(70, 170, 71, 17))
        self.noise_filter_checkbox.setObjectName("noise_filter_checkbox")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "LCL System"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.target_screenshot_button.setText(_translate("MainWindow", "Target \n"
" Screenshot"))
        self.non_target_screenshot_button.setText(_translate("MainWindow", "Non-Target \n"
" Screenshot"))
        self.misc_screenshot_button.setText(_translate("MainWindow", "Misc. \n"
" Screenshot"))
        self.comment_box_label.setText(_translate("MainWindow", "Comment box"))
        self.user_comment_button.setText(_translate("MainWindow", "Add comment to log"))
        self.magnification_label.setText(_translate("MainWindow", "Magnification"))
        self.laser_controls_groupbox.setTitle(_translate("MainWindow", "Laser Controls"))
        self.start_flashlamp_pushbutton.setText(_translate("MainWindow", "Flash Lamp Auto"))
        self.stop_flashlamp_pushbutton.setText(_translate("MainWindow", "Flash Lamp Off"))
        self.fire_qswitch_pushbutton.setText(_translate("MainWindow", "Fire Q-Switch"))
        self.Qswitch_delay_label.setText(_translate("MainWindow", "Q Switch Delay [us]"))
        self.attenuator_label.setText(_translate("MainWindow", "Attenuator"))
        self.lysed_screenshot_button.setText(_translate("MainWindow", "Lysed \n"
" Screenshot"))
        self.step_size_label.setText(_translate("MainWindow", "Stage Step Size"))
        self.noise_filter_checkbox.setText(_translate("MainWindow", "CLAHE"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

