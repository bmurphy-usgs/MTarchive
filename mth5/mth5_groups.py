# -*- coding: utf-8 -*-
"""

Containers to hold the various groups Station, channel, Channel

Created on Fri May 29 15:09:48 2020

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import inspect
import numpy as np
import weakref
import logging
import h5py

from mth5 import metadata
from mth5.standards import schema
from mth5.utils.helpers import to_numpy_type
from mth5.helpers import get_tree
from mth5.utils.exceptions import MTH5TableError, MTH5Error


meta_classes = dict(inspect.getmembers(metadata, inspect.isclass))
# =============================================================================
# 
# =============================================================================
class BaseGroup():
    """
    generic object that will have functionality for reading/writing groups, 
    including attributes and data.
    
    methods:
        * initialize_group
        * write_metadata
        * read_metadata
        * from_reference?
    """
    
    def __init__(self, group, group_metadata=None, **kwargs):
        
        if group is not None and isinstance(group, (h5py.Group, h5py.Dataset)):
            self.hdf5_group = weakref.ref(group)()
        
        self.logger = logging.getLogger('{0}.{1}'.format(__name__, 
                                                         self._class_name))
        
        # set metadata to the appropriate class.  Standards is not a 
        # metadata.Base object so should be skipped. If the class name is not
        # defined yet set to Base class.
        self.metadata = metadata.Base()
        if self._class_name not in ['Standards']:
            try:
                self.metadata = meta_classes[self._class_name]()
            except KeyError:
                self.metadata = metadata.Base()
            
        # add 2 attributes that will help with querying 
        # 1) the metadata class name
        self.metadata.add_base_attribute('mth5_type', 
                                         self._class_name.split('Group')[0],
                                         {'type':str, 
                                          'required':True,
                                          'style':'free form',
                                          'description': 'type of group', 
                                          'units':None,
                                          'options':[],
                                          'alias':[],
                                          'example':'group_name'})
        
        # 2) the HDF5 reference that can be used instead of paths
        self.metadata.add_base_attribute('hdf5_reference', 
                                         self.hdf5_group.ref,
                                         {'type': 'h5py_reference', 
                                          'required':True,
                                          'style':'free form',
                                          'description': 'hdf5 internal reference', 
                                          'units':None,
                                          'options':[],
                                          'alias':[],
                                          'example':'<HDF5 Group Reference>'})
        # set summary attributes    
        self.logger.debug("Metadata class for {0} is {1}".format(
                self._class_name, type(self.metadata)))
        
        # if metadata, make sure that its the same class type
        if group_metadata is not None:
            if not isinstance(group_metadata, (self.metadata, metadata.Base)):
                msg = "metadata must be type metadata.{0} not {1}".format(
                    self._class_name, type(metadata))
                self.logger.error(msg)
                raise MTH5Error(msg)
             
            # load from dict because of the extra attributes for MTH5
            self.metadata.from_dict(metadata.to_dict())
            self.write_metadata()

        # set default columns of summary table.
        self._defaults_summary_attrs = {'name': 'Summary',
                                  'max_shape': (10000, ),
                                  'dtype': np.dtype([('default', np.float)])}
        
        # if any other keywords 
        for key, value in kwargs.items():
            setattr(self, key, value)
        
    def __str__(self):
        try: 
            self.hdf5_group.ref
            
            return get_tree(self.hdf5_group)
        except ValueError:
            msg = 'MTH5 file is closed and cannot be accessed.'
            self.logger.warning(msg)
            return msg
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        raise MTH5Error('Cannot test equals yet')
    
    # Iterate over key, value pairs
    def __iter__(self):
        return self.hdf5_group.items().__iter__()
        
    @property
    def _class_name(self):
        return self.__class__.__name__.split('Group')[0]
    
    @property
    def summary_table(self):
        return MTH5Table(self.hdf5_group['Summary'])
    
    @property
    def groups_list(self):
        return list(self.hdf5_group.keys())
    
    def read_metadata(self):
        """
        read metadata
        
        :return: DESCRIPTION
        :rtype: TYPE

        """
        meta_dict = dict([(key, value) for key, value in 
                          self.hdf5_group.attrs.items()])
        
        self.metadata.from_dict({self._class_name: meta_dict})
               
    def write_metadata(self):
        """
        Write metadata from a dictionary

        :return: DESCRIPTION
        :rtype: TYPE

        """
        meta_dict = self.metadata.to_dict()[self.metadata._class_name.lower()]
        for key, value in meta_dict.items():
            value = to_numpy_type(value)
            self.logger.debug('wrote metadata {0} = {1}'.format(key, value))
            self.hdf5_group.attrs.create(key, value)

    def read_data(self):
        raise MTH5Error("read_data is not implemented yet")
    
    def write_data(self):
        raise MTH5Error("write_data is not implemented yet")
    
    def initialize_summary_table(self):
        """
        Initialize summary table based on default values
        :return: DESCRIPTION
        :rtype: TYPE

        """
        
        summary_table = self.hdf5_group.create_dataset(
            self._defaults_summary_attrs['name'], 
            (1, ),
            maxshape=self._defaults_summary_attrs['max_shape'],
            dtype=self._defaults_summary_attrs['dtype'])
        
        summary_table.attrs.update({'type': 'summary table',
                                    'last_updated': 'date_time',
                                    'reference': summary_table.ref})
        
        self.logger.debug(
            "Created {0} table with max_shape = {1}, dtype={2}".format(
                self._defaults_summary_attrs['name'],
                self._defaults_summary_attrs['max_shape'],
                self._defaults_summary_attrs['dtype']))
        
    def initialize_group(self):
        """
        Initialize group
        
        :return: DESCRIPTION
        :rtype: TYPE

        """
        self.initialize_summary_table()
        self.write_metadata()
        
   
class SurveyGroup(BaseGroup):
    """
    holds the survey group
    
    """
    
    def __init__(self, group, **kwargs):
        
        super().__init__(group, **kwargs)
    

class MasterStationGroup(BaseGroup):
    """
    holds the station group
    
    methods:
        * add_station
        * from_reference
        * 
    
    """
    
    def __init__(self, group, **kwargs):
        
        super().__init__(group, **kwargs)
        
        self._defaults_summary_attrs = {'name': 'Summary',
                                  'max_shape': (1000,),
                                  'dtype': np.dtype([('archive_id', 'S5'),
                                                     ('start', 'S32'),
                                                     ('end', 'S32'),
                                                     ('components', 'S100'),
                                                     ('measurement_type',
                                                      'S12'),
                                                     ('location.latitude',
                                                      np.float),
                                                     ('location.longitude',
                                                      np.float),
                                                     ('hdf5_reference', 
                                                      h5py.ref_dtype)])}
        
    
    def add_station(self, station_name, station_metadata=None):
        """
        Add a station with metadata if given.
        
        :param station_name: DESCRIPTION
        :type station_name: TYPE
        :param station_metadata: DESCRIPTION, defaults to None
        :type station_metadata: TYPE, optional
        :return: DESCRIPTION
        :rtype: TYPE

        """
        
        try:
            station_group = self.hdf5_group.create_group(station_name)
            self.logger.debug("Created group {0}".format(station_group.name))
            station_obj = StationGroup(station_group, 
                                       metadata=station_metadata)
            station_obj.write_metadata()
        except ValueError:
            msg = (f"Station {station_name} already exists, " +
                   "returning existing group.")
            self.logger.info(msg)
            station_obj = StationGroup(self.hdf5_group[station_name])
            station_obj.read_metadata()

        return station_obj
    
    def get_station(self, station_name):
        """
        
        :param station_name: DESCRIPTION
        :type station_name: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        
        try:
            return StationGroup(self.hdf5_group[station_name])
        except KeyError:
            msg = (f'{station_name} does not exist, ' +
                   'check station_list for existing names')
            self.logger.exception(msg)
            raise MTH5Error(msg)
        
