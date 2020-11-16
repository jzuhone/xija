from IPython.core.interactiveshell import InteractiveShell
from IPython.core.completer import IPCompleter

from qtconsole.inprocess import QtInProcessKernelManager
from qtconsole.rich_jupyter_widget import RichJupyterWidget

from PyQt5 import QtWidgets

InteractiveShell.cache_size.default_value = 0

if hasattr(IPCompleter, 'dict_keys_only'):
    IPCompleter.dict_keys_only.default_value = True

kernel_manager = None
kernel_client = None


class WidgetTable(dict):
    def __init__(self, n_rows, n_cols=None, colnames=None, show_header=False, colwidths=None):
        if n_cols is None and colnames is None:
            raise ValueError('WidgetTable needs either n_cols or colnames')
        if colnames:
            self.colnames = colnames
            self.n_cols = len(colnames)
        else:
            self.n_cols = n_cols
            self.colnames = ['col{}'.format(i + 1) for i in range(n_cols)]
        self.n_rows = n_rows
        self.show_header = show_header

        self.table = QtWidgets.QTableWidget(self.n_rows, self.n_cols)

        if show_header and colnames:
            self.table.setHorizontalHeaderLabels(colnames)

        if colwidths:
            for col, width in colwidths.items():
                self.table.setColumnWidth(col, width)

        dict.__init__(self)

    def __getitem__(self, rowcol):
        """Get widget at location (row, col) where ``col`` can be specified as
        either a numeric index or the column name.

        [Could do a nicer API that mimics np.array access, column wise by name,
        row-wise by since numeric index, or element by (row, col).  But maybe
        this isn't needed now].
        """
        row, col = rowcol
        if col in self.colnames:
            col = self.colnames.index(col)
        return dict.__getitem__(self, (row, col))

    def __setitem__(self, rowcol, widget):
        row, col = rowcol
        dict.__setitem__(self, rowcol, widget)
        self.table.setCellWidget(row, col, widget)


"""
The code here has been borrowed from glue:

http://glueviz.org
https://github.com/glue-viz/glue

See the Glue BSD license here:
https://github.com/glue-viz/glue/blob/master/LICENSE

"""


def start_in_process_kernel():

    global kernel_manager, kernel_client

    kernel_manager = QtInProcessKernelManager()
    kernel_manager.start_kernel()

    kernel_client = kernel_manager.client()
    kernel_client.start_channels()


def in_process_console(console_class=RichJupyterWidget, **kwargs):
    """Create a console widget, connected to an in-process Kernel
    
    Keyword arguments will be added to the namespace of the shell.

    Parameters
    ----------
    console_class :
         (Default value = RichJupyterWidget)
    **kwargs :
        

    Returns
    -------

    
    """

    global kernel_manager, kernel_client

    if kernel_manager is None:
        start_in_process_kernel()

    def stop():
        kernel_client.stop_channels()
        kernel_manager.shutdown_kernel()

    control = console_class()
    control._display_banner = False
    control.kernel_manager = kernel_manager
    control.kernel_client = kernel_client
    control.exit_requested.connect(stop)
    control.shell = kernel_manager.kernel.shell
    control.shell.user_ns.update(**kwargs)
    control.setWindowTitle('xija_gui_fit IPython Terminal -- type howto() for instructions')

    return control

