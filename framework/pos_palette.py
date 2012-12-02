#!/usr/bin/python

import sys
import os
import colorsys
from scipy.interpolate import interp1d

# Directory with all the available palettes, Palettes are stored as gnuplot
# palette files which are basicly csv files in form of:
# value red_component(0-1) green_component(0-1)  blue_component(0-1)
DIRECTORY_PALLETES = 'palettes/'


def int_colour_to_float(color, maxValue=255.):
    """
    Convert colors provided as tuple of (r,g,b) components to tuple of floats
    ranging from 0 to 1.

    :param color: tuple of (r,g,b) components provided as integers from 0 to 255
    :return: tuple of (r,g,b) float components.
    """
    return tuple(x / maxValue for x in color)


def float_colour_to_int(colour, maxValue=255):
    """
    Convert (r,g,b) color tuple provided as integers to tuple of floats ranging
    from 0 to 1.
    """
    return tuple(int(x * maxValue) for x in colour)


class pos_color(object):
    """
    Color object. Class representing a color :)
    """
    def __init__(self, (r, g, b)):
        """
        :param r: Red component of given color. Float from 0 to 1,
        :param g: Green component of given color. Float from 0 to 1,
        :param b: Blue component of given color. Float from 0 to 1,
        """

        # Just store the color components. Yes, it's just so simple.
        self.r = r
        self.g = g
        self.b = b

    @classmethod
    def from_int(pos_color, (rInt, bInt, gInt)):
        """
        Create pos_color objest from tuple of iintegert from (0 to 255) instead
        of floats.

        :param rInt: Red component of given color, Integer from 0 to 255.
        :param gInt: Green component of given color, Integer from 0 to 255.
        :param bInt: Blue component of given color, Integer from 0 to 255.

        :return: pos_color object
        """

        (r, g, b) = int_colour_to_float((rInt, bInt, gInt))
        return pos_color((r, g, b))

    @classmethod
    def from_html(cls, colorstring):
        """
        Create pos_color object from html color string. String can be in form of
        either "#rrggbb" or just "rrggbb".

        :param colorstring: html color string.
        :return: pos_color object
        """

        colorstring = colorstring.strip()

        # Check if the colorstring starts from "#"
        if colorstring[0] == '#':
            colorstring = colorstring[1:]

        if len(colorstring) != 6:
            raise ValueError, "input #%s is not in #RRGGBB format" % colorstring

        # Extract individual color components and convert them to integers.
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]

        return cls.from_int((r, g, b))

    @classmethod
    def fromHSVTuple(cls, (h, s, v)):
        """
        Create color object from hue, saturation, value tuple.

        :return: pos_color object
        """
        return cls(colorsys.hsv_to_rgb(h, s, v))

    def __str__(self):
        return str(self())

    def __call__(self):
        return self._getValues()

    def _getInt(self, x):
        return int(x * 255.)

    def _getIntTuple(self):
        return tuple(map(self._getInt, self()))

    def _getHTMLcolor(self):
        return '#%02X%02X%02X' % self.rgb

    def _getValues(self):
        return (self.r, self.g, self.b)

    def _getHSVTuple(self):
        return colorsys.rgb_to_hsv(*self())

    def _get_gnuplot_color_format(self):
        return ' rgb "' + self.html + '"'

    rgb = property(_getIntTuple)
    html= property(_getHTMLcolor)
    hsv = property(_getHSVTuple)
    c   = property(_getValues)
    gnuplot = property(_get_gnuplot_color_format)


