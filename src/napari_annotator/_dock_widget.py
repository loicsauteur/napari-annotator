"""
INFO:
1) Visibility settings: hiding individual label items.
    currently, works with a very crude hack:
    - I create a color dictionary, by creating a new label_colormap and assign it to the layer
    - I set this color_dict on each Label_Item object
    - Within the Label_item object, when it check if the visibility checkbox was clicked it applies the color_dict to the labels layer
    Problems:
        - drawing gets super SLOW! :( I believe this is due on how the colors of the layer are updated by napari
        - I did not manage to retrieve the current colormap used for the labels layer, therefore I create a new one using napari.utils.colormaps.label_colormap()
            - hence, switches colors after plugin initialization
        - also when drawing a hidden label, it would be good if the visibility would switch back on automatically...
        - by creating this custom colormap, the label_layer color mode is switched to direct (automatically), which
            - prevents the shuffle color in the label-layer controls to work (normal behaviour in direct mode)
            - when show selected checkbox in layer controls (makes non selected labels appear brown, probably normal behaviour in direct mode)

"""
# FIXME: napari plugin via npe2 does not work as previous vesion with hook implementation => colors displayed do not match with tool colors

#from napari_plugin_engine import napari_hook_implementation
from napari_annotator._annotations_list_widget import AnnoList

from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from qtpy.QtCore import Qt
import napari


class Annotator(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    #   --> I defined the input type for autocompletion purposes
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__()

        ########                class varialbes             ########
        self.viewer = napari_viewer
        if isinstance(self.viewer.layers.selection.active, napari.layers.Labels):
            self.selected_Layer = self.viewer.layers.selection.active
        else:
            self.selected_Layer = None
        self.info = QLabel("Labels layer = " + str(self.selected_Layer))
        self.widget_label_main = AnnoList(self.selected_Layer) # create this object anyway for initialisation


        ########                layout             ########
        # create default layout and add text info for current selected labels layer
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.info)

        # get the header of the label items (to be) and add it into the layout
        self.layout().addWidget(self.widget_label_main.header)

        # Set a scroll area onto the widget_label_main (list of label entries) and add it to the widget
        scroll = QScrollArea()
        scroll.setWidget(self.widget_label_main)
        self.widget_label_main.layout().setAlignment(Qt.AlignTop)
        scroll.setWidgetResizable(True)
        self.layout().addWidget(scroll)


        ########                "Action listeners"             ########
        # autodetect change in layer selection
        # and update the class variables
        @self.viewer.layers.selection.events.connect
        def update_selected_layer(event):
            '''
            Reset the widget label list entry when layer selection changes.
            Check if the selected layer is a label layer or not.
            :param event:
            :return:
            '''
            #print("-------   Notification:  layer change event")
            layer = self.viewer.layers.selection.active
            # check if the current selection is a labels layer
            if isinstance(layer, napari.layers.Labels):
                # Connect the labels layer to events, if plugin was started on a non-labels layer
                self.selected_Layer = layer
                @self.selected_Layer.events.connect
                def notify_change_in_Labels_layer(event):
                    '''
                        Connecting the labels layer to events done on the layer,
                        in case the plugin was started on a non-labels layer.
                        (should be the same function as below...)
                        :param event:
                        :return:
                    '''
                    self.upon_change_in_Labels_layer()

                # set the class variable to the current labels layer
                self.selected_Layer = layer

                # update the display name
                self.info.setText("Labels layer: " + str(self.selected_Layer))
                # reset the entries of the label list
                self.widget_label_main.remove_widget_entries()
                # and re-initialise with the new layer information
                self.widget_label_main.initialise_widget(self.selected_Layer)

            else: # i.e. not a Labels layer
                self.selected_Layer = None
                # update the info field for the selected layer (will be "None")
                self.info.setText("Labels layer: " + str(self.selected_Layer))
                # reset the entries since this is not a label layer
                self.widget_label_main.remove_widget_entries()


        # auto-update when changes in the current labels layer
        if self.selected_Layer != None:
            @self.selected_Layer.events.connect
            def notify_change_in_Labels_layer(event):
                '''
                Method that catches changes done on the currently selected labels layer.
                Calls class method 'upon_change_in_Labels_layer()' to perform actions.
                Doing it this way, allows redefining the event-connection to the layer,
                in case the plugin was started on a non-Labels layer
                :param event:
                :return:
                '''
                self.upon_change_in_Labels_layer()




    ########                Annotator class methods             ########

    def upon_change_in_Labels_layer(self):
        '''
        Method to run actions upon change-catches on the current labels layer
        :return:
        '''
        #print("-------   Notification:  event in selected label layer!")

        # update the widget label list for new entries
        self.widget_label_main.update_label_entries()

        # mark/select the currently selected label
        self.widget_label_main.get_selected_label()




#@napari_hook_implementation
#def napari_experimental_provide_dock_widget():
#    # you can return either a single widget, or a sequence of widgets
#    return Annotator


'''     un-used stuff
@magic_factory
def example_magic_widget(Label_layer: "napari.layers.Labels"):
    test_LabelNumber(labels = Label_layer)
    print(f"you have selected {Label_layer}")

def test_LabelNumber(
        labels: "napari.types.LabelsData"
):
    print(labels)
    print("nlabels = " + str(labels.data.max()))
'''
