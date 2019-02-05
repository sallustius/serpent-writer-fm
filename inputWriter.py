""" Collection of writers to create the Serpent input file"""
import numpy as np


class SerpentWriter:
    """
    SerpentWriter creates the input file

    Parameters
    ----------
    file_path: str
        filePath
    geometry: object
        geometry object
    materials: object

    Attributes
    ----------

    """
    def __init__(self, file_path, geometry, materials, settings,
                 fission_matrix, title='input'):
        self.fp = file_path
        self.geo = geometry
        self.mat = materials
        self.set = settings
        self.fm = fission_matrix
        self.title = title

    def write(self):
        file = open(self.fp, 'w')
        file.write('set title "%s"\n\n' % self.title)
        # Create object instances
        m = _MaterialsWriter(file, self.mat)
        g = _GeometryWriter(file, self.geo)
        s = _SettingsWriter(file, self.set)
        d = _DetectorWriter(file, self.fm)
        # Write on input file
        g.geo_write()
        m.mat_write()
        s.set_write()
        d.fm_write()
        # Close file
        file.close()

class _GeometryWriter:

    def __init__(self, file_path, geometry):
        self.fp = file_path
        self.g = geometry

    def geo_write(self):
        self.fp.write('% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')
        self.fp.write('%\t\t\t GEOMETRY\n')
        self.fp.write('% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n')
        self._write_pins(self.fp)
        self._write_assms(self.fp)
        self._write_cell(self.fp)
        self._write_box(self.fp)

    def _write_pins(self, fp):
        fp.write('%--- Pins\n')
        for jj in range(0, len(self.g.pins)):
            fp.write('pin %s \n' % self.g.pins[jj].name)
            for ii in range(0, np.size(self.g.pins[jj].radii) - 1):
                fp.write('%s   %.4f \n' % (self.g.pins[jj].materials[ii],
                                           self.g.pins[jj].radii[ii]))
            fp.write('%s  \n\n' % (self.g.pins[jj].materials[-1]))

    def _write_assms(self, fp):
        fp.write('%--- Assemblies\n')
        for ii in range(0, len(self.g.assm)):
            fp.write('lat %s 1 0.0 0.0 %d %d %.2f\n'
                     % (self.g.assm[ii].name, len(self.g.assm[ii].map),
                        len(self.g.assm[ii].map), self.g.assm[ii].pitch))
            for jj in range(0, np.size(self.g.assm[ii].map, 0)):
                for kk in range(0, np.size(self.g.assm[ii].map, 1)):
                    fp.write('%s ' % self.g.assm[ii].map[jj][kk])
                fp.write('\n')
            fp.write('\n')

    def _write_cell(self, fp):
        fp.write('%--- Super-Cell\n')
        fp.write('lat %s 1 0.0 0.0 %d %d %.2f\n'
                 % (self.g.cell.name, 2,
                    2, self.g.cell.pitch))
        for jj in range(0, np.size(self.g.cell.map[0])):
            for kk in range(0, np.size(self.g.cell.map[1])):
                fp.write('%s ' % self.g.cell.map[jj][kk])
            fp.write('\n')
        fp.write('\n')

    def _write_box(self, fp):
        lung1 = self.g.cell.pitch*np.size(self.g.cell.map[0])/2
        fp.write('surf 5 cuboid %.2f %.2f %.2f %.2f %.2f %.2f \n'
                 % (-lung1, lung1, -lung1, lung1, -10.71, 10.71))
        fp.write('cell 98  0 fill %s   -5\n' % self.g.cell.name)
        fp.write('cell 99  0 outside   5\n')
        fp.write('set bc 1 1 2\n')


class _MaterialsWriter:
    """

    """
    def __init__(self, file_path, materials):
        self.lista = materials
        self.fp = file_path

    def mat_write(self):
        """ Iterates over materials in the dictionary"""
        self.fp.write('% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')
        self.fp.write('%\t\t\t MATERIALS\n')
        self.fp.write('% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n')
        for ii in range(0, len(self.lista)):
            if self.lista[ii].moder == 0:
                self.fp.write('mat %s %s\n' % (
                    self.lista[ii].name, self.lista[ii].density))
            else:
                self.fp.write('mat %s %s moder lwtr 1001\n' % (
                    self.lista[ii].name, self.lista[ii].density))
            lunghezza = np.size(self.lista[ii].composition, 0)
            for jj in range(0, lunghezza):
                self.fp.write('%s %s\n' % (self.lista[ii].composition[jj][0],
                                           self.lista[ii].composition[jj][1]))
            self.fp.write('\n')


class _SettingsWriter:
    def __init__(self, file_path, settings):
        self.set = settings
        self.fp = file_path

    def set_write(self):
        self.fp.write('% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')
        self.fp.write('%\t\t\t SETTINGS\n')
        self.fp.write('% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n')
        self.fp.write('set pop %s %s %s %s \n' %
                      (self.set['pop'], self.set['active cycles'],
                       self.set['inactive cycles'], self.set['k guess']))
        self.fp.write('% -- Cross-sections\n')
        self.fp.write('set acelib "%s"\n' % self.set['lib'])
        if self.set['ures'] != 0:
            self.fp.write('set ures 1 3 %s \n' % self.set['ures'])
        self.fp.write('set nfg 1\n')
        self.fp.write('ene ciao 1 0 20\n\n')


class _DetectorWriter:
    """

    """
    def __init__(self, file_path, fission_matrix):
        self.fp = file_path
        self.fm = fission_matrix

    def _pre_check(self):
        if self.fm.typeFM == 'cartesian':
            flag = 4
        else:
            flag = 0
        return flag

    def _fission_matrix_cart(self, flag):
        string = 'set fmtx %d %.2f %.2f %d ' \
                 '%.2f %.2f %d %.2e %.2e %d\n' \
                 % (flag,
                    self.fm.Limits[0], self.fm.Limits[1], self.fm.Limits[2],
                    self.fm.Limits[3], self.fm.Limits[4], self.fm.Limits[5],
                    self.fm.Limits[6], self.fm.Limits[7], self.fm.Limits[8],)
        return string

    def fm_write(self):
        flag = self._pre_check()
        if flag == 0:
            raise ValueError('Only supported FM-type is "cartesian"')
        print('Appending detectors')
        self.fp.write('% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')
        self.fp.write('%\t\t\t FISSION MATRIX\n')
        self.fp.write('% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n')
        self.fp.write(self._fission_matrix_cart(flag))
        print('Completed')
