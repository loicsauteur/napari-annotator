import napari
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from napari_annotator._annotations_list_widget import AnnoList


class Annotator(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    #   --> I defined the input type for autocompletion purposes
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__()

        #                   class varialbes                 #
        self.viewer = napari_viewer
        active = self.viewer.layers.selection.active
        if isinstance(active, napari.layers.Labels):
            self.selected_Layer = self.viewer.layers.selection.active
        else:
            self.selected_Layer = None
        self.info = QLabel("Labels layer = " + str(self.selected_Layer))
        self.widget_label_main = AnnoList(
            self.selected_Layer
        )  # create this object anyway for initialisation

        #                   layout              #
        # create default layout and
        # add text info for current selected labels layer
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.info)

        # get the header of the label items (to be) and add it into the layout
        self.layout().addWidget(self.widget_label_main.header)

        # Set a scroll area onto the widget_label_main
        # (list of label entries) and add it to the widget
        scroll = QScrollArea()
        scroll.setWidget(self.widget_label_main)
        self.widget_label_main.layout().setAlignment(Qt.AlignTop)
        scroll.setWidgetResizable(True)
        self.layout().addWidget(scroll)

        #                   "Action listeners"              #
        # autodetect change in layer selection
        # and update the class variables
        @self.viewer.layers.selection.events.connect
        def update_selected_layer(event):
            """
            Reset the widget label list entry when layer selection changes.
            Check if the selected layer is a label layer or not.
            :param event:
            :return:
            """
            # print("-------   Notification:  layer change event")
            layer = self.viewer.layers.selection.active
            # check if the current selection is a labels layer
            if isinstance(layer, napari.layers.Labels):
                # Connect the labels layer to events,
                # if plugin was started on a non-labels layer
                self.selected_Layer = layer

                @self.selected_Layer.events.connect
                def notify_change_in_Labels_layer(event):
                    """
                    Connecting the labels layer to events done on the layer,
                    in case the plugin was started on a non-labels layer.
                    (should be the same function as below...)
                    :param event:
                    :return:
                    """
                    self.upon_change_in_Labels_layer()

                # set the class variable to the current labels layer
                self.selected_Layer = layer

                # update the display name
                self.info.setText("Labels layer: " + str(self.selected_Layer))
                # reset the entries of the label list
                self.widget_label_main.remove_widget_entries()
                # and re-initialise with the new layer information
                self.widget_label_main.initialise_widget(self.selected_Layer)

            else:  # i.e. not a Labels layer
                self.selected_Layer = None
                # update the info field for the selected layer (will be "None")
                self.info.setText("Labels layer: " + str(self.selected_Layer))
                # reset the entries since this is not a label layer
                self.widget_label_main.remove_widget_entries()

        # auto-update when changes in the current labels layer
        if self.selected_Layer is not None:

            @self.selected_Layer.events.connect
            def notify_change_in_Labels_layer(event):
                """
                Method that catches changes done
                on the currently selected labels layer.
                Calls class method 'upon_change_in_Labels_layer()'
                to perform actions.
                Doing it this way, allows redefining the
                event-connection to the layer,
                in case the plugin was started on a non-Labels layer
                :param event:
                :return:
                """
                self.upon_change_in_Labels_layer()

    #                   Annotator class methods                 #

    def upon_change_in_Labels_layer(self):
        """
        Method to run actions upon change-catches on the current labels layer
        :return:
        """
        # print("-------   Notification:  event in selected label layer!")

        # update the widget label list for new entries
        self.widget_label_main.update_label_entries()

        # mark/select the currently selected label
        self.widget_label_main.get_selected_label()


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return Annotator