class StationGroup(BaseGroup):
    """
    holds the station group

    
    """
    
    def __init__(self, group, station_metadata=None, **kwargs):
        
        super().__init__(group, group_metadata=station_metadata, **kwargs)
        
        self._defaults_summary_attrs = {'name': 'Summary',
                                        'max_shape': (1000,),
                                        'dtype': np.dtype([
                                            ('id', 'S5'),
                                            ('start', 'S32'),
                                            ('end', 'S32'),
                                            ('components', 'S100'),
                                            ('measurement_type', 'S12'),
                                            ('sample_rate', np.float)])}
        
        
    @property
    def name(self):
        return self.metadata.archive_id
    
    @name.setter
    def name(self, name):
        self.metadata.archive_id = name
        
    def add_run(self, run_name, run_metadata=None):
        """
        Add a run
        
        :param run_name: DESCRIPTION
        :type run_name: TYPE
        :param metadata: DESCRIPTION, defaults to None
        :type metadata: TYPE, optional
        :return: DESCRIPTION
        :rtype: TYPE
        
        need to be able to fill an entry in the summary table.

        """
        
        try:
            run_group = self.hdf5_group.create_group(run_name)
            self.logger.debug("Created group {0}".format(run_group.name))
            run_obj = RunGroup(run_group, run_metdata=run_metadata)
            run_obj.initialize_group()
        
        except ValueError:
            msg = (f"run {run_name} already exists, " +
                   "returning existing group.")
            self.logger.info(msg)
            run_obj = RunGroup(self.hdf5_group[run_name])
            run_obj.read_metadata()

        return run_obj
    
    def get_run(self, run_name):
        """
        get a run from run name
        
        :param run_name: DESCRIPTION
        :type run_name: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        try:
            return RunGroup(self.hdf5_group[run_name])
        except KeyError:
            msg = (f'{run_name} does not exist, ' +
                   'check groups_list for existing names')
            self.logger.exception(msg)
            raise MTH5Error(msg)
    

class ReportsGroup(BaseGroup):
    """
    holds the reports group
    
    """
    
    def __init__(self, group, **kwargs):
        
        super().__init__(group, **kwargs)
        
        self._defaults_summary_attrs = {'name': 'Summary',
                                  'max_shape': (1000,),
                                  'dtype': np.dtype([('name', 'S5'),
                                                     ('type', 'S32'),
                                                     ('summary', 'S200')])}
        
class StandardsGroup(BaseGroup):
    """
    holds the standards group
    
    """
    
    def __init__(self, group, **kwargs):
        
        super().__init__(group, **kwargs)
        
        self._defaults_summary_attrs = {'name': 'Summary',
                                  'max_shape': (500,),
                                  'dtype': np.dtype([('attribute', 'S72'),
                                                     ('type', 'S15'),
                                                     ('required', np.bool_),
                                                     ('style', 'S72'),
                                                     ('units', 'S32'),
                                                     ('description', 'S300'),
                                                     ('options', 'S150'),
                                                     ('alias', 'S72'),
                                                     ('example', 'S72')])} 
    
    def summary_table_from_dict(self, summary_dict):
        """
        Fill summary table from a dictionary 
        
        :param summary_dict: DESCRIPTION
        :type summary_dict: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        
        for key, v_dict in summary_dict.items():
            key_list = [key]
            for dkey in self.summary_table.dtype.names[1:]:
                value = v_dict[dkey]
                
                if isinstance(value, list):
                    if len(value) == 0:
                        value = ''
                        
                    else:
                        value = ','.join(['{0}'.format(ii) for ii in 
                                                  value])
                if value is None:
                    value = ''
                    
                key_list.append(value)
            
            key_list = np.array([tuple(key_list)], self.summary_table.dtype)
            index = self.summary_table.add_row(key_list)
            
        self.logger.debug(f'Added {index} rows to Standards Group')
        
    def initialize_group(self):
        """
        make summary table of standards
        :return: DESCRIPTION
        :rtype: TYPE

        """
        schema_obj = schema.Standards()
        self.summary_table_from_dict(schema_obj.summarize_standards())
        self.write_metadata()
        
        
