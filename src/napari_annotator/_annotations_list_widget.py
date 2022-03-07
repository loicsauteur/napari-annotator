import napari
from napari_annotator._annotation_entry import LabelItem

from qtpy.QtWidgets import QWidget, QLabel, QGridLayout
from qtpy.QtCore import Qt

class AnnoList(QWidget):
    '''
    Creates a grid layout QWidget to be inserted into the main dock_widget,
    with buttons for each label of a label layer.
    The (main) grid layout will contain only the label entries.
    A header is created and saved as a class variable. This way, in the main dock_widget,
    the header can be added independently of the label entries list, allowing them to be scrollable.
    '''
    def __init__(self, labelLayer:napari.layers.Labels):
        super().__init__()
        self.gridLayout = QGridLayout()
        self.setLayout(self.gridLayout)

        # class variables
        self.labelLayer = labelLayer
        self.header_items = ["Label #", "Visible", "Center", "Color", "Erase"]
        self.header_items_info = [
            "Label entry",
            "Toggle visibility of the label",
            "Move to the label",
            "Change color of the label",
            "Erase the drawings of the label"
        ]
        self.label_items_array = [] # array for the Label_item entries

        # create a LUT color dictionary
        self.colormap = napari.utils.colormaps.label_colormap()#(num_colors=1024)
        # limits the label layer to 255 labels, current limitation due to mismatch of viewer color with tool colors
        self.color_dict = self.create_color_dictionary(self.colormap.colors)
        # apply the color dictionary to the labels layer
        if self.labelLayer != None:
            self.labelLayer.colormap = self.colormap
            self.labelLayer.color = self.color_dict

        # create header widget object to be added into the _dock_Widget Layout
        self.header = self.create_header()

        # initialise the widget
        # check if label_items_array is empty and populate it
        if not self.label_items_array and self.labelLayer != None:
            self.initialise_widget(self.labelLayer)



    ######          AnnoList class methods               ######

    def create_color_dictionary(self, cur_colors):
        '''
        Helper function
        Create a color dictionary of the current colors
        :parameter: cur_colors: array of RGBA colors (possible: current labels colormap)
        :return: color_dictionary, where key = label, value = array of 4 floats (RGBA)
        '''

        color_dict = {}
        for i in range(0, len(cur_colors)):
            color_dict[i] = cur_colors[i]
        return color_dict


    # highlight the currently selected label
    def get_selected_label(self):
        '''
        Highlights the label button in the widget list with a yellow color.
        '''
        label_index = self.labelLayer.selected_label
        # first, reset all buttons to the default color
        for i in range(0, len(self.label_items_array)):
            self.label_items_array[i].reset_font_color()
        if len(self.label_items_array) >= label_index:
            label_item = self.label_items_array[label_index-1].set_font_color('color: yellow')


    # update to the current number of drawn labels
    def update_label_entries(self):
        '''
        Updates the entries according to the max number of labels
        '''
        # create new entry, if new label was added
        if len(self.label_items_array) < self.labelLayer.data.max():
            # make sure that it works for if several labels were added at once
            for i in range(len(self.label_items_array), self.labelLayer.data.max()):
                new_label_item = LabelItem(len(self.label_items_array) + 1, self.labelLayer, self.color_dict)
                new_label_item.set_color_dictionary(self.color_dict)
                self.label_items_array.append(new_label_item)
                cur_qWidgets_list = new_label_item.get_qWidget_list()
                # add the entry to the widget
                for j in range(0, len(cur_qWidgets_list)):
                    self.layout().addWidget(cur_qWidgets_list[j], len(self.label_items_array), j)

    # remove the label entries in the widget (excluding the header)
    def remove_widget_entries(self):
        '''
        Resets the labels in the widget.
        Should be called upon layer change.
        '''
        self.label_items_array = []
        for i in range(0, self.layout().count()):
            self.layout().itemAt(i).widget().deleteLater()



    # create the header of the widget Label_item list
    def create_header(self):
        '''
        Create the widget header, labeling (Tooltip) subsequent entries for what they are for.
        This creates a QWidget for adding directly into the _dock_widget
        :return: QWidget (with QGridLayout with horizontally centered items)
        '''
        headerWidget = QWidget()
        headerWidget.setLayout(QGridLayout())

        for i in range(0, len(self.header_items)):
            header = QLabel(self.header_items[i])
            header.setToolTip(self.header_items_info[i])
            headerWidget.layout().addWidget(header, 0, i, Qt.AlignHCenter)
        return headerWidget

    # initialise/populate the label_items_array
    def create_label_item_array(self):
        '''
        Creates the list of Label_items with a given number of labels read from the labels layer.
        '''
        if self.labelLayer != None and self.labelLayer.data.max() > 0:
            for i in range(0, self.labelLayer.data.max()):
                entry = LabelItem(i+1, self.labelLayer, self.color_dict)
                entry.set_color_dictionary(self.color_dict)
                self.label_items_array.append(entry)


    # initialise widget
    def initialise_widget(self, layer):
        '''
        Initialises the QWidget i.e. adding a grid of QWidgets into the main widget.
        Called upon layer change to Labels layer
        :param layer: napari labels layer
        '''
        self.labelLayer = layer
        self.label_items_array = []
        self.create_label_item_array() # populates the label_items_array
        for i in range(0, len(self.label_items_array)): # basically the table rows (i+1 later to jump header)
            cur_qWidgets_list = self.label_items_array[i].get_qWidget_list()
            for j in range(0, len(cur_qWidgets_list)): # basically go over the columns
                self.layout().addWidget(cur_qWidgets_list[j], i, j)
        # update the colors
        self.labelLayer.colormap = self.colormap
        self.labelLayer.color = self.color_dict
