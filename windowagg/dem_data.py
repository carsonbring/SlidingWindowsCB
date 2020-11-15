import numpy as np

class Dem_data:

    # TODO default arrays are float, is that good?
    def __init__(self, z, xz=None, yz=None, xxz=None, yyz=None, xyz=None, num_aggre=0):
        self.num_aggre = num_aggre
        arrays = {'z':z, 'xz':xz, 'yz':yz, 'xxz':xxz, 'yyz':yyz, 'xyz':xyz}
        
        for i in arrays:
            if (arrays[i] is None):
                arrays[i] = np.zeros(z.shape, z.dtype)
        
        self.set_arrays(**arrays)

    def arrays(self):
        return self._z, self._xz, self._yz, self._xxz, self._yyz, self._xyz

    def z(self):
        return self._z
    
    def xz(self):
        return self._xz
    
    def yz(self):
        return self._yz
                    
    def xxz(self):
        return self._xxz
    
    def yyz(self):
        return self._yyz

    def xyz(self):
        return self._xyz

    def set_arrays(self, z, xz, yz, xxz, yyz, xyz):
        shape = z.shape

        if (len(z.shape) != 2):
            raise ValueError('All arrays must be 2 dimensional')
        for array in [xz, yz, xxz, yyz, xyz]:
            if (array.shape != shape):
                raise ValueError('All arrays must have the same shape')

        self._z = z
        self._xz = xz
        self._yz = yz
        self._xxz = xxz
        self._yyz = yyz
        self._xyz = xyz

    @staticmethod
    def from_import(file_name):
        with np.load(file_name) as npz:
            z = npz['z']
            xz = npz['xz']
            yz = npz['yz']
            xxz = npz['xxz']
            yyz = npz['yyz']
            xyz = npz['xyz']
            num_aggre = npz['num_aggre']

        return Dem_data(z, xz, yz, xxz, yyz, xyz, num_aggre)
    
    def export(self, file_name):
        np.savez(
            file_name,
            z=self._z,
            xz=self._xz,
            yz=self._yz,
            xxz=self._xxz,
            yyz=self._yyz,
            xyz=self._xyz,
            num_aggre=self.num_aggre
        )
