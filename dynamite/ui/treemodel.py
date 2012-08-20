# encoding: utf-8
from PySide.QtCore import *

class TreeNodeKind(object):
    ROOT = u'root'
    GROUP = u'group'
    PLOT = u'plot'
    TEXT = u'text'


class TreeNode(object):

    def __init__(self, data, kind=TreeNodeKind.TEXT):
        self._parent = None
        self._data = data
        self._childs = []
        self._kind = kind

    def add(self, node):
        self._childs.append(node)
        node._parent = self

    def child(self, row):
        return self._childs[row]

    def childCount(self):
        return len(self._childs)

    def data(self):
        return self._data

    def parent(self):
        return self._parent

    def row(self):
        if self._parent:
            return self._parent._childs.index(self)
        return 0

    def display(self):
        if self._kind == TreeNodeKind.PLOT:
            return self._data.getName()
        return self.data()

    def __repr__(self):
        return '<TreeNode: %s, %s>' % (self._kind, repr(self._data))


class PlotTreeModel(QAbstractItemModel):
    
    def __init__(self, dView, *args, **kwargs):
        super(PlotTreeModel, self).__init__(*args, **kwargs)
        self._root = TreeNode(u'Dynamite', TreeNodeKind.ROOT)

        # DynamiteView signals
        dView.plot_added.connect(self._plot_added)

    def _plot_added(self, plot):
        self._root.add(TreeNode(plot, TreeNodeKind.PLOT))
        self.reset() # TODO: call only 'dataChanged' or something?

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root.display()
        return None

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole:
            return node.display()
        elif role == Qt.CheckStateRole:
            if node._kind == TreeNodeKind.PLOT:
                plot = node.data()

                if plot.enabled:
                    return Qt.Checked
            return Qt.Unchecked

        return None

    def setData(self, index, value, role):
        node = index.internalPointer()

        if role == Qt.CheckStateRole:
            if value == Qt.Checked:
                node.data().setEnabled(True)
            else:
                node.data().setEnabled(False)

        self.dataChanged.emit(index, index)
        return True

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        parentNode = self._root if not parent.isValid() else parent.internalPointer()
        return parentNode.childCount()

    def columnCount(self, parent):
        return 1

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parentNode = self._root if not parent.isValid() else parent.internalPointer()
        child = parentNode.child(row)

        if child:
            return self.createIndex(row, column, child)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childNode = index.internalPointer()
        parentNode = childNode.parent()

        if parentNode == self._root:
            return QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
