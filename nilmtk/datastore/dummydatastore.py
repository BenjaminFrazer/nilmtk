#!/usr/bin/env ipython

from copy import deepcopy
from os.path import isfile
import warnings

import numpy as np
import pandas as pd

from nilmtk.timeframe import TimeFrame
from nilmtk.timeframegroup import TimeFrameGroup
from .datastore import DataStore, MAX_MEM_ALLOWANCE_IN_BYTES
from nilmtk.docinherit import doc_inherit

class DummyDataStore(DataStore):

    @doc_inherit
    def __init__(self):
        with warnings.catch_warnings():
            # Silence pytables warnings with numpy, out of our control
            warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*numpy.ufunc size changed.*')

            self.store = None
            super(DummyDataStore, self).__init__() # this just creeates a blank timeframe

    @doc_inherit
    def get_timeframe(self, key):# coppied from hdf5datastore
        """
        Returns
        -------
        nilmtk.TimeFrame of entire table after intersecting with self.window.
        """
        data_start_date = self.store.select(key, [0]).index[0]
        data_end_date = self.store.select(key, start=-1).index[0]
        timeframe = TimeFrame(data_start_date, data_end_date)
        return self.window.intersection(timeframe)

    @property
    def window(self): # direct copy from hdf5 datastore
        return self._window

    @window.setter
    def window(self, window): #direct copy from hdf5 datastore
        window.check_tz()
        self._window = window
