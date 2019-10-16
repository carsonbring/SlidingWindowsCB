import numpy as np
from numpy.polynomial import polynomial as poly
import rasterio
import inspect
import os
import math
import affine

class SlidingWindow:

    # TODO create more tests
    # test geoTransform update in __create_tif()
    # test averages (e.g. xz, yz) in DEM_UTILS   TODO also figure out how to initialize arrays

    # TODO do I have all required functionality?
    # image creation with geoTransform update
    # array conversion TODO needs updating
    # ndvi
    # binary
    # aggregation
    # regression
    # Pearson
    # fractal
    # fractal 3D TODO ensure this method is written properly (check __boxed_array() for sure)
    # DEM window mean
    # DEM array intialization
    # DEM double_w TODO this has 3 methods, do we need all 3?
    # DEM slope
    # DEM aspect
    # DEM standard curve
    # DEM profile curve
    # DEM planform curve

    # TODO what is the best way to handles aggregations?
    # 1. generate all images at each step
    # 2. specify what images to generate at each step
    # 3. store the results of all aggregations and let user choose images to generate at which step

    # TODO how should RBG and DEM be differentiated?

    # TODO Is the current model for the application desirable?
    # currently: intit with image -> execute operation -> image automatically created
    # cannot currently stack bands, TODO do we want to?

    # TODO research how to create python package
    # TODO add more documentation
    # TODO should all these methods use floating point?

    def __init__(self, file_path):
        self.file_name = os.path.split(file_path)[-1]
        self.img = rasterio.open(file_path)

    # operations for image aggregation
    __valid_ops = {'++++', '++--', '-+-+', '-++-', 'MAX', 'MIN'}
    @property
    def valid_ops(self):
        return self.__valid_ops

    # dictionary of all arrays required for DEM utils
    z, xz, yz, xxz, yyz, xyz = (np.zeros(0) for _ in range(6))
    __dem_arr_dic = {'z':z, 'xz':xz, 'yz':yz, 'xxz':xxz, 'yyz':yyz, 'xyz':xyz}
    @property
    def dem_arr_dic(self):
        return self.__dem_arr_dic

    # number of dem pixels aggregated
    __dem_pixels_aggre = 1
    @property
    def dem_pixels_aggre(self):
        return self.__dem_pixels_aggre

    # create NDVI image
    def ndvi(self, red_band, ir_band):
        bands = np.array(range(self.img.count))+1
        if (red_band not in bands or ir_band not in bands):
            raise ValueError('bands must be in range of %r.' % bands)
        
        red = self.img.read(red_band)
        ir = self.img.read(ir_band)
        ndvi = self.__ndvi(red, ir)
        # TODO change later
        ndvi = self.__arr_dtype_conversion(ndvi, np.uint8)
        self.__create_tif(ndvi)

    # i.e. Normalized Difference Vegetation Index
    # for viewing live green vegetation
    # requires red and infrared bands
    # returns floating point array
    def __ndvi(self, red_arr, ir_arr):
        red_arr = red_arr.astype(float)
        ir_arr = ir_arr.astype(float)
        return ( (ir_arr - red_arr) / (ir_arr + red_arr) )

    # create binary image
    def binary(self, band, threshold):
        bands = np.array(range(self.img.count))+1
        if (band not in bands):
            raise ValueError('band must be in range of %r.' % bands)

        arr = self.img.read(band)
        arr = self.__binary(arr, threshold)
        self.__create_tif(arr)

    # create black and white image
    # values greater than or equal to threshold percentage will be white
    # threshold: percent in decimal of maximum
    # returns array of same data type
    # TODO can I assume minimum is always 0, how would I handle it otherwise?
    def __binary(self, arr, threshold):
        if (threshold < 0 or threshold > 1):
            raise ValueError('threshold must be between 0 and 1')
        dtype = arr.dtype
        maximum = self.__get_max_min(arr.dtype)[0]
        return np.where(arr < (threshold*maximum), 0, maximum).astype(dtype)

    # check if an image is black and white or not
    # i.e. only contains values of dtype.min and dtype.max
    # TODO should min value be arr_in.dtype.min or 0?
    def __is_binary(self, arr_in):
        max_val = np.amax(arr_in)
        return ((arr_in==0) | (arr_in==max_val)).all()

    # get max and min of numpy data type
    # returns tuple (max, min)
    def __get_max_min(self, dtype):
        max_val = 0
        min_val = 0
        if (np.issubdtype(dtype, np.floating)):
            max_val = np.finfo(dtype).max
            min_val = np.finfo(dtype).min
        else:
            max_val = np.iinfo(dtype).max
            min_val = np.iinfo(dtype).min

        return (max_val, min_val)

    # create tif with array of numpy arrays representing image bands
    # adjust geoTransform according to how many pixels were aggregated
    def __create_tif(self, arr_in, pixels_aggre=1, fn=None):
        if (type(arr_in) == np.ndarray):
            arr_in = [arr_in]
        dtype = arr_in[0].dtype
        for x in range(1, len(arr_in)):
            if (arr_in[x].dtype is not dtype):
                raise TypeError('arrays must have the same dtype')


        profile = self.img.profile

        # update geo transform with aggregated pixels
        transform = profile['transform']
        temp = np.empty(6)
        # TODO test this stuff, ok?
        pixel_width = math.sqrt(transform[0]**2 + transform[3]**2)
        pixel_height = math.sqrt(transform[1]**2 + transform[4]**2)
        temp[2] = transform[2] + (pixels_aggre-1) * pixel_width / 2
        temp[5] = transform[5] - (pixels_aggre-1) * pixel_height / 2
        temp[0] = transform[0] * pixels_aggre
        temp[1] = transform[1] * pixels_aggre
        temp[3] = transform[3] * pixels_aggre
        temp[4] = transform[4] * pixels_aggre
        new_transform = affine.Affine(temp[0], temp[1], temp[2], temp[3] , temp[4], temp[5])

        profile.update(
            nodata=0,
            transform=new_transform,
            dtype=dtype,
            count=len(arr_in),
            height=len(arr_in[0]),
            width=len(arr_in[0][0])
            )

        if (fn == None):
            caller_name = inspect.stack()[1].function
            fn = os.path.splitext(self.file_name)[0] + '_' + caller_name + '.tif'
            
        with rasterio.open(fn, 'w', **profile) as dst:
            for x in range(len(arr_in)): 
                dst.write(arr_in[x], x+1)

    # TODO fix later, not the best way to do this
    # arr_in: array to be converted
    # dtype: numpy type to convert to
    def __arr_dtype_conversion(self, arr_in, dtype):
        arr_max = np.amax(arr_in)
        arr_min = np.amin(arr_in)
        dtype_max = self.__get_max_min(dtype)[0]
        arr_out = ((arr_in - arr_min)/(arr_max - arr_min)*dtype_max).astype(dtype) 
        return arr_out

    # non-vectorized aggregation method
    # very slow
    # returns floating point array
    def _aggregation_brute(self, arr_in, operation, num_aggre):
        if (operation.upper() not in self.__valid_ops):
            raise ValueError('operation must be one of %r.' % self.__valid_ops)

        arr_in = arr_in.astype(float)
        x_max = arr_in.shape[1]
        y_max = arr_in.shape[0]
        arr_out = np.array(arr_in)

        # iterate through window sizes
        for i in range(num_aggre):
            delta = 2**i
            y_max -= delta
            x_max -= delta
            arr = np.empty([y_max, x_max])

            # iterate through pixels
            for j in range (y_max):
                for i in range (x_max):
                    if (operation == '++++'):
                        arr[j, i] = arr_out[j, i] + arr_out[j, i+delta] + arr_out[j+delta, i] + arr_out[j+delta, i+delta]
                    if (operation == '++--'):
                        arr[j, i] = arr_out[j, i] + arr_out[j, i+delta] - arr_out[j+delta, i] - arr_out[j+delta, i+delta]
                    if (operation == '-+-+'):
                        arr[j, i] = -arr_out[j, i] + arr_out[j, i+delta] - arr_out[j+delta, i] + arr_out[j+delta, i+delta]
                    if (operation == '-++-'):
                        arr[j, i] = -arr_out[j, i] + arr_out[j, i+delta] + arr_out[j+delta, i] - arr_out[j+delta, i+delta]
                    elif (operation.upper() == 'MAX'):
                        arr[j, i] = max(max(max(arr_out[j, i], arr_out[j, i+delta]), arr_out[j+delta, i]), arr_out[j+delta, i+delta])
                    elif (operation.upper() == 'MIN'):
                        arr[j, i] = min(min(min(arr_out[j, i], arr_out[j, i+delta]), arr_out[j+delta, i]), arr_out[j+delta, i+delta])
            arr_out = arr
        return arr_out

    # create image with each band aggregated num_aggre times
    def aggregation(self, operation, num_aggre):        
        arr = []
        for x in range(self.img.count):
            arr.append(self.img.read(x+1))
            arr[x] = self._partial_aggregation(arr[x], 0, num_aggre, operation)

            # TODO remove later
            arr[x] = self.__arr_dtype_conversion(arr[x], np.uint8)
        
        self.__create_tif(arr, pixels_aggre=2**num_aggre)

    # do power_target-power_start aggregations on window
    # starting with delta=2**power_start aggregation offset
    # returns floating point array
    def _partial_aggregation(self, arr_in, power_start, power_target, operation):
        if (operation.upper() not in self.__valid_ops):
            raise ValueError('operation must be one of %r.' % self.__valid_ops)
        if (power_start < 0 or power_start >= power_target):
            raise ValueError('power_start must be nonzero and less than power_target')

        arr_in = arr_in.astype(float)
        y_max = arr_in.shape[0]
        x_max = arr_in.shape[1]
        arr_out = arr_in.flatten()
        
        # iterate through sliding window sizes
        for i in range(power_start, power_target):
            delta = 2**i
            size = arr_out.size
            # create offset slices of the array to aggregate elements
            # aggregates the corners of squares of length delta+1
            top_left = arr_out[0: size - (delta*x_max + delta)]
            top_right = arr_out[delta: size - (x_max*delta)]
            bottom_left = arr_out[delta*x_max: size - (delta)]
            bottom_right = arr_out[delta*x_max + delta: size]

            if operation.upper() == '++++':
                arr_out = top_left + top_right + bottom_left + bottom_right
            if operation.upper() == '++--':
                arr_out = top_left + top_right - bottom_left - bottom_right
            if operation.upper() == '-+-+':
                arr_out = -top_left + top_right - bottom_left + bottom_right
            if operation.upper() == '-++-':
                arr_out = -top_left + top_right + bottom_left - bottom_right
            elif operation.upper() == 'MAX':
                arr_out = np.maximum(np.maximum(np.maximum(top_left, top_right), bottom_left), bottom_right)
            elif operation.upper() == 'MIN':
                arr_out = np.minimum(np.minimum(np.minimum(top_left, top_right), bottom_left), bottom_right)

        # remove last removal_num rows and columns, they are not aggregate pixels
        removal_num = (2**power_target) - (2**power_start)
        y_max -= removal_num
        # pad to make array square
        arr_out = np.pad(arr_out, (0, removal_num), 'constant')
        arr_out = np.reshape(arr_out, (y_max, x_max))
        arr_out = np.delete(arr_out, np.s_[-removal_num:], 1)
        
        return arr_out

    # create image with pixel values cooresponding to their aggregated regression slope
    def regression(self, band1, band2, num_aggre):
        bands = np.array(range(self.img.count))+1
        if (band1 not in bands or band2 not in bands):
            raise ValueError('bands must be in range of %r.' % bands)

        arr_a = self.img.read(band1)
        arr_b = self.img.read(band2)
        arr_m = self._regression(arr_a, arr_b, num_aggre)

        # TODO remove later
        arr_m = self.__arr_dtype_conversion(arr_m, np.uint8)

        self.__create_tif(arr_m, pixels_aggre=2**num_aggre)

    # Do num_aggre aggregations and return the regression slope between two bands
    # returns floating point array
    def _regression(self, arr_a, arr_b, num_aggre):
        arr_a = arr_a.astype(float)
        arr_b = arr_b.astype(float)
        arr_aa = arr_a**2
        arr_ab = arr_a*arr_b

        arr_a = self._partial_aggregation(arr_a, 0, num_aggre, '++++')
        arr_b = self._partial_aggregation(arr_b, 0, num_aggre, '++++')
        arr_aa = self._partial_aggregation(arr_aa, 0, num_aggre, '++++')
        arr_ab = self._partial_aggregation(arr_ab, 0, num_aggre, '++++')

        # total input pixels aggregated per output pixel
        count = (2**num_aggre)**2

        # regression coefficient, i.e. slope of best fit line
        numerator = count * arr_ab - arr_a * arr_b
        denominator = count * arr_aa - arr_a**2
        # avoid division by zero
        # TODO is this required? Zero only occurs when there is no variance in the a band
        denominator = np.maximum(denominator, 1)
        arr_m = numerator/denominator

        return arr_m

    # TODO potentially add R squared method?

    # create image with pixel values cooresponding to their aggregated pearson correlation
    def pearson(self, band1, band2, num_aggre):
        bands = np.array(range(self.img.count))+1
        if (band1 not in bands or band2 not in bands):
            raise ValueError('bands must be in range of %r.' % bands)

        arr_a = self.img.read(band1)
        arr_b = self.img.read(band2)
        arr_r = self._pearson(arr_a, arr_b, num_aggre)

        # TODO remove later
        arr_r = self.__arr_dtype_conversion(arr_r, np.uint8)

        self.__create_tif(arr_r, pixels_aggre=2**num_aggre)

    # Do num_aggre aggregations and return the regression slope between two bands
    # returns floating point array
    def _pearson(self, arr_a, arr_b, num_aggre):
        arr_a = arr_a.astype(float)
        arr_b = arr_b.astype(float)
        arr_aa = arr_a**2
        arr_bb = arr_b**2
        arr_ab = arr_a*arr_b

        arr_a = self._partial_aggregation(arr_a, 0, num_aggre, '++++')
        arr_b = self._partial_aggregation(arr_b, 0, num_aggre, '++++')
        arr_aa = self._partial_aggregation(arr_aa, 0, num_aggre, '++++')
        arr_bb = self._partial_aggregation(arr_bb, 0, num_aggre, '++++')
        arr_ab = self._partial_aggregation(arr_ab, 0, num_aggre, '++++')

        # total input pixels aggregated per output pixel
        count = (2**num_aggre)**2

        # pearson correlation
        numerator = count*arr_ab - arr_a*arr_b
        denominator = np.sqrt(count * arr_aa - arr_a**2) * np.sqrt(count * arr_bb - arr_b**2)
        # avoid division by zero
        # TODO is this required? Zero only occurs when there is no variance in the a or b bands
        denominator = np.maximum(denominator, 1)
        arr_r = numerator / denominator
        
        return arr_r

    # Do num_aggre aggregations and return the regression slope between two bands
    # non-vectorized using numpy's polyfit method
    # returns floating point array
    def _regression_brute(self, arr_a, arr_b, num_aggre):
        arr_a = arr_a.astype(float)
        arr_b = arr_b.astype(float)
        w_out = 2**num_aggre
        y_max =  arr_a.shape[0] - (w_out-1)
        x_max = arr_a.shape[1] - (w_out-1)
        arr_m = np.empty([x_max, y_max])
        
        for j in range (y_max):
            for i in range (x_max):
                arr_1 = arr_a[j:j+w_out, i:i+w_out].flatten()
                arr_2 = arr_b[j:j+w_out, i:i+w_out].flatten()
                arr_coef = poly.polyfit(arr_1, arr_2, 1)
                arr_m[j][i] = arr_coef[1]

        return arr_m

    # create image with pixel values cooresponding to their aggregated fractal dimension
    def fractal(self, band, threshold, power_start, power_target):
        bands = np.array(range(self.img.count))+1
        if (band not in bands):
            raise ValueError('band must be in range of %r.' % bands)

        arr = self.img.read(band)
        arr = self._fractal(self.__binary(arr, threshold), power_start, power_target)

        # TODO remove later
        arr = self.__arr_dtype_conversion(arr, np.uint16)

        self.__create_tif(arr, pixels_aggre=2**power_target)

    # Compute fractal dimension on 2**power_target wide pixel areas
    def _fractal(self, arr_in, power_start, power_target):
        if (not self.__is_binary(arr_in)):
            raise ValueError('array must be binary')
        if (power_start < 0 or power_start >= power_target):
            raise ValueError('power_start must be nonzero and less than power_target')

        arr = arr_in.astype(float)
        x_max = arr.shape[1]-(2**power_target-1)
        y_max = arr.shape[0]-(2**power_target-1)
        denom_regress = np.empty(power_target-power_start)
        num_regress = np.empty([power_target-power_start, x_max*y_max])
        
        if power_start > 0:
            arr = self._partial_aggregation(arr, 0, power_start, 'max')

        for i in range(power_start, power_target):
            arr_sum = self._partial_aggregation(arr, i, power_target, '++++')
            arr_sum = np.maximum(arr_sum, 1)

            arr_sum = np.log2(arr_sum)
            denom_regress[i-power_start] = power_target-i
            num_regress[i-power_start,] = arr_sum.flatten()
            if i < power_target-1:
                arr = self._partial_aggregation(arr, i, i+1, 'max')

        arr_slope = poly.polyfit(denom_regress, num_regress, 1)[1]
        arr_out = np.reshape(arr_slope, (y_max, x_max))
        return arr_out

    # This is for the 3D fractal dimension that is between 2 and 3, but it isn't tested yet
    def __boxed_array(self, arr_in, power_target):
        arr_min = np.amin(arr_in)
        arr_max = np.amax(arr_in)
        arr_out = np.zeros(arr_in.size)
        if (arr_max > arr_min):
            n_boxes = 2**power_target-1
            buffer = (arr_in-arr_min)/(arr_max-arr_min)
            arr_out = np.floor(n_boxes * buffer)
        return arr_out

    def fractal_3d(self, band, num_aggre):
        bands = np.array(range(self.img.count))+1
        if (band not in bands):
            raise ValueError('band must be in range of %r.' % bands)

        arr = self.img.read(band)
        arr = self._fractal_3d(arr, num_aggre)

        # TODO remove later
        arr = self.__arr_dtype_conversion(arr, np.uint8)

        self.__create_tif(arr, pixels_aggre=2**num_aggre)

    # TODO does this need to be binary too? probably not?
    # TODO should this have a power_start?
    def _fractal_3d(self, arr_in, num_aggre):
        if (num_aggre <= 1):
            raise ValueError('number of aggregations must be greater than one')
        y_max = arr_in.shape[0] - (2**num_aggre-1)
        x_max = arr_in.shape[1] - (2**num_aggre-1)
        arr_box = self.__boxed_array(arr_in, num_aggre).astype(float)
        arr_min = np.array(arr_box)
        arr_max = np.array(arr_box)
        denom_regress = np.empty(num_aggre-1)
        num_regress = np.empty([num_aggre-1, x_max*y_max])
        
        # TODO is this supposed to start at 1?
        for i in range(1, num_aggre):
            arr_min = self._partial_aggregation(arr_min, i-1, i, 'min')
            arr_max = self._partial_aggregation(arr_max, i-1, i, 'max')
            arr_sum = self._partial_aggregation(arr_max-arr_min+1, i, num_aggre, '++++')
            arr_num = np.log2(arr_sum)
            denom_regress[i-1] = num_aggre - i
            num_regress[i-1,] = arr_num.flatten()

            # TODO why do we divide by two?
            arr_min /= 2
            arr_max /= 2

        arr_slope = poly.polyfit(denom_regress, num_regress, 1)[1]
        arr_out = np.reshape(arr_slope, (y_max, x_max))
        return arr_out

    # TODO should I assume dem band is the only band?
    def dem_initialize_arrays(self, z):
        z = self.img.read(1)
        xz, yz, xxz, yyz, xyz = (np.zeros(z.shape) for _ in range(5))
        self.__dem_arr_dic.update({'z':z, 'xz':xz, 'yz':yz, 'xxz':xxz, 'yyz':yyz, 'xyz':xyz})

    def dem_aggregation_step(self, num_steps):
        z, xz, yz, xxz, yyz, xyz, delta = (self.__dem_arr_dic[x] for x in ('z', 'xz', 'yz', 'xxz', 'yyz', 'xyz'))
        delta_power = math.log2(self.__dem_pixels_aggre)

        for _ in range(num_steps):
            z_sum_all = self._partial_aggregation(z, delta_power, delta_power+1, '++++')
            z_sum_top = self._partial_aggregation(z, delta_power, delta_power+1, '++--')
            z_sum_right = self._partial_aggregation(z, delta_power, delta_power+1, '-+-+')
            z_sum_anti_diag = self._partial_aggregation(z, delta_power, delta_power+1, '-++-')

            xz_sum_all = self._partial_aggregation(xz, delta_power, delta_power+1, '++++')
            xz_sum_top = self._partial_aggregation(xz, delta_power, delta_power+1, '++--')
            xz_sum_right = self._partial_aggregation(xz, delta_power, delta_power+1, '-+-+')

            yz_sum_all = self._partial_aggregation(yz, delta_power, delta_power+1, '++++')
            yz_sum_top = self._partial_aggregation(yz, delta_power, delta_power+1, '++--')
            yz_sum_right = self._partial_aggregation(yz, delta_power, delta_power+1, '-+-+')

            xxz_sum_all = self._partial_aggregation(xxz, delta_power, delta_power+1, '++++')

            yyz_sum_all = self._partial_aggregation(yyz, delta_power, delta_power+1, '++++')

            xyz_sum_all = self._partial_aggregation(xyz, delta_power, delta_power+1, '++++')

            xxz = 0.25*(xxz_sum_all + delta*xz_sum_right + 0.25*(delta**2)*z_sum_all)
            yyz = 0.25*(yyz_sum_all + yz_sum_top*delta + 0.25*(delta**2)*z_sum_all)
            xyz = 0.25*(xyz_sum_all + 0.5*delta*(xz_sum_top + yz_sum_right) + 0.25*(delta**2)*z_sum_anti_diag)
            xz = 0.25*(xz_sum_all + 0.5*delta*z_sum_right)
            yz = 0.25*(yz_sum_all + 0.5*delta*z_sum_top)
            z = 0.25*z_sum_all

            delta_power += 1
        
        self.__dem_arr_dic.update({'z': z, 'xz': xz, 'yz': yz, 'xxz': xxz, 'yyz': yyz, 'xyz': xyz})
        self.__dem_pixels_aggre = 2**delta_power

    def _dem_aggregation_step_brute(self, num_steps):
        z, xz, yz, xxz, yyz, xyz = (self.__dem_arr_dic[x] for x in ('z', 'xz', 'yz', 'xxz', 'yyz', 'xyz'))
        
        for _ in range(num_steps):
            x_max = z.shape[1] - delta
            y_max = z.shape[0] - delta
            for y in range (y_max):
                for x in range (x_max):
                    z_sum_all = z[y, x] + z[y, x+delta] + z[y+delta, x] + z[y+delta, x+delta]
                    z_sum_top = z[y, x] + z[y, x+delta] - z[y+delta, x] - z[y+delta, x+delta]
                    z_sum_right = -z[y, x] + z[y, x+delta] - z[y+delta, x] + z[y+delta, x+delta]
                    z_sum_anti_diag = -z[y,x] + z[y, x+delta] + z[y+delta, x] - z[y+delta, x+delta]

                    xz_sum_all = xz[y, x] + xz[y, x+delta] + xz[y+delta, x] + xz[y+delta, x+delta]
                    xz_sum_top = xz[y, x] + xz[y, x+delta] - xz[y+delta, x] - xz[y+delta, x+delta]
                    xz_sum_right = -xz[y, x] + xz[y, x+delta] - xz[y+delta, x] + xz[y+delta, x+delta]

                    yz_sum_all = yz[y, x] + yz[y, x+delta] + yz[y+delta, x] + yz[y+delta, x+delta]
                    yz_sum_top = yz[y, x] + yz[y, x+delta] - yz[y+delta, x] - yz[y+delta, x+delta]
                    yz_sum_right = -yz[y, x] + yz[y, x+delta] - yz[y+delta, x] + yz[y+delta, x+delta]

                    xxz_sum_all = xxz[y, x] + xxz[y, x+delta] + xxz[y+delta, x] + xxz[y+delta, x+delta]

                    yyz_sum_all = yyz[y, x] + yyz[y, x+delta] + yyz[y+delta, x] + yyz[y+delta, x+delta]

                    xyz_sum_all = xyz[y, x] + xyz[y, x+delta] + xyz[y+delta, x] + xyz[y+delta, x+delta]

                    xz[y, x] = 0.25*(xz_sum_all + 0.5*delta*z_sum_right)
                    yz[y, x] = 0.25*(yz_sum_all + 0.5*delta*z_sum_top)
                    xxz[y, x] = 0.25*(xxz_sum_all + delta*xz_sum_right + 0.25*(delta**2)*z_sum_all)
                    yyz[y, x] = 0.25*(yyz_sum_all + delta*yz_sum_top + 0.25*(delta**2)*z_sum_all)
                    xyz[y, x] = 0.25*(xyz_sum_all + 0.5*delta*(xz_sum_top + yz_sum_right) + 0.25*(delta**2)*z_sum_anti_diag)
                    z[y, x] = 0.25*z_sum_all
            delta *= 2
        
        self.__dem_arr_dic.update({'z': z, 'xz': xz, 'yz': yz, 'xxz': xxz, 'yyz': yyz, 'xyz': xyz})
        self.__dem_pixels_aggre = delta

    def dem_mean(self, arr_name='z'):
        if (arr_name not in self.__dem_arr_dic):
            raise ValueError('%s must be a member of %r' % (arr_name, self.__dem_arr_dic))
        
        arr = self.__dem_arr_dic[arr_name]
        arr = self.__arr_dtype_conversion(arr, np.uint16)
        pixels_aggre = self.__dem_pixels_aggre
        fn = os.path.splitext(self.file_name)[0] + '_' + arr_name + '_mean_w' + str(pixels_aggre) + '.tif'
        self.__create_tif(arr, pixels_aggre=pixels_aggre, fn=fn)

    def dem_slope(self, delta_power):
        slope = self.__slope(delta_power)

        slope = self.__arr_dtype_conversion(slope, np.uint16)
        pixels_aggre = self.__dem_pixels_aggre
        fn = os.path.splitext(self.file_name)[0] + '_slope_w' + str(pixels_aggre) +'.tif'
        self.__create_tif(slope, pixels_aggre=pixels_aggre, fn=fn)

    def __slope(self, delta_power):
        pixels_aggre = self.__dem_pixels_aggre
        transform = self.img.profile['transform']
        pixel_width = math.sqrt(transform[0]**2 + transform[3]**2)
        pixel_height = math.sqrt(transform[1]**2 + transform[4]**2)
        xz = self.__dem_arr_dic['xz']
        yz = self.__dem_arr_dic['yz']

        slope_x = xz*(12/(pixels_aggre**2 - 1))
        slope_y = yz*(12/(pixels_aggre**2 - 1))
        len_opp = abs(slope_x)*xz + abs(slope_y)*yz
        len_adj = math.sqrt( ((pixel_width*xz)**2) + ((pixel_height*yz)**2) )
        slope = np.arctan(len_opp/len_adj)

        return slope

    # angle clockwise from north of the downward slope
    def aspect(self, arr_dic, delta_power):
        delta = 2**delta_power
        xz = arr_dic['xz']
        yz = arr_dic['yz']

        aspect = (-np.arctan(xz/np.maximum(yz,1)) - np.sign(yz)*math.pi/2 + math.pi/2) % (2*math.pi)
        fn = os.path.splitext(self.file_name)[0] + '_aspect_w' + str(delta*2) +'.tif'
        aspect = self.__arr_dtype_conversion(aspect, np.uint16)
        self.__create_tif(aspect, pixels_aggre=delta*2, fn=fn)

    def profile(self, delta_power, arr_dic):
        delta = 2**delta_power
        z, xz, yz, yyz, xxz, xyz = tuple (arr_dic[i] for i in ('z', 'xz', 'yz', 'yyz', 'xxz', 'xyz'))

        a00 = (2160*xxz - 720*(delta**2)*z - 180*z) / (32*(delta**4) - 40*(delta**2) + 8)
        a10 = (288*xyz) / (32*(delta**4) - 16*(delta**2) + 2)
        a11 = (2160*yyz - 720*(delta**2)*z - 180*z) / (32*(delta**4) - 40*(delta**2) + 8)
        
        profile = (a00*(xz**2) + 2*a10*xz*yz + a11*(yz*2)) / ((xz**2) + (yz**2))

        fn = os.path.splitext(self.file_name)[0] + '_profile_w' + str(delta*2) +'.tif'
        profile = self.__arr_dtype_conversion(profile, np.uint16)
        self.__create_tif(profile, pixels_aggre=delta*2, fn=fn)

    def planform(self, delta_power, arr_dic):
        delta = 2**delta_power
        z, xz, yz, yyz, xxz, xyz = tuple (arr_dic[i] for i in ('z', 'xz', 'yz', 'yyz', 'xxz', 'xyz'))

        a00 = (2160*xxz - 720*(delta**2)*z - 180*z) / (32*(delta**4) - 40*(delta**2) + 8)
        a10 = (288*xyz) / (32*(delta**4) - 16*(delta**2) + 2)
        a11 = (2160*yyz - 720*(delta**2)*z - 180*z) / (32*(delta**4) - 40*(delta**2) + 8)
        
        planform = (a00*(yz**2) - 2*a10*xz*yz + a11*(xz*2)) / ((xz**2) + (yz**2))
        
        fn = os.path.splitext(self.file_name)[0] + '_planform_w' + str(delta*2) +'.tif'
        planform = self.__arr_dtype_conversion(planform, np.uint16)
        self.__create_tif(planform, pixels_aggre=delta*2, fn=fn)

    def standard(self, delta_power, arr_dic):
        delta = 2**delta_power
        z, yyz, xxz = tuple (arr_dic[i] for i in ('z', 'yyz', 'xxz'))

        a00 = (2160*xxz - 720*(delta**2)*z - 180*z) / (32*(delta**4) - 40*(delta**2) + 8)
        a11 = (2160*yyz - 720*(delta**2)*z - 180*z) / (32*(delta**4) - 40*(delta**2) + 8)
        standard = (a00 + a11) / 2

        fn = os.path.splitext(self.file_name)[0] + '_standard_w' + str(delta*2) +'.tif'
        standard = self.__arr_dtype_conversion(standard, np.uint16)
        self.__create_tif(standard, pixels_aggre=delta*2, fn=fn)
