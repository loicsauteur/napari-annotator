from pathlib import Path

import napari
import numpy as np
import skimage.measure
from napari.resources import _icons
from napari.utils import DirectLabelColormap
from qtpy.QtCore import QSize
from qtpy.QtGui import QColor, QIcon
from qtpy.QtWidgets import QCheckBox, QColorDialog, QPushButton


class LabelItem:
    """
    This object contains QWidgets for a label.
    Each Button has its own methods.

    Visibility and changing colors will recreate the layer.colormap,
    using DirectLabelColormap (and the modified values in layer.colormap.color_dict).
    """

    def __init__(self, index, layer, color_dictionary):
        self.label = index  # number of the label
        self.layer = layer  # associated image/labels layer
        # assign color dictionary
        self.color_dict = color_dictionary
        self.active = False  # state if it is selected for drawing
        self.visible = True  # shown in the viewer or not
        self.color = self.color_dict[
            self.label
        ]  # this variable is never really used...
        self.mem = None  # for remembering drawn pixels after erasing
        # (array with len axis = image len axis)

        # QWidget label name/number
        self.qLabel = QPushButton("Label #" + str(self.label))
        # set label color as background
        self.qLabel.setStyleSheet(
            "background-color: "
            + QColor(
                int(self.color[0] * 255),
                int(self.color[1] * 255),
                int(self.color[2] * 255),
            ).name()
        )
        self.default_styleSheet = (
            self.qLabel.styleSheet()
        )  # default font color variable, for resetting purposes

        # QWidget shown or not checkbox
        self.qVisible = QCheckBox("")
        self.qVisible.setChecked(self.visible)

        # QWidget move to center
        self.qMove = QPushButton()
        self.qMove.setIcon(QIcon(_icons.get_icon_path("zoom")))
        self.qMove.setIconSize(QSize(20, 20))

        # QWidget color picker
        # for button icon there is a picker.svg icon in napari/resources/icons/
        self.qColor = QPushButton()
        self.qColor.setIcon(QIcon(_icons.get_icon_path("picker")))
        self.qColor.setIconSize(QSize(20, 20))
        self.colorPickerWindow = None

        # QWidget erase label
        self.qErase = QPushButton()
        self.qErase.setIcon(QIcon(_icons.get_icon_path("erase")))
        self.qErase.setIconSize(QSize(20, 20))

        # QWidget restore label
        redoArrowPath = Path(__file__).parent
        redoArrowPath = redoArrowPath / "redo-arrow-icon.svg"
        redoArrowPath = str(redoArrowPath.absolute())
        self.qRestore = QPushButton()
        self.qRestore.setIcon(QIcon(redoArrowPath))
        self.qRestore.setIconSize(QSize(20, 20))
        self.qRestore.setToolTip("Functionality is lost after layer change.")
        self.qRestore.setDisabled(True)

        # List of QWidgets
        self.qWidget_list = []
        self.qWidget_list.append(self.qLabel)
        self.qWidget_list.append(self.qVisible)
        self.qWidget_list.append(self.qMove)
        self.qWidget_list.append(self.qColor)
        self.qWidget_list.append(self.qErase)
        self.qWidget_list.append(self.qRestore)

        # Connect the qLabels button for selecting the corresponding label
        self.qLabel.clicked.connect(self._onClick_select_Label)
        # connect the visibility checkbox
        self.qVisible.stateChanged.connect(self._set_visibility_checkBox)
        # connect the move to label button
        self.qMove.clicked.connect(self._onClick_move_to_label)
        # connect the erase button
        self.qErase.clicked.connect(self._onClick_erase_label)
        # connect the color picker button
        self.qColor.clicked.connect(self._onClick_pick_label_color)
        # connect the restore button
        self.qRestore.clicked.connect(self._onClick_restore_label)

    #          Label_item class methods         #

    def _onClick_restore_label(self):
        """
        Restores the label that has been saved after erasing.
        Implemented up to 4D images
        """
        # 1D image
        if self.mem.shape[0] == 1:
            for x in self.mem:
                self.layer.data[x] = self.label
        # 2D image
        elif self.mem.shape[0] == 2:
            for i in range(self.mem.shape[1]):
                self.layer.data[self.mem[0][i]][self.mem[1][i]] = self.label
        # 3D image
        elif self.mem.shape[0] == 3:
            for i in range(self.mem.shape[-1]):
                self.layer.data[self.mem[0][i]][self.mem[1][i]][
                    self.mem[2][i]
                ] = self.label
        # 4D image
        elif self.mem.shape[0] == 4:
            for i in range(self.mem.shape[-1]):
                t = self.mem[0][i]
                z = self.mem[1][i]
                y = self.mem[2][i]
                x = self.mem[3][i]
                self.layer.data[t][z][y][x] = self.label
        else:
            raise NotImplementedError(
                f"Error: The restore function for {self.mem.shape[0]}"
                f"-dimensional images is not implemented."
            )

        self.layer.refresh()
        self.qRestore.setDisabled(True)
        # delete the memorised label drawing
        self.mem = None
        print(f"Label #{self.label} has been restored.")

    def _onClick_pick_label_color(self):
        """
        Pop up a color picker window to choose a color from.
        Set the color to the layer colormap, layer color and
        label button default_stylesheet background color
        """
        # open a color picker (dialog) window
        color = QColorDialog.getColor()  # returns a QColor
        if not color.isValid():
            return
        # continue if the color dialog is OK'ed

        # set the aLabel style and update the default_styleSheet variable
        self.qLabel.setStyleSheet("background-color: " + color.name())
        self.default_styleSheet = self.qLabel.styleSheet()

        # update the layer color
        self.color_dict[self.label] = np.asarray(
            color.getRgbF()
        )  # set the color in the color_dict
        self.color = np.asarray(
            color.getRgbF()
        )  # set the color variable to the selected color

        # Recreate a color_dict and apply it to the layer colormap
        temp_color = self.color_dict[self.label]
        temp_color[0] = self.color[0]
        temp_color[1] = self.color[1]
        temp_color[2] = self.color[2]
        self.layer.colormap = DirectLabelColormap(color_dict=self.color_dict)

    def _onClick_erase_label(self):
        """
        Replaces the label layer data for given label with 0 values.
        Used for the erase button
        """
        # store the drawn pixels
        rememberMe = np.asarray(np.where(self.layer.data == self.label))
        if rememberMe.size != 0:
            self.mem = rememberMe
            self.qRestore.setDisabled(False)

        # erase
        dataRef = self.layer.data
        self.layer.data = np.where(dataRef == self.label, 0, dataRef)
        print(f"Label #{self.label} has been erased.")

    def _onClick_move_to_label(self):
        """
        check where the pixels are painted (finds centroid
         coordinates, using skimage), and moves to the
         viewer-camera to it at the current zoom.
        """
        # Using skimage to get the centroid coordinates
        # (only works on 2D/3D label layers)
        # check if there are pixels drawn for the label, if not don't continue
        if self.label not in self.layer.data:
            print(f"No annotated pixels for label # {self.label}.")
            return

        # get the current camera zoom
        cur_zoom = napari.viewer.current_viewer().camera.zoom

        # Get the centroid for the label entry
        props = skimage.measure.regionprops(self.layer.data)
        # label "0" (= background) is not listed in region props
        # as regionprops will not list un-drawn labels:
        # identify also un-drawn labels
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
        napari.viewer.current_viewer().dims.set_current_step(
            0, center[0]
        )  # this seems to do the trick...

        # set the zoom to the current zoom
        napari.viewer.current_viewer().camera.zoom = (
            0.00001 + cur_zoom
        )  # Bug: https://github.com/napari/napari/issues/3723

    def set_color_dictionary(self, color_dict):
        """
        Setter. for the self.color_dict class variable.
        :param color_dict: color dictionary {#Label: RGBA-float-values}
        """
        self.color_dict = color_dict

    def _set_visibility_checkBox(self):
        """
        Sets the visible class variable according to current checkbox state.
        Adjusts the alpha value of the current label and
        applies the color_dict to the label layer
        """
        if self.qVisible.isChecked():
            self.visible = True
            # set the alpha in the current color dictionary
            self.color_dict[self.label][3] = 1.0
        else:
            self.visible = False
            # set the alpha in the current color dictionary
            self.color_dict[self.label][3] = 0.0
        # Apply the color dictionary, by recreating the colormap
        self.layer.colormap = DirectLabelColormap(color_dict=self.color_dict)

    def _onClick_select_Label(self):
        """
        (clicking button) selects the corresponding label
        """
        self.layer.selected_label = self.label

    def get_qWidget_list(self):
        """
        Getter of the QWidget list.
        :return: array of QWidgets (class variable)
        """
        return self.qWidget_list

    def reset_font_color(self):
        """
        reset the font of the qLabel to the default.
        """
        self.qLabel.setStyleSheet(self.default_styleSheet)

    def set_font_color(self, font):
        """
        sets the font of the qLabel widget.
        :param font: String, e.g.: 'color: yellow'
        """
        self.qLabel.setStyleSheet(font)