class FiltersGroup(BaseGroup):
    """
    holds calibration group
    """
    
    def __init__(self, group, **kwargs):
        
        super().__init__(group, **kwargs)
    
        
class RunGroup(BaseGroup):
    """
    holds the run group
    """
   
    def __init__(self, group, run_metadata=None, **kwargs):
        
        super().__init__(group, group_metadata=run_metadata, **kwargs)
        
        self._defaults_summary_attrs = {'name': 'Summary',
                                        'max_shape': (20,),
                                        'dtype': np.dtype([
                                            ('component', 'S5'),
                                            ('start', 'S32'),
                                            ('end', 'S32'),
                                            ('n_samples', np.int),
                                            ('measurement_type', 'S12'),
                                            ('units', 'S25')])}
        
    def add_channel(self, channel_name, channel_type, data, channel_dtype='f',
                    max_shape=(None,), chunks=True, channel_metadata=None):
        """
        add a channel to the run
        
        :param name: DESCRIPTION
        :type name: TYPE
        :param channel_type: DESCRIPTION
        :type channel_type: TYPE
        :raises: MTH5Error if channel type is not correct
        
        :param channel_metadata: DESCRIPTION, defaults to None
        :type channel_metadata: TYPE, optional
        :return: DESCRIPTION
        :rtype: TYPE
        

        """
        if data is not None:
            if data.size < 1024:
                chunks = None
        try:
            if data is not None:
                channel_group = self.hdf5_group.create_dataset(channel_name,
                                                           data=data,
                                                           maxshape=max_shape,
                                                           dtype=data.dtype,
                                                           chunks=chunks)
            else:
                channel_group = self.hdf5_group.create_dataset(channel_name,
                                                           shape=(1, ),
                                                           maxshape=max_shape,
                                                           dtype=channel_dtype,
                                                           chunks=chunks)
            
            self.logger.debug("Created group {0}".format(channel_group.name))
            if channel_type.lower() in ['magnetic']:
                channel_obj = MagneticDataset(channel_group,
                                            channel_metdata=channel_metadata)
            elif channel_type.lower() in ['electric']:
                channel_obj = ElectricDataset(channel_group,
                                            channel_metdata=channel_metadata)
            elif channel_type.lower() in ['auxiliary']:
                channel_obj = AuxiliaryDataset(channel_group,
                                            channel_metdata=channel_metadata)
            else:
                msg = ("`channel_type` must be in [ electric | magnetic | " +
                       "auxiliary ]. Input was {0}".format(channel_type))
                self.logger.error(msg)
                raise MTH5Error(msg)
            channel_obj.write_metadata()
            self.summary_table.add_row(channel_obj.table_entry)
        
        except OSError:
            msg = (f"channel {channel_name} already exists, " +
                   "returning existing group.")
            self.logger.info(msg)
            if channel_type in ['magnetic']:
                channel_obj = MagneticDataset(self.hdf5_group[channel_name])
            elif channel_type in ['electric']:
                channel_obj = ElectricDataset(self.hdf5_group[channel_name])
            elif channel_type in ['auxiliary']:
                channel_obj = AuxiliaryDataset(self.hdf5_group[channel_name])
            channel_obj.read_metadata()
            
        return channel_obj
    
