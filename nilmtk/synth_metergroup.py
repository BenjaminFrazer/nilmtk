#!/usr/bin/env ipython
from nilmtk.dataset import DataSet
from nilmtk.elecmeter import ElecMeter
from nilmtk.metergroup import MeterGroup
import pandas as pd
import pytz
from datetime import timedelta

class Synth_MeterGroup(MeterGroup):
    def __init__(self, meters=None, disabled_meters=None, master_time_origin=None):
        self.master_time_origin = master_time_origin;
        super().__init__(meters, disabled_meters)

    def mains(self):
        if self.contains_meters_from_multiple_buildings():
            # datasets = self.dataset()
            # buildings = self.building()
            # for dataset in datasets:
            #     for building in buildings:
            site_meters = [meter for meter in self.meters if meter.is_site_meter()]
            n_site_meters = len(site_meters)

            if n_site_meters == 0:
                return
            elif n_site_meters == 1:
                return site_meters[0]
            else:
                return MeterGroup(meters=site_meters)

        else:
            return super(Synth_MeterGroup, self).mains()

    def __getitem__(self, key): # overwrite to deal with multiple datasets and buildings in one metergroup
        # TODO I should probabaly complile a list of appliances matching key because it could be that the default dataset
        # and building dont actualy have the target device
        if isinstance(key, tuple):
            # default to get first meter and first dataset
            meters=[]
            if len(key) == 2:
            # we have to choose the buildings and dataset keyword together since
            # we might not have provided the same buildings for both datasets
                if isinstance(key[0], str):
                    keyDict = {'type': key[0],'instance': key[1]}
                    for meter in self.meters:
                        # try:
                        #     if meter.appliances[0].type['type']=='fridge':
                        #         import pdb; pdb.set_trace()
                        # except:
                        #     pass
                        if meter.matches_appliances(keyDict):
                            meters.append(meter)

                    selected_meter = meters[0]
                    dataset = selected_meter.dataset() # i think this will always be just one dataset
                    building = selected_meter.building() # i think this will always be just one dataset
                    print("Selecting {device} from dataset {dataset}, building {building}".format(device=key[0],dataset=dataset,building=building)) # format()
                    # return super(Synth_MeterGroup,self).__getitem__({'type': key[0], 'instance': key[1], 'dataset': datasets[0], 'building': buildings[0]})
                    return meters[0]
        elif isinstance(key, dict): # if we return multiple matches to the key we just shove them in a metergroup and return that
            meters = []
            for meter in self.meters:
                if meter.matches_appliances(key):
                    meters.append(meter)
            if len(meters) == 1:
                return meters[0]
            else:
                return Synth_MeterGroup(meters)
        return super(Synth_MeterGroup,self).__getitem__(key) # default superclass behaviour

    def get_timeframe(self):
        # TODO this will probabaly have to be altered
        """
        Returns
        -------
        nilmtk.TimeFrame representing the timeframe which is the union
            of all meters in self.meters.
        """
        timeframe = None
        for meter in self.meters:
            if timeframe is None:
                timeframe = meter.get_timeframe()
            elif meter.get_timeframe().empty:
                pass
            else:
                timeframe = timeframe.union(meter.get_timeframe())
        return timeframe

    def calc_alignment_offset(self, method='front', master_time_origin=None, master_tz=None):
        if master_time_origin !=None:
            self.master_time_origin=master_time_origin
        if self.master_time_origin==None:
            self.master_time_origin=self.meters[0].get_timeframe()
        # timzone = self.
        master_tz = pytz.timezone('US/Eastern') # how do we get this from

        for dataset in self.dataset():
        # TODO optional flag to allign buildings as well
            datasetMetergroup = self[{'dataset':dataset}]
            thisTimeframe = datasetMetergroup.get_timeframe()
            # TODO correct for timezone localization, so allign data but such that it is the same local time for all sets
            # eastern = pytz.timezone('US/Eastern')
            # df.index = df.index.tz_localize(pytz.utc).tz_convert(eastern)
            thisDelta = master_time_origin - thisTimeframe.start

            for meter in datasetMetergroup:
                meter.alignment_timeshift = thisDelta

        return


    # def _calc_meter_alignment_offset(self,meter,master_time_origin, origin_timezone, method='front'):
    #     """
    #     Returns
    #     -------
    #     timedelta representing the timeshift required to alighn the start of this meter's time with the selected time origin
    #     """
    #     assert isinstance(meter, ElecMeter)

    #     meter_timeframe = meter.get_timeframe()
    #     master_time_origin = pd.datetime(2011,1,1) # for testing

    #     return
