import numpy as np
from .utils import WidgetTable
from PyQt5 import QtCore, QtWidgets
from Chandra.Time import DateTime


class WriteTableWindow(QtWidgets.QMainWindow):
    def __init__(self, model, main_window):
        super(WriteTableWindow, self).__init__()
        self.model = model
        self.mw = main_window
        self.setWindowTitle("Write Table")
        wid = QtWidgets.QWidget(self)
        self.box = QtWidgets.QVBoxLayout()
        wid.setLayout(self.box)
        self.setGeometry(0, 0, 200, 600)
        self.scroll = QtWidgets.QScrollArea()
        self.setCentralWidget(wid)

        self.last_filename = ""

        self.ftd = self.mw.fmt_telem_data
        self.write_list = self.ftd.data_names

        self.start_date = self.ftd.dates[0]
        self.stop_date = self.ftd.dates[-1]

        main_box = QtWidgets.QVBoxLayout()

        self.start_label = QtWidgets.QLabel("Start time: {}".format(self.start_date))
        self.stop_label = QtWidgets.QLabel("Stop time: {}".format(self.stop_date))
        self.list_label = QtWidgets.QLabel("Data to write:")

        self.start_text = QtWidgets.QLineEdit()
        self.start_text.returnPressed.connect(self.change_start)

        self.stop_text = QtWidgets.QLineEdit()
        self.stop_text.returnPressed.connect(self.change_stop)

        main_box.addWidget(self.start_label)
        main_box.addWidget(self.start_text)
        main_box.addWidget(self.stop_label)
        main_box.addWidget(self.stop_text)

        item_box = QtWidgets.QVBoxLayout()

        pair = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Write All Data")
        all_chkbox = QtWidgets.QCheckBox()
        all_chkbox.setChecked(True)
        pair.addWidget(all_chkbox)
        pair.addWidget(label)
        pair.addStretch(1)
        item_box.addLayout(pair)

        all_chkbox.stateChanged.connect(self.toggle_all_data)

        self.check_boxes = []
        for name in self.ftd.data_names:
            pair = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(name)
            chkbox = QtWidgets.QCheckBox()
            chkbox.setChecked(True)
            pair.addWidget(chkbox)
            pair.addWidget(label)
            pair.addStretch(1)
            item_box.addLayout(pair)
            self.check_boxes.append(chkbox)

        item_wid = QtWidgets.QWidget(self)
        item_wid.setLayout(item_box)

        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(item_wid)
        main_box.addWidget(self.scroll)
        buttons = QtWidgets.QHBoxLayout()

        write_button = QtWidgets.QPushButton('Write Table')
        write_button.clicked.connect(self.save_ascii_table)

        close_button = QtWidgets.QPushButton('Close')
        close_button.clicked.connect(self.close_window)

        buttons.addWidget(write_button)
        buttons.addWidget(close_button)

        main_box.addLayout(buttons)
        self.box.addLayout(main_box)

    def toggle_all_data(self, state):
        checked = state == QtCore.Qt.Checked
        for i, box in enumerate(self.check_boxes):
            box.setChecked(checked)

    def change_start(self):
        self.start_date = self.start_text.text()
        self.start_label.setText("Start time: {}".format(self.start_date))
        self.start_text.setText("")

    def change_stop(self):
        self.stop_date = self.stop_text.text()
        self.stop_label.setText("Stop time: {}".format(self.stop_date))
        self.stop_text.setText("")

    def close_window(self, *args):
        self.close()

    def save_ascii_table(self):
        from astropy.table import Table, Column
        dlg = QtWidgets.QFileDialog()
        dlg.setNameFilters(["DAT files (*.dat)", "TXT files (*.txt)", "All files (*)"])
        dlg.selectNameFilter("DAT files (*.dat)")
        dlg.setAcceptMode(dlg.AcceptSave)
        dlg.exec_()
        filename = str(dlg.selectedFiles()[0])
        if filename != '':
            try:
                checked = []
                for i, box in enumerate(self.check_boxes):
                    if box.isChecked():
                        checked.append(i)
                t = Table()
                ts = DateTime([self.start_date, self.stop_date]).secs
                ts[-1] += 1.0 # a buffer to make sure we grab the last point
                istart, istop = np.searchsorted(self.ftd.times, ts)
                c = Column(self.ftd.dates[istart:istop], name="date", format="{0}")
                t.add_column(c)
                for i, key in enumerate(self.ftd):
                    if i in checked:
                        c = Column(self.ftd[i][istart:istop], name=key, format=self.ftd.formats[i])
                        t.add_column(c)
                t.write(filename, overwrite=True, format='ascii.ecsv')
                self.last_filename = filename
            except IOError as ioerr:
                msg = QtWidgets.QMessageBox()
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setText("There was a problem writing the file:")
                msg.setDetailedText("Cannot write {}. {}".format(filename, ioerr.strerror))
                msg.exec_()