class pos_palette(object):
    """
    An very flexible object for managing color palettes and lookup tables.
    """
    def __init__(self, mapping, min=0.0, max=1.0):
        """
        :param mapping: {float: (float, float, float), ...}. A mapping from a
        value to the corensponding color provided by float r,g,b components
        ranging from 0 to 1. The mapping can be either continous (with lot of
        entries) or discrete (with just a few entries). In both cases continous
        palette is built and color for any value within min,max range can be
        calculated.

        :param min: Lower bound of the palette
        :param max: Upper bound of the lookup table.
        """

        # First thing to check :P
        assert max > min

        # Calculate scaling and offset mapping range (0,1) to (min,max)
        # and store them within the class
        scale, offset = (max - min), min
        self.scale = float(scale)
        self.offset = float(offset)

        # Define mappings and then define interpolation function between the
        # mapping entries.
        self._define_mapping(mapping)
        self._define_interpolation()

    def _define_mapping(self, mapping):
        # Initialize empty mapping
        self._mapping = {}

        # For every mapping entry create internal entry
        # scaled to min,max range
        for value, color in mapping.iteritems():
            transformed = self._shift_scale(value)
            self._mapping[transformed] = pos_color(color)

    def _define_interpolation(self, kind='linear'):
        """
        Define interpolation function for discrete mapping.

        :param kind: Kind of interpolation. See scipy interp1d function for list
        of available interpolation types.
        """
        # Get all the mapping values and sort them
        # Then get all the colors preserving their order
        m = sorted(self._mapping)
        r = map(lambda x: self._mapping[x].r, m)
        g = map(lambda x: self._mapping[x].g, m)
        b = map(lambda x: self._mapping[x].b, m)

        # Create three interpolation functions. Each interpolation function
        # interpolates single color channel thus we need three eof them. Perhaps
        # this step could be implemented in a better way (e.g. using numpy
        # arrays) but this implementation also works fine.
        # TODO: Implement using numpy arrays.
        ic = \
           tuple(map(lambda x: interp1d(m, x, kind=kind), [r, g, b]))

        # Store all the three interpolation functions.
        self._intepolated = ic

    def _shift_scale(self, value):
        """
        Trivial helper function that affinely transforms provided value.
        """
        return value * self.scale + self.offset

    def _interpolate(self, value):
        """
        Return color corresponding to the provided value. The value can be any number within
        boundaries. If the value is not match any of the explicit mapping
        entries, it is interpolated.

        :param value: a number within table's boundaries.
        :return: pos_color
        """
        ci = map(lambda x: self._intepolated[x](value), range(3))

        return pos_color(tuple(map(float, ci)))

    def __call__(self, value):
        return self._interpolate(value)

    def _get_vtk_color_transfer_function(self, additional_mapping=None):
        """
        Generate vtk 'vtkColorTransferFunction object' with exactly the same
        mapping as defined in the table.

        :param additional_mapping: [(x,y),(x,y),.....]. An additional mapping
        trough which source lookup table will be mapped (sic!). It sounds awful
        but works really cool. The 'additional_mapping' parameter can be for
        example piecewise linear or even nonlinear (in both cases discrete)
        mapping.

        :return: vtkColorTransferFunction
        """

        # First off all, check if the python vtk binding is installed. If it's
        # not, the function cannot proceed.
        try:
            import vtk
        except:
            print >>sys.stderr, "Cannot import vtk. exiting"
            return None

        # If additional mapping is provided, execute this mapping.
        # Otherwise use the identity mapping.
        if additional_mapping:
            xpts = map(lambda p: p[0], additional_mapping)
            ypts = map(lambda p: p[1], additional_mapping)
        else:
            xpts = sorted(self._mapping.keys())
            ypts = xpts

        # Create intepolation function for the 'additional_mapping'
        interpolator = interp1d(xpts, ypts)

        # Finally, create and fill the colot transfer function
        ctf = vtk.vtkColorTransferFunction()

        for xpt in xpts:
            value = float(interpolator(xpt))
            ctf.AddRGBPoint(value, *self(xpt).c)

        return ctf

    def color_transfer_function(self, additional_mapping=None):
        return self._get_vtk_color_transfer_function(additional_mapping)

    @classmethod
    def from_gnuplot_file(cls, filename, delimiter=" ", min=0.0, max=1.0):
        """
        Create lookup table based on given file containing gnuplot color
        palette.

        :param filename: path to file with the palette.

        :param delimiter: use custom delimiter instead of the default (space).
        Just in case when the file is stored in some unusual manner.

        :param min: Use custom lower boundary. Default is 0.
        :param max: Use custom upper boundary. Default is 1.

        :return: pos_palette
        """

        # Initialize empty dictionary fo the mapping. Open provided file and
        # read the entry line by line.
        mapping = {}
        for sourceLine in open(filename):
            if sourceLine.strip().startswith('#') or sourceLine.strip() == "":
                continue

            line = sourceLine.split("#")[0].strip().split(delimiter)
            value = float(line[0])

            r, g, b = map(lambda x: float(line[x]), range(1, 4))
            mapping[value] = (r, g, b)

        return cls(mapping, min=min, max=max)

    @classmethod
    def lib(cls, name, min=0.0, max=1.0):
        """
        Load provided palette from the library of palettes within this
        framework.

        :param name: name of the palette,

        :param min: Use custom lower boundary. Default is 0.
        :param max: Use custom upper boundary. Default is 1.

        :return: pos_palette
        """
        execution_path = os.path.dirname(__file__)
        return cls.from_gnuplot_file(os.path.join(
                execution_path, DIRECTORY_PALLETES, name + '.gpf'),
                min=min, max=max)

if __name__ == '__main__':
    pass
