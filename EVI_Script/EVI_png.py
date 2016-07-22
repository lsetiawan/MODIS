#!/usr/bin/env python

# Import the necessary libraries
import matplotlib as mpl
import matplotlib.pyplot as plt
import os, sys
import numpy as np
import xarray as xr
import rasterio as rio
from PIL import Image
from pylab import cm

def make_cmap(colors, position=None, bit=False):
    '''
    make_cmap takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.
    Arrange your tuples so that the first color is the lowest value for the
    colorbar and the last is the highest.
    position contains values from 0 to 1 to dictate the location of each color.
    '''
    bit_rgb = np.linspace(0,1,256)
    if position == None:
        position = np.linspace(0,1,len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red':[], 'green':[], 'blue':[]}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)
    return cmap

def export_colormap(name, cmap):
    '''
    This function is used to export colormap to size of 1000px width and 1px height
    export_colormap takes a name of the output and the colormap desired to be saved as a png
    :param name: is the name of the output
    :param cmap: is the colormap
    :return: a png file with the colorbar name
    '''
    im = np.outer(np.ones(1), np.arange(1000))
    fig, ax = plt.subplots(1, figsize=(5, 10), subplot_kw=dict(xticks=[], yticks=[]))
    # fig.subplots_adjust(hspace=0.1)
    ax.imshow(im, cmap=cmap)
    ax.axis('off')
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(4.3115, 0.5)

    plt.savefig('{}.png'.format(name), bbox_inches='tight', dpi=299.5, transparent=True, format='png', pad_inches=0.0)

def createPNG(fil,name):
    EVI = create_cmap()

    # Open EVI data and read values
    with rio.drivers():
        with rio.open(fil) as src:
            print(src.meta)
            data = src.read(1)
    # Masking data, making no value transparent
    x = np.ma.masked_where(data < 0, data)
    # Normalizing data to make it from 0-1
    x_normed = x / float(x.max())
    print(x_normed)

    # Create Image from array and apply EVI, converting np array to values of 0-255
    im = Image.fromarray(EVI(x_normed, bytes=True))
    if not os.path.exists('EVI_png'):
        os.mkdir('EVI_png')
    # Save image out
    im.save(os.path.join("EVI_png", '{0}.png'.format(name)))

def prnt_lib_ver():
    '''
        Function used to print the current versions of xarray, cartopy, and numpy
    '''
    print "xarray version: " + xr.__version__
    print "numpy version: " + np.__version__
    print "rasterio version: " + rio.__version__

def create_cmap():
    ### Create a list of RGB tuples
    colors = [(229, 229, 229), (182, 165, 134), (160, 138, 91),
              (138, 111, 49), (140, 127, 43), (142, 143, 37), (144, 159, 31),
              (146, 175, 25), (138, 177, 21), (119, 165, 18), (99, 154, 15), (80, 142, 12),
              (60, 131, 9), (41, 119, 6), (22, 108, 3), (3, 97, 0), (0, 23, 0)]  # This example uses the 8-bit RGB
    ### Create an array or list of positions from 0 to 1.
    position = [0, 0.04, 0.08, 0.12, 0.16, 0.20, 0.24, 0.28, 0.32, 0.36, 0.40, 0.44, 0.48, 0.52, 0.56, 0.60, 1]
    evi_cmap = make_cmap(colors, position=position, bit=True)
    cm.register_cmap(name='evi', cmap=evi_cmap)
    EVI = cm.get_cmap('evi')
    export_colormap('evi_colorbar',evi_cmap)

    return EVI

def main():
    prnt_lib_ver()

    pth = "/Users/lsetiawan/Desktop/shared_ubuntu/APL/MODIS/data/climatology/"
    for f in os.listdir(pth):
        if ".DS_Store" in f or ".aux.xml" in f:
            pass
        else:
            fil = os.path.join(pth, "{}".format(f))
            name = f.split('.')[0]
            createPNG(fil, name)

if __name__ == '__main__':
    main()