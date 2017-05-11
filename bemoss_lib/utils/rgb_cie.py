"""
Library for RGB / CIE1931 coversion.
Ported and extended from Bryan Johnson's JavaScript implementation:
https://github.com/bjohnso5/hue-hacking

Copyright (c) 2014 Benjamin Knight / MIT License.
"""
import math
import random
from collections import namedtuple


# Represents a CIE 1931 XY coordinate pair.
XYPoint = namedtuple('XYPoint', ['x', 'y'])


class ColorHelper:

    Red = XYPoint(0.675, 0.322)
    Lime = XYPoint(0.4091, 0.518)
    Blue = XYPoint(0.167, 0.04)

    @staticmethod
    def hexToRed( hex):
        """Parses a valid hex color string and returns the Red RGB integer value."""
        return int(hex[0:2], 16)
    @staticmethod
    def hexToGreen( hex):
        """Parses a valid hex color string and returns the Green RGB integer value."""
        return int(hex[2:4], 16)

    @staticmethod
    def hexToBlue( hex):
        """Parses a valid hex color string and returns the Blue RGB integer value."""
        return int(hex[4:6], 16)

    @staticmethod
    def hexToRGB( h):
        """Converts a valid hex color string to an RGB array."""
        rgb = [ColorHelper.hexToRed(h), ColorHelper.hexToGreen(h), ColorHelper.hexToBlue(h)]
        return rgb

    @staticmethod
    def rgbToHex( r, g, b):
        """Converts RGB to hex."""
        return '%02x%02x%02x' % (r, g, b)

    @staticmethod
    def randomRGBValue():
        """Return a random Integer in the range of 0 to 255, representing an RGB color value."""
        return random.randrange(0, 256)

    @staticmethod
    def crossProduct( p1, p2):
        """Returns the cross product of two XYPoints."""
        return (p1.x * p2.y - p1.y * p2.x)

    @staticmethod
    def checkPointInLampsReach( p):
        """Check if the provided XYPoint can be recreated by a Hue lamp."""
        v1 = XYPoint(ColorHelper.Lime.x - ColorHelper.Red.x, ColorHelper.Lime.y - ColorHelper.Red.y)
        v2 = XYPoint(ColorHelper.Blue.x - ColorHelper.Red.x, ColorHelper.Blue.y - ColorHelper.Red.y)

        q = XYPoint(p.x - ColorHelper.Red.x, p.y - ColorHelper.Red.y)
        s = ColorHelper.crossProduct(q, v2) / ColorHelper.crossProduct(v1, v2)
        t = ColorHelper.crossProduct(v1, q) / ColorHelper.crossProduct(v1, v2)

        return (s >= 0.0) and (t >= 0.0) and (s + t <= 1.0)

    @staticmethod
    def getClosestPointToLine( A, B, P):
        """Find the closest point on a line. This point will be reproducible by a Hue lamp."""
        AP = XYPoint(P.x - A.x, P.y - A.y)
        AB = XYPoint(B.x - A.x, B.y - A.y)
        ab2 = AB.x * AB.x + AB.y * AB.y
        ap_ab = AP.x * AB.x + AP.y * AB.y
        t = ap_ab / ab2

        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0

        return XYPoint(A.x + AB.x * t, A.y + AB.y * t)

    @staticmethod
    def getClosestPointToPoint( xyPoint):
        # Color is unreproducible, find the closest point on each line in the CIE 1931 'triangle'.
        pAB = ColorHelper.getClosestPointToLine(ColorHelper.Red, ColorHelper.Lime, xyPoint)
        pAC = ColorHelper.getClosestPointToLine(ColorHelper.Blue, ColorHelper.Red, xyPoint)
        pBC = ColorHelper.getClosestPointToLine(ColorHelper.Lime, ColorHelper.Blue, xyPoint)

        # Get the distances per point and see which point is closer to our Point.
        dAB = ColorHelper.getDistanceBetweenTwoPoints(xyPoint, pAB)
        dAC = ColorHelper.getDistanceBetweenTwoPoints(xyPoint, pAC)
        dBC = ColorHelper.getDistanceBetweenTwoPoints(xyPoint, pBC)

        lowest = dAB
        closestPoint = pAB

        if (dAC < lowest):
            lowest = dAC
            closestPoint = pAC

        if (dBC < lowest):
            lowest = dBC
            closestPoint = pBC

        # Change the xy value to a value which is within the reach of the lamp.
        cx = closestPoint.x
        cy = closestPoint.y

        return XYPoint(cx, cy)

    @staticmethod
    def getDistanceBetweenTwoPoints( one, two):
        """Returns the distance between two XYPoints."""
        dx = one.x - two.x
        dy = one.y - two.y
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def getXYPointFromRGB( red, green, blue):
        """Returns an XYPoint object containing the closest available CIE 1931 coordinates
        based on the RGB input values."""

        r = ((red + 0.055) / (1.0 + 0.055))**2.4 if (red > 0.04045) else (red / 12.92)
        g = ((green + 0.055) / (1.0 + 0.055))**2.4 if (green > 0.04045) else (green / 12.92)
        b = ((blue + 0.055) / (1.0 + 0.055))**2.4 if (blue > 0.04045) else (blue / 12.92)

        X = r * 0.4360747 + g * 0.3850649 + b * 0.0930804
        Y = r * 0.2225045 + g * 0.7168786 + b * 0.0406169
        Z = r * 0.0139322 + g * 0.0971045 + b * 0.7141733

        if X + Y + Z == 0:
            cx = cy = 0
        else:
            cx = X / (X + Y + Z)
            cy = Y / (X + Y + Z)

        # Check if the given XY value is within the colourreach of our lamps.
        xyPoint = XYPoint(cx, cy)
        inReachOfLamps = ColorHelper.checkPointInLampsReach(xyPoint)

        if not inReachOfLamps:
            xyPoint = ColorHelper.getClosestPointToPoint(xyPoint)

        return xyPoint

    @staticmethod
    def getRGBFromXYAndBrightness( x, y, bri=1):
        """Returns a rgb tuplet for given x, y values.  Not actually an inverse of `getXYPointFromRGB`.
        Implementation of the instructions found on the Philips Hue iOS SDK docs: http://goo.gl/kWKXKl
        """
        xyPoint = XYPoint(x, y)

        # Check if the xy value is within the color gamut of the lamp.
        # If not continue with step 2, otherwise step 3.
        # We do this to calculate the most accurate color the given light can actually do.
        if not ColorHelper.checkPointInLampsReach(xyPoint):
            # Calculate the closest point on the color gamut triangle
            # and use that as xy value See step 6 of color to xy.
            xyPoint = ColorHelper.getClosestPointToPoint(xyPoint)

        # Calculate XYZ values Convert using the following formulas:
        Y = bri
        X = (Y / xyPoint.y) * xyPoint.x
        Z = (Y / xyPoint.y) * (1 - xyPoint.x - xyPoint.y)

        # Convert to RGB using Wide RGB D65 conversion.
        r =  X * 1.612 - Y * 0.203 - Z * 0.302
        g = -X * 0.509 + Y * 1.412 + Z * 0.066
        b =  X * 0.026 - Y * 0.072 + Z * 0.962

        # Apply reverse gamma correction.
        r, g, b = map(
            lambda x: (12.92 * x) if (x <= 0.0031308) else ((1.0 + 0.055) * pow(x, (1.0 / 2.4)) - 0.055),
            [r, g, b]
        )

        # Bring all negative components to zero.
        r, g, b = map(lambda x: max(0, x), [r, g, b])

        # If one component is greater than 1, weight components by that value.
        max_component = max(r, g, b)
        if max_component > 1:
            r, g, b = map(lambda x: x / max_component, [r, g, b])

        r, g, b = map(lambda x: int(x * 255), [r, g, b])

        return (r, g, b)


