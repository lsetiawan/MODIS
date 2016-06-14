#!/usr/bin/env python

# Import the necessary libraries
import matplotlib.pyplot as plt
import os
import numpy as np
import xarray as xr
import matplotlib as mpl
import cartopy
import cartopy.crs as ccrs
import rasterio

import pyproj
import shapely.geometry as sgeom
import sys

def transform_proj(p1, p2, x, y, nocopy=False):
    """Wrapper around the pyproj transform.
    When two projections are equal, this function avoids quite a bunch of
    useless calculations. See https://github.com/jswhit/pyproj/issues/15
    """

    if p1.srs == p2.srs:
        if nocopy:
            return x, y
        else:
            return copy.deepcopy(x), copy.deepcopy(y)

    return pyproj.transform(p1, p2, x, y)

def try_to_get_latlon_coords(da):
    if 'crs' in da.attrs:
        proj = pyproj.Proj(da.attrs['crs'])
        x, y = np.meshgrid(da['x'], da['y'])
        proj_out = pyproj.Proj("+init=EPSG:4326", preserve_units=True)
        xc, yc = transform_proj(proj, proj_out, x, y)
        coords = dict(y = da['y'], x=da['x'])
        dims = ('y', 'x')

        da.coords['latitude'] = xr.DataArray(yc, coords=coords, dims=dims, name='latitude',
                                             attrs={'units': 'degrees_north', 'long_name': 'latitude', 'standard_name': 'latitude'})
        da.coords['longitude'] = xr.DataArray(xc, coords=coords, dims=dims, name='latitude',
                                             attrs={'units': 'degrees_east', 'long_name': 'longitude', 'standard_name': 'longitude'})

    return da

def rasterio_to_xarray(fname):
    with rasterio.drivers():
        with rasterio.open(fname) as src:
            data = src.read()

            data = np.where(data == src.nodata, np.nan, data)

            # Get coords
            nx, ny = src.width, src.height
            x0, y0 = src.bounds.left, src.bounds.top
            dx, dy = src.res[0], -src.res[1]

            coords = {'y': np.arange(start=y0, stop=(y0 + ny * dy), step=dy),
                      'x': np.arange(start=x0, stop=(x0 + nx * dx), step=dx)}
            # Get dims
            if src.count == 1:
                dims = ('band', 'y', 'x')
                coords['band'] = src.indexes
            elif src.count == 2:
                dims = ('y', 'x')
            else:
                raise ValueError('unknown dims')

            attrs = {}
            for attr_name in ['crs', 'affine', 'proj']:
                try:
                    attrs[attr_name] = getattr(src, attr_name)
                except AttributeError:
                    pass

    return try_to_get_latlon_coords(xr.DataArray(data, dims=dims, name='raster',
                                                 coords=coords, attrs=attrs)).to_dataset()

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

def getPNG(name, data, epsg, pth):
    dpi = 100
    # 8.87483870967742
    plt.figure(figsize=(9, 7), frameon=False, dpi=dpi)
    box = sgeom.box(minx=-127.829404882663, maxx=-59.0737169554389, miny=5.20063004139071, maxy=49.9999999955068)
    x0, y0, x1, y1 = box.bounds
    #fig.set_size_inches(6878.0 / float(100), 4482.0 / float(100))
    ### Create a list of RGB tuples
    colors = [(229, 229, 229), (182, 165, 134), (160, 138, 91),
              (138, 111, 49), (140, 127, 43), (142, 143, 37), (144, 159, 31),
              (146, 175, 25), (138, 177, 21), (119, 165, 18), (99, 154, 15), (80, 142, 12),
              (60, 131, 9), (41, 119, 6), (22, 108, 3), (3, 97, 0), (0, 23, 0)]  # This example uses the 8-bit RGB
    ### Create an array or list of positions from 0 to 1.
    position = [0,0.04,0.08,0.12,0.16,0.20,0.24,0.28,0.32,0.36,0.40,0.44,0.48,0.52,0.56,0.60,1]
    evi_cmap = make_cmap(colors, position=position, bit=True)

    # Set output projection
    if epsg == 4326:
        ax = plt.axes(projection=ccrs.PlateCarree())
    else:
        ax = plt.axes(projection=ccrs.epsg(epsg))
    #ax.set_global()

    # Define the coordinate system that the grid lons and grid lats are on
    coord = ccrs.PlateCarree()  # aka Lat,Long
    ax.background_patch.set_visible(False)
    ax.outline_patch.set_visible(False)

    # Plots the data
    data.plot(ax=ax, transform=coord, add_colorbar=False, vmin=-2000, vmax=10000, add_labels=False, cmap=evi_cmap)
    #ax.set_extent([x0, x1, y0, y1])
    # Put Coastline on figure
    # ax.coastlines()
    if not os.path.exists("EVI_png"):
        os.mkdir("EVI_png")
    plt.savefig(os.path.join("EVI_png", '{0}.png'.format(name)), bbox_inches='tight',dpi=dpi * 10,
                transparent=True, format='png', pad_inches=0.0)
    # plt.show()

def prnt_lib_ver():
    '''
        Function used to print the current versions of xarray, cartopy, and numpy
    '''
    print "xarray version: " + xr.__version__
    print "cartopy version: " + cartopy.__version__
    print "numpy version: " + np.__version__
    print "rasterio version: " + rasterio.__version__

def main():
    prnt_lib_ver()

    pth = "/Users/lsetiawan/Desktop/shared_ubuntu/APL/MODIS/data/climatology"
    for tif in os.listdir(pth):
        if ".tif" in tif and ".aux.xml" not in tif and ".DS_Store" not in tif:
            print "Working on {}".format(tif)
            name = tif.split('.')
            ds = rasterio_to_xarray(os.path.join(pth, tif))
            evi = ds.raster[0, :, :]
            lons = ds.raster["x"][:]
            lats = ds.raster["y"][:]
            print(ds, '\n')
            print(ds['raster'], '\n')
            print ""
            getPNG(name[0], evi, 4326, pth)

if __name__ == '__main__':
    main()