# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *


class TreeNodeKind(object):
    ROOT = u'root'
    GROUP = u'group'
    OBJECT = u'object'
    INVALID_FORMULA = u'invalid-formula'


class TreeNode(object):

    def __init__(self, data, kind=TreeNodeKind.OBJECT):
        self._parent = None
        self._data = data
        self._childs = []
        self._kind = kind

    def add(self, node):
        self._childs.append(node)
        node._parent = self

    def remove(self, node):
        self._childs.remove(node)
        node._parent = None

    # def find(self, data):
    #     if self._data == data:
    #         return self

    #     for child in self._childs:
    #         if child._data == data:
    #             return child

    #     return None

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
        if self._kind == TreeNodeKind.INVALID_FORMULA:
            return u'(!) %s' % self._data
        elif self._kind == TreeNodeKind.OBJECT:
            return str(self._data)
        # if self._kind == TreeNodeKind.OBJECT:
        #     return self._data.getName()
        return self.data()

    def __repr__(self):
        return '<TreeNode: %s, %s>' % (self._kind, repr(self._data))


class PlotTreeModel(QAbstractItemModel):
    
    def __init__(self, dView, *args, **kwargs):
        super(PlotTreeModel, self).__init__(*args, **kwargs)
        self._root = TreeNode(u'Dynamite', TreeNodeKind.ROOT)

        # DynamiteView signals
        # dView.plotAdded.connect(self._plotAdded)
        # dView.plotRemoved.connect(self._plotRemoved)

    def addFormula(self, text):
        self._root.add(TreeNode(text, TreeNodeKind.INVALID_FORMULA))
        self.reset()

    def search(self, obj):
        for x in self._root._childs:
            if x._data == obj:
                return x
        return None

    def _plotAdded(self, plot):
        self._root.add(TreeNode(plot, TreeNodeKind.OBJECT))
        self.reset() # TODO: be more efficient here (do not reset the hole the model)

    def _plotRemoved(self, plot):
        self.reset() # TODO: be more efficient here (do not reset the hole the model)

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
            if node._kind == TreeNodeKind.OBJECT:
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

    # some particular methods
    def select(self, indexes):
        for index in indexes:
            node = index.internalPointer()

            if node._kind == TreeNodeKind.OBJECT:
                if hasattr(node._data, 'selected'):
                    node.data().selected = True

                    for x in node._childs:
                        if hasattr(x._data, 'selected'):
                            x._data.selected = True

    def deselect(self, indexes):
        for index in indexes:
            node = index.internalPointer()

            if node._kind == TreeNodeKind.OBJECT:
                if hasattr(node._data, 'selected'):
                    node.data().selected = False


class PlotTreeView(QTreeView):

    def __init__(self, dView, *args, **kwargs):
        super(PlotTreeView, self).__init__(*args, **kwargs)
        self._view = dView

        self.setMinimumWidth(200)

        self.setModel(PlotTreeModel(dView))
        self.setSelectionMode(QTreeView.ExtendedSelection)
        self.setSelectionBehavior(QTreeView.SelectRows)
        self.selectionModel().selectionChanged.connect(self._selectionChanged)

        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self._setupActions()

        self._view.selectionChanged.connect(self._viewSelectionChanged)

    def _setupActions(self):
        configure = QAction(u'Configure', self)
        #configure.triggered.connect(self.con)
        self.addAction(configure)

        # self.style().standardIcon(QStyle.SP_TrashIcon),
        delete = QAction(u'Delete', self)
        delete.triggered.connect(self._deleteAction)
        self.addAction(delete)

    def _deleteAction(self, checked=False):
        for index in self.selectionModel().selectedIndexes():
            node = index.internalPointer()
            if node._kind == TreeNodeKind.OBJECT:
                node.parent().remove(node)
                self._view.remove(node.data())

    # fired when the selection changes
    def _selectionChanged(self, selected, deselected):
        self.model().select(selected.indexes())
        self.model().deselect(deselected.indexes())

    def _viewSelectionChanged(self, selected, notSelected):
        if not selected:
            self.clearSelection()
            # self.update()
            # self.selectionModel().setCurrentIndex(QModelIndex(), QItemSelectionModel.Select)
            # self.update()
        # selectedIndexes = []

        # for p in selected:
        #     print repr(self.model().find(p))