class ChannelDataset(BaseGroup):
    """
    holds a channel
    """
    
    def __init__(self, group, **kwargs):
        
        super().__init__(group, **kwargs)
        
    @property
    def _class_name(self):
        return self.__class__.__name__.split('Dataset')[0]
    
    @property
    def table_entry(self):
        """
        """
        
        return np.array([(self.metadata.component,
                         self.metadata.time_period.start,
                         self.metadata.time_period.end,
                         self.hdf5_group.size,
                         self.metadata.type,
                         self.metadata.units)],
                        dtype= np.dtype([('component', 'S5'),
                                         ('start', 'S32'),
                                         ('end', 'S32'),
                                         ('n_samples', np.int),
                                         ('measurement_type', 'S12'),
                                         ('units', 'S25')]))
        
class ElectricDataset(ChannelDataset):
    """
    holds a channel
    """
    
    def __init__(self, group, **kwargs):
        
        super().__init__(group, **kwargs)
        
class MagneticDataset(ChannelDataset):
    """
    holds a channel
    """
    
    def __init__(self, group, **kwargs):
        
        super().__init__(group, **kwargs)
        
class AuxiliaryDataset(ChannelDataset):
    """
    holds a channel
    """
    
    def __init__(self, group, **kwargs):
        
        super().__init__(group, **kwargs)
        