class Converter:

    color = ColorHelper()

    @staticmethod
    def hexToCIE1931( h):
        """Converts hexadecimal colors represented as a String to approximate CIE 1931 coordinates.
        May not produce accurate values."""
        rgb = Converter.color.hexToRGB(h)
        return Converter.rgbToCIE1931(rgb[0], rgb[1], rgb[2])

    @staticmethod
    def rgbToCIE1931( red, green, blue):
        """Converts red, green and blue integer values to approximate CIE 1931 x and y coordinates.
        Algorithm from: http://www.easyrgb.com/index.php?X=MATH&H=02#text2.
        May not produce accurate values.
        """
        point = Converter.color.getXYPointFromRGB(red, green, blue)
        return [point.x, point.y]

    @staticmethod
    def getCIEColor( hexColor=None):
        """Returns the approximate CIE 1931 x, y coordinates represented by the supplied hexColor parameter,
        or of a random color if the parameter is not passed.
        The point of this function is to let people set a lamp's color to any random color.
        Arguably this should be implemented elsewhere."""
        xy = []

        if hexColor:
            xy = Converter.hexToCIE1931(hexColor)

        else:
            r = Converter.color.randomRGBValue()
            g = Converter.color.randomRGBValue()
            b = Converter.color.randomRGBValue()
            xy = Converter.rgbToCIE1931(r, g, b)

        return xy

    @staticmethod
    def CIE1931ToHex( x, y, bri=1):
        """Converts CIE 1931 x and y coordinates and brightness value from 0 to 1 to a CSS hex color."""
        r, g, b = Converter.color.getRGBFromXYAndBrightness(x, y, bri)
        return Converter.color.rgbToHex(r, g, b)
