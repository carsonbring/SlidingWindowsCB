import numpy as np
from SlidingWindow import SlidingWindow
import rasterio
import matplotlib.pyplot as plt
import math

slide_window = SlidingWindow('test.tif')
slide_window_2 = SlidingWindow('gunsite_dem-2-1_export_w64.tif')

#img = rasterio.open('gunsite_dem-2-1.tif').read(1)
#plt.imshow(img)
#plt.show()
#img = rasterio.open('gunsite_dem-2-1_export_w64_z_mean_w64.tif').read(1)
#plt.imshow(img)
#plt.show()
#img = rasterio.open('gunsite_dem-2-1_export_w64_standard_w64.tif').read(1)
#plt.imshow(img)
#plt.show()
#img = rasterio.open('gunsite_dem-2-1_export_w64_slope_w64.tif').read(1)
#plt.imshow(img)
#plt.show()
#img = rasterio.open('gunsite_dem-2-1_export_w64_profile_w64.tif').read(1)
#plt.imshow(img)
#plt.show()
#img = rasterio.open('gunsite_dem-2-1_export_w64_planform_w64.tif').read(1)
#plt.imshow(img)
#plt.show()
#img = rasterio.open('gunsite_dem-2-1_export_w64_aspect_w64.tif').read(1)
#plt.imshow(img)
#plt.show()

#slide_window_2.dem_import_arrays()
#slide_window_2.dem_initialize_arrays()
#for _ in range(6):
#    slide_window_2.dem_aggregation_step(1)
#    slide_window_2.dem_export_arrays()
#slide_window_2.dem_mean()
#slide_window_2.dem_slope()
#slide_window_2.dem_aspect()
#slide_window_2.dem_profile()
#slide_window_2.dem_planform()
#slide_window_2.dem_standard()

# slide_window.fractal_3d(1, 6)
# slide_window.fractal(1, .5, 0, 6)
# slide_window.binary(1, .5)
# slide_window.regression(1, 2, 6)
# slide_window.pearson(1, 2, 6)
# slide_window.aggregation('++++', 6)
# slide_window.ndvi(1, 4)