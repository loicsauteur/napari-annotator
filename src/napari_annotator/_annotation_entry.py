from qtpy.QtWidgets import QCheckBox, QPushButton, QColorDialog
from qtpy.QtCore import QSize
from qtpy.QtGui import QColor, QIcon
import napari

from napari.resources import _icons
import numpy as np
import skimage.measure

class LabelItem:
    '''
    This object contains QWidgets for a label.
    Each Button has its own methods.
    The erase functionality is not un-doable! FIXME possible improvement
    '''
    def __init__(self, index, layer, color_dictionary):
        self.label = index # number of the label
        self.layer = layer # associated image/labels layer (probably useless but...)
        # assign color dictionary
        self.color_dict = color_dictionary
        self.active = False # state if it is selected for drawing
        self.visible = True # shown in the viewer or not
        self.color = self.color_dict[self.label] # this variable is never really used...

        # QWidget label name/number
        self.qLabel = QPushButton("Label #"+ str(self.label))
        # set label color as backround
        self.qLabel.setStyleSheet("background-color: " + QColor(self.color[0]*255, self.color[1]*255, self.color[2]*255).name())
        self.default_styleSheet = self.qLabel.styleSheet() # default font color variable, for resetting purposes

        # QWidget shown or not checkbox
        self.qVisible = QCheckBox("")
        self.qVisible.setChecked(self.visible)

        # QWidget move to center
        self.qMove = QPushButton()
        self.qMove.setIcon(QIcon(_icons.get_icon_path('zoom')))
        self.qMove.setIconSize(QSize(20, 20))

        # QWidget color picker
        # for button icon there is a picker.svg icon in napari/resources/icons/
        self.qColor = QPushButton()
        self.qColor.setIcon(QIcon(_icons.get_icon_path('picker')))
        self.qColor.setIconSize(QSize(20, 20))
        self.colorPickerWindow = None

        # QWidget erase label
        self.qErase = QPushButton()
        self.qErase.setIcon(QIcon(_icons.get_icon_path('erase')))
        self.qErase.setIconSize(QSize(20, 20))


        # List of QWidgets
        self.qWidget_list = []
        self.qWidget_list.append(self.qLabel)
        self.qWidget_list.append(self.qVisible)
        self.qWidget_list.append(self.qMove)
        self.qWidget_list.append(self.qColor)
        self.qWidget_list.append(self.qErase)

        # Click - connect the qLabel button for selecting the corresponding label
        self.qLabel.clicked.connect(self._onClick_select_Label)
        # connect the visibility checkbox
        self.qVisible.stateChanged.connect(self._set_visibility_checkBox)
        # connect the move to label button
        self.qMove.clicked.connect(self._onClick_move_to_label)
        # connect the erase button
        self.qErase.clicked.connect(self._onClick_erase_label)
        # connect the color picker button
        self.qColor.clicked.connect(self._onClick_pick_label_color)


    #######       Label_item class methods      #######

    def _onClick_pick_label_color(self):
        '''
        Pop up a color picker window to choose a color from.
        Set the color to the layer colormap, layer color and label button default_stylesheet background color
        '''
        # open a color picker (dialog) window
        color = QColorDialog.getColor() # returns a QColor
        if not color.isValid():
            return
        # continue if the color dialog is OK'ed

        # set the aLabel style and update the default_styleSheet variable
        self.qLabel.setStyleSheet("background-color: " + color.name())
        self.default_styleSheet = self.qLabel.styleSheet()

        # update the layer color
        self.color_dict[self.label] = np.asarray(color.getRgbF()) # set the color in the color_dict
        self.color = np.asarray(color.getRgbF()) # set the color variable to the selected color
        self.layer.color = self.color_dict # update the layer color

        # update also the layer's color map (not sure what this does)
        self.layer.colormap.colors[self.label] = np.asarray(color.getRgbF())




    def _onClick_erase_label(self):
        '''
        TODO / improvement: add undo functionality?
        Replaces the label layer data for given label with 0 values.
        Used for the erase button
        '''
        self.layer.data = np.where(self.layer.data == self.label, 0, self.layer.data)
        print("Label #", self.label, "has been erased.")


    def _onClick_move_to_label(self):
        '''
        check where the pixels are painted (finds centroid coordinates, using skimage),
        and moves to the viewer-camera to it at the current zoom.
        '''
        # Using skimage to get the centroid coordinates (only works on 2D/3D label layers)
        # check if there are pixels drawn for the label, if not don't continue
        if self.label not in self.layer.data:
            print("No annotated pixels for label #", self.label)
            return

        # get the current camera zoom
        cur_zoom = napari.viewer.current_viewer().camera.zoom  # save the current zoom

        # Get the centroid for the label entry
        props = skimage.measure.regionprops(self.layer.data)
        # label "0" (= background) is not listed in region props
        # as regionprops will not list undrawn labels i have to identify also undrawn labels
        skip = 1
        for i in range(1, self.label + 1):
            if i not in self.layer.data:
                skip = skip + 1

        centroid = props[self.label - skip].centroid
        # if a 2D image, provide also a z-coordinate (=0)
        if len(centroid) == 2:
            center = [0, round(centroid[0]), round(centroid[1])]
        else:
            center = np.around(np.asarray(centroid))
        # set the center of the viewer
        napari.viewer.current_viewer().camera.center = center
        # set the slice according to center[0]
        napari.viewer.current_viewer().dims.set_current_step(0, center[0])  # this seems to do the trick...

        # set the zoom to the current zoom
        napari.viewer.current_viewer().camera.zoom = 0.00001 + cur_zoom  # Bug: https://github.com/napari/napari/issues/3723


        '''
        # this is an old version
        # get (Z)YX arrays for where the pixels have the value of the label
        label_coordinates = np.where(self.layer.data == self.label) # returs 2 arrays, for x and y pixel-coordinates
        # check if there is any drawn pixels for this label
        if (len(label_coordinates[0]) == 0):
            print("No annotated pixels for label #", self.label)
            return

        # initialise the center coordinate array (to set the camera to)
        center = []
        cur_zoom = napari.viewer.current_viewer().camera.zoom # save the currrent zoom

        # Checking for 2D vs 3D image
        if len(label_coordinates) == 2:
            # add the z-coordinate (which is absent in the coordinate list)
            center.append(0)
        # add the (remaining) center coordinates, by
        # getting the middle point of the coordinates (i.e. middle of each coordinate array)
        for i in range(0, len(label_coordinates)):
            middle = label_coordinates[i][round(len(label_coordinates)/2)]
            center.append(middle)

        # set the center of the viewer
        napari.viewer.current_viewer().camera.center = center
        # set the slice according to center[0]
        napari.viewer.current_viewer().dims.set_current_step(0, center[0]) # this seems to do the trick...

        # set the zoom to the current zoom
        napari.viewer.current_viewer().camera.zoom = 0.00001 + cur_zoom # Bug: https://github.com/napari/napari/issues/3723
        '''




    def set_color_dictionary(self, color_dict):
        '''
        Setter. for the self.color_dict class variable.
        :param color_dict: color dictionary {#Label: RGBA-float-values}
        '''
        self.color_dict = color_dict

    def _set_visibility_checkBox(self):
        '''
        Sets the visible class variable according to current checkbox state.
        Adjusts the alpha value of the current label and
        applies the color_dict to the label layer
        '''
        if self.qVisible.isChecked():
            self.visible = True
            # set the alpha in the current color dictionary
            self.color_dict[self.label][3] = 1.0
        else:
            self.visible = False
            # set the alpha in the current color dictionary
            self.color_dict[self.label][3] = 0.0
        # apply the color dictionary
        self.layer.color = self.color_dict



    def _onClick_select_Label(self):
        '''
        (clicking button) selects the corresponding label
        '''
        self.layer.selected_label = self.label

    def get_qWidget_list(self):
        '''
        Getter of the QWidget list.
        :return: array of QWidgets (class variable)
        '''
        return self.qWidget_list

    def reset_font_color(self):
        '''
        reset the font of the qLabel to the default.
        '''
        self.qLabel.setStyleSheet(self.default_styleSheet)

    def set_font_color(self, font):
        '''
        sets the font of the qLabel widget.
        :param font: String, e.g.: 'color: yellow'
        '''
        self.qLabel.setStyleSheet(font)