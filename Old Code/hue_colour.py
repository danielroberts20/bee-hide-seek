import math

# This code is a modified version of a Python copy of Java code.
# Originally from http://stackoverflow.com/a/22649803
# Python adapation https://gist.github.com/error454/6b94c46d1f7512ffe5ee
# ----


def EnhanceColor(normalized):
    if normalized > 0.04045:
        return math.pow( (normalized + 0.055) / (1.0 + 0.055), 2.4)
    else:
        return normalized / 12.92

def RGBtoXY(r, g, b):
    # Normalize RGB values to the range [0, 1]
    rNorm = r / 255.0
    gNorm = g / 255.0
    bNorm = b / 255.0

    # Apply the enhancement curve (gamma correction)
    rFinal = EnhanceColor(rNorm)
    gFinal = EnhanceColor(gNorm)
    bFinal = EnhanceColor(bNorm)
    
    # Calculate XYZ using the RGB to XYZ matrix
    X = rFinal * 0.649926 + gFinal * 0.103455 + bFinal * 0.197109
    Y = rFinal * 0.234327 + gFinal * 0.743075 + bFinal * 0.022598
    Z = rFinal * 0.000000 + gFinal * 0.053077 + bFinal * 1.035763

    # Normalize to XY (chromaticity)
    if X + Y + Z == 0:
        return (0, 0)  # Avoid division by zero
    else:
        xFinal = X / (X + Y + Z)
        yFinal = Y / (X + Y + Z)
    
        return (xFinal, yFinal)

def xy_to_ble(x, y):
    # Scale XY to the range [0, 65535] for 16-bit encoding
    max_val = 65535
    x_scaled = int(x * max_val)
    y_scaled = int(y * max_val)

    # Clamp values to ensure they stay within the 16-bit range
    x_scaled = max(0, min(max_val, x_scaled))
    y_scaled = max(0, min(max_val, y_scaled))

    # Convert to hex format (2 bytes each)
    # Use hex() and remove the "0x" prefix, then pad manually with zeros to ensure 4 digits
    x_hex = hex(x_scaled)[2:].upper()
    y_hex = hex(y_scaled)[2:].upper()

    # Manually pad with leading zeros if necessary
    x_hex = '0' * (4 - len(x_hex)) + x_hex
    y_hex = '0' * (4 - len(y_hex)) + y_hex

    # Convert to little-endian (swap the bytes)
    x_le = x_hex[2:4] + x_hex[0:2]  # Swap the first and second byte
    y_le = y_hex[2:4] + y_hex[0:2]  # Swap the first and second byte
    
    return x_le, y_le


def rgb_to_hue(r, g, b):
    x, y = RGBtoXY(r, g, b)
    return xy_to_ble(x, y)

def lerp_color_heatmap(t, color1=(0, 0, 255), color2=(255, 0, 0)):
    # Ensure t is between 0 and 1
    t = max(0, min(t, 1))

    # The midpoint is white, so we create a linear interpolation between color1 and white, then between white and color2
    if t < 0.5:
        # Interpolate from color1 to white
        t = t * 2  # Scale t to [0, 1] for the first half (color1 to white)
        r = int(color1[0] + t * (255 - color1[0]))
        g = int(color1[1] + t * (255 - color1[1]))
        b = int(color1[2] + t * (255 - color1[2]))
    else:
        # Interpolate from white to color2
        t = (t - 0.5) * 2  # Scale t to [0, 1] for the second half (white to color2)
        r = int(255 + t * (color2[0] - 255))
        g = int(255 + t * (color2[1] - 255))
        b = int(255 + t * (color2[2] - 255))

    return rgb_to_hue(r, g, b)