class ModelInfoWindow(QtWidgets.QMainWindow):
    def __init__(self, model, main_window, filename):
        super(ModelInfoWindow, self).__init__()
        self.model = model
        self.setWindowTitle("Model Info")
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        self.box = QtWidgets.QVBoxLayout()
        wid.setLayout(self.box)
        self.setGeometry(0, 0, 300, 200)

        self.main_window = main_window
        self.checksum_label = QtWidgets.QLabel()
        self.checksum_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.update_checksum()
        self.filename_label = QtWidgets.QLabel()
        self.update_filename(filename)

        checksum_layout = QtWidgets.QHBoxLayout()
        checksum_layout.addWidget(QtWidgets.QLabel("MD5 sum: "))
        checksum_layout.addWidget(self.checksum_label)
        checksum_layout.addStretch(1)

        main_box = QtWidgets.QVBoxLayout()
        main_box.addWidget(self.filename_label)
        main_box.addLayout(checksum_layout)
        main_box.addWidget(QtWidgets.QLabel("Start time: {}".format(model.datestart)))
        main_box.addWidget(QtWidgets.QLabel("Stop time: {}".format(model.datestop)))
        main_box.addWidget(QtWidgets.QLabel("Timestep: {:.1f} s".format(model.dt)))
        main_box.addWidget(QtWidgets.QLabel("Evolve Method: Core {}".format(model.evolve_method)))
        main_box.addWidget(QtWidgets.QLabel("Runge-Kutta Order: {}".format(4 if model.rk4 else 2)))
        main_box.addStretch(1)

        close_button = QtWidgets.QPushButton('Close')
        close_button.clicked.connect(self.close_window)

        close_box = QtWidgets.QHBoxLayout()
        close_box.addStretch(1)
        close_box.addWidget(close_button)

        main_box.addLayout(close_box)
        self.box.addLayout(main_box)

    def update_checksum(self):
        self.main_window.set_checksum()
        if self.main_window.checksum_match:
            color = 'black'
        else:
            color = 'red'
        checksum_str = self.main_window.md5sum
        self.checksum_label.setText(checksum_str)
        self.checksum_label.setStyleSheet(f'color: {color}')

    def update_filename(self, filename):
        self.filename_label.setText(f"Filename: {filename}")

    def close_window(self, *args):
        self.close()
        self.main_window.model_info_window = None


class LineDataWindow(QtWidgets.QMainWindow):
    def __init__(self, model, main_window, plots_box):
        super(LineDataWindow, self).__init__()
        self.model = model
        self.setWindowTitle("Line Data")
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        self.box = QtWidgets.QVBoxLayout()
        wid.setLayout(self.box)
        self.setGeometry(0, 0, 350, 600)

        self.plots_box = plots_box
        self.main_window = main_window
        self.ftd = self.main_window.fmt_telem_data
        self.nrows = len(self.ftd.data_names)+1

        self.table = WidgetTable(n_rows=self.nrows,
                                 colnames=['name', 'value'],
                                 colwidths={1: 200},
                                 show_header=True)

        self.table[0, 0] = QtWidgets.QLabel("date")
        self.table[0, 1] = QtWidgets.QLabel("")

        for row in range(1, self.nrows):
            name = self.ftd.data_names[row-1]
            self.table[row, 0] = QtWidgets.QLabel(name)
            self.table[row, 1] = QtWidgets.QLabel("")

        self.update_data()

        self.box.addWidget(self.table.table)

    def update_data(self):
        pos = np.searchsorted(self.plots_box.pd_times,
                              self.plots_box.xline)
        date = self.main_window.dates[pos]
        self.table[0, 1].setText(date)
        for row in range(1, self.nrows):
            val = self.ftd[row-1]
            fmt = self.ftd.formats[row-1]
            self.table[row, 1].setText(fmt.format(val[pos]))
