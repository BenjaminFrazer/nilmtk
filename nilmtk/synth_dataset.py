#!/usr/bin/env ipython
from collections import OrderedDict
from nilmtk import datastore

from nilmtk.datastore.dummydatastore import DummyDataStore
from nilmtk.synth_metergroup import Synth_MeterGroup
from .building import Building

from nilmtk.dataset import DataSet
from .timeframe import TimeFrame


class Synth_DataSet(DataSet):
    # a synthetic dataset for a single 'building'

    def __init__(self):
        # TODO setup input arguments properly
        # self.DataSets = OrderedDict()
        self.buildings = OrderedDict()
        self.buildings[1] = Building()
        self.buildings[1].elec = Synth_MeterGroup()
        self.metadata = {'timezone': 'US/Eastern'}#'Europe/London'} # needs to be implemented to statisfy timezone
        self.store = DummyDataStore() # need to implement a custom datastore object that fuses two datastores, do we?
        self.alignDatasetMethod = None
        self.sampleRate = None # when set to `None`, the sample rate is upsampled by default to the highest supported by the dataset
        self.alignDatasetMethods = ['maxIntersection'] # supported methods for timeseries alignment
        self.doAlignDataset = self.alignDatasetMethods[0]  # should data from different sources be aligned to the same time index
        self._DataSet_Info = {}
        self._DataSet_Keys = [] # the name of the dataset as defined in metadata is used here
        self.datastores = OrderedDict() # all sub datastores in the synthetic set, indexed by datset name
        # i = 1 # this follows the nilmtk precident of indexing from 1
        # if type(filename) == list:
        #     for thisFile in filename:
        #         self.DataSets[i] = DataSet(thisFile,format)
        #         i+=1
        # elif type(filename) != None:
        #         self.DataSets[i] = DataSet(filename,format)

    def import_metadata(self, store, i):
        self._init_buildings(store[i])
        return self

    def append_metadata(self):
        # this function will append the metadata of a
        return self

    def add_meters_from_DataSet(self, metergroup, datasetIdx):
        #will add a dataset to the dataset dict and modify site and metadata apropriately
        # self._DataSet_Info[DataSet.metadata['name']] = {}
        # we assume that there is only one store per metergroup
        self.datastores[datasetIdx] = metergroup.meters[0].store
        for meter in metergroup.meters:
            self.buildings[1].elec.meters.append(meter)

    def set_window(self, start=None, end=None):
        """Set the timeframe window on self.store. Used for setting the
        'region of interest' non-destructively for all processing.

        Parameters
        ----------
        start, end : str or pd.Timestamp or datetime or None
        """
        if self.store is None:
            raise RuntimeError("You need to set self.store first!")

        tz = self.metadata.get('timezone')
        if tz is None:
            raise RuntimeError("'timezone' is not set in dataset metadata.")

        # TODO we need to set the correct timeframe for all sub datasets depending on relative alignment to the master timeframe
        for key, datastore in self.datastores.items():
            datastore.window = TimeFrame(start, end, tz)