class MTH5Table():
    """
    Use the underlying NumPy basics, there are simple actions in this table, 
    if a user wants to use something more sophisticated for querying they 
    should try using a pandas table.  In this case entries in the table 
    are more difficult to change and datatypes need to be kept track of. 
    
    
    
    """
    
    def __init__(self, hdf5_dataset):
        self.logger = logging.getLogger('{0}.{1}'.format(
            __name__, self.__class__.__name__))
        
        if isinstance(hdf5_dataset, h5py.Dataset):
            self.array = weakref.ref(hdf5_dataset)()
        else:
            msg = "Input must be a h5py.Dataset not {0}".format(
                type(hdf5_dataset))
            self.logger.error(msg)
            raise MTH5TableError(msg)
            
    def __str__(self):
        """
        return a string that shows the table in text form
    
        :return: text representation of the table
        :rtype: string

        """
        length_dict = dict([(key, max([len(str(b)) for b in self.array[key]]))
                            for key in list(self.dtype.names)])
        lines = [' | '.join(['index']+['{0:^{1}}'.format(name, 
                                                         length_dict[name]) 
                             for name in list(self.dtype.names)])]
        lines.append('-' * len(lines[0]))
        for ii, row in enumerate(self.array):
            line = ['{0:^5}'.format(ii)]
            for element, key in zip(row, list(self.dtype.names)):
                if isinstance(element, (np.bytes_)):
                    element = element.decode()
                try:
                    line.append('{0:^{1}}'.format(element, length_dict[key]))
                
                except TypeError as error:
                    if isinstance(element, h5py.h5r.Reference):
                        msg = '{0}: Cannot represent h5 reference as a string'
                        self.logger.debug(msg.format(error))
                        line.append('{0:^{1}}'.format('<HDF5 object reference>',
                                                      length_dict[key]))
                    else:
                        self.logger.exception(f'{error}')
                        
            lines.append(' | '.join(line))
        return '\n'.join(lines)
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if isinstance(other, MTH5Table): 
            return self.array == other.array
        elif isinstance(other, h5py.Dataset):
            return self.array == other
        else:
            msg = "Cannot compare type={0}".format(type(other))
            self.logger.error(msg)
            raise TypeError(msg)
            
    def __ne__(self, other):
        return not self.__eq__(other) 

    def __len__(self):
        return self.array.shape[0]                    
            
    @property
    def dtype(self):
        try:
            return self.array.dtype
        except AttributeError as error:
            msg = '{0}, dataframe is not initiated yet'.format(error)
            self.logger.warning(msg)
            return None
        
    def check_dtypes(self, other_dtype):
        """
        Check to make sure datatypes match
        """
        
        if self.dtype == other_dtype:
            return True
        
        return False
    
    @property
    def shape(self):
        return self.array.shape
    
    @property
    def nrows(self):
        return self.array.shape[0]
    
    def locate(self, column, value, test='eq'):
        """
        
        locate index where column is equal to value
        :param column: DESCRIPTION
        :type column: TYPE
        :param value: DESCRIPTION
        :type value: TYPE
        :type test: type of test to try
            * 'eq': equals
            * 'lt': less than
            * 'le': less than or equal to
            * 'gt': greater than
            * 'ge': greater than or equal to.
            * 'be': between or equal to
            * 'bt': between
            
        If be or bt input value as a list of 2 values
            
        :return: DESCRIPTION
        :rtype: TYPE

        """
        if isinstance(value, str):
            value = np.bytes_(value)
            
        # use numpy datetime for testing against time.    
        if column in ['start', 'end', 'start_date', 'end_date']:
            test_array = self.array[column].astype(np.datetime64)
            value = np.datetime64(value)
        else:
            test_array = self.array[column]
        
        if test == 'eq':
            index_values = np.where(test_array == value)[0] 
        elif test == 'lt':
            index_values = np.where(test_array < value)[0]
        elif test == 'le':
            index_values = np.where(test_array <= value)[0]
        elif test == 'gt':
            index_values = np.where(test_array > value)[0]
        elif test == 'ge':
            index_values = np.where(test_array >= value)[0]
        elif test == 'be':
            if not isinstance(value, (list, tuple, np.ndarray)):
                msg = ("If testing for between value must be an iterable of" +
                      " length 2.")
                self.logger.error(msg)
                raise ValueError(msg)
                
            index_values = np.where((test_array > value[0]) & 
                                    (test_array < value[1]))[0]
        else:
            raise ValueError('Test {0} not understood'.format(test))
            
        return index_values
            
    def add_row(self, row, index=None):
        """
        Add a row to the table.
        
        row must be of the same data type as the table
        
        
        :param row: row entry for the table
        :type row: TYPE
        
        :param index: index of row to add
        :type index: integer, if None is given then the row is added to the
                     end of the array
                     
        :return: index of the row added
        :rtype: integer

        """
        
        if not isinstance(row, (np.ndarray)):
            msg = ("Input must be an numpy.ndarray" + 
                   "not {0}".format(type(row)))
        if isinstance(row, np.ndarray):
            if not self.check_dtypes(row.dtype):
                msg = '{0}\nInput dtypes:\n{1}\n\nTable dtypes:\n{2}'.format(
                    'Data types are not equal:', row.dtype, self.dtype)
                self.logger.error(msg)
                raise ValueError(msg)

        if index is None:
            index = self.nrows
            new_shape = tuple([self.nrows + 1] + [ii for ii in self.shape[1:]])
            self.array.resize(new_shape)
        
        # add the row
        self.array[index] = row
        self.logger.debug('Added row as index {0} with values {1}'.format(
            index, row))
        
        return index
        
