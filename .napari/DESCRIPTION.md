# Description

This light-weight plugin provides additional control over label layers.
It is intended to ease your work when annotating data manually.
![Example screenshot](https://github.com/loicsauteur/napari-annotator/blob/main/resources/image1.png?raw=true)

It provides you with a widget listing all individual labels.
For each label, you can:
- select it from the list to activate it for further drawing.
- toggle the visibility of individual labels
- locate the drawn label (i.e. move to the centroid location at the current zoom level)
- change the label color with a color picker
- erase the label (sets all the drawn pixels to the label layer background value)
- restore an erased label (switching layers will reset this capability)

# Intended Audience & Supported Data

Everyone that has 2D or 3D data and wants to annotate (or curate annotated data)
should find a useful extension with this plugin.

The plugin will recognise and work only on label layers.

**Note:**
The "locate center" button will only work on 2D/3D label layers, i.e.: YX, ZYX, TYX, CYX.

Channels are considered a dimension.

# Quickstart

1. Start napari
2. Open an image you want to annotate
   1. Best, an image with the same dimension as you labels layer should have
   2. e.g. ``File > Open Sample > napari > Binary Blobs (3D)``
3. Add (or load) a labels layer
4. Start the plugin ``Plugins > napari-annotator: Annotator``
5. Make sure the labels layer is selected
6. Start drawing

#### Known limitations
1. Lag when drawing (see [GitHub README](https://github.com/loicsauteur/napari-annotator) for more info).
2. Maximum 255 labels supported (see [GitHub README](https://github.com/loicsauteur/napari-annotator) for more info).

# Getting Help

If you encounter bugs, please [file an issue] along with a detailed description.
Or open a thread on [forum.image.sc](https://forum.image.sc) with a detailed description
and a [@loicsauteur](https://github.com/loicsauteur) tag.

For general help, reach out via the [forum.image.sc](https://forum.image.sc) with a tag [@loicsauteur](https://github.com/loicsauteur).

# How to Cite

No citation needed. Honorable mention welcome.
