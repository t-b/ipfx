"""
Convert DAT files, created by PatchMaster, to NWB v2 files.
"""

from hashlib import sha256
from datetime import datetime
import os
import json
import warnings

import numpy as np

from pynwb.device import Device
from pynwb import NWBHDF5IO, NWBFile
from pynwb.icephys import IntracellularElectrode

from ipfx.x_to_nwb.hr_bundle import Bundle
from ipfx.x_to_nwb.hr_stimsetgenerator import StimSetGenerator
from ipfx.x_to_nwb.conversion_utils import PLACEHOLDER, V_CLAMP_MODE, I_CLAMP_MODE, \
     parseUnit, getStimulusSeriesClass, getAcquiredSeriesClass, createSeriesName, convertDataset, \
     getPackageInfo, getChannelRecordIndex, getStimulusRecordIndex, createCycleID


class DatConverter:

    def __init__(self, inFile, outFile, multipleGroupsPerFile=False):

        if not os.path.isfile(inFile):
            raise ValueError(f"The input file {inFile} does not exist.")

        self.bundle = Bundle(inFile)

        self._check()

        self.totalSeriesCount = self._getMaxTimeSeriesCount()

        def generateList(multipleGroupsPerFile, pul):
            """
            Return a list of groups from pul depending on multipleGroupsPerFile.
            """

            if multipleGroupsPerFile:
                return [pul]

            return [[x] for x in pul]

        for elem in generateList(multipleGroupsPerFile, self.bundle.pul):

            nwbFile = self._createFile()

            device = self._createDevice()
            nwbFile.add_device(device)

            self.electrodeDict = DatConverter._generateElectrodeDict(elem)
            electrodes = self._createElectrodes(device)
            nwbFile.add_ic_electrode(electrodes)

            for i in self._createAcquiredSeries(electrodes, elem):
                nwbFile.add_acquisition(i)

            for i in self._createStimulusSeries(electrodes, elem):
                nwbFile.add_stimulus(i)

            if multipleGroupsPerFile:
                outFileFmt = outFile
            else:
                name, suffix = os.path.splitext(outFile)
                outFileFmt = f"{name}-{elem[0].GroupCount}{suffix}"

            with NWBHDF5IO(outFileFmt, "w") as io:
                io.write(nwbFile, cache_spec=True)

    @staticmethod
    def outputMetadata(inFile):
        if not os.path.isfile(inFile):
            raise ValueError(f"The file {inFile} does not exist.")

        root, ext = os.path.splitext(inFile)

        with Bundle(inFile) as bundle:
            bundle._all_info(root + ".txt")

    @staticmethod
    def _getClampMode(ampState, trace):
        """
        Return the clamp mode of the given amplifier state node.
        """

        if ampState:
            clampMode = ampState.Mode

            if clampMode == "VCMode":
                return V_CLAMP_MODE
            elif clampMode == "CCMode":
                return I_CLAMP_MODE
            else:
                raise ValueError(f"Unknown clamp mode {clampMode}")

        warnings.warn("No amplifier state available, falling back to AD unit heuristics.")

        unit = trace.YUnit

        if unit == "A":
            return V_CLAMP_MODE
        elif unit == "V":
            return I_CLAMP_MODE
        else:
            raise ValueError(f"Unknown unit {unit}")

    def _getMaxTimeSeriesCount(self):
        """
        Return the maximum number of TimeSeries which will be created the DAT file contents.
        """

        counter = 0

        # We ignore the multipleGroupsPerFile flag here so that the sweep numbers are
        # independent of its value.
        for group in self.bundle.pul:
            for series in group:
                for sweep in series:
                    for _ in sweep:
                        counter += 1

        return counter

    @staticmethod
    def _generateElectrodeKey(trace):

        # Using LinkDAChannel and SourceChannel here as these look correct

        DAC = trace.LinkDAChannel
        ADC = trace.SourceChannel

        return f"{DAC}_{ADC}"

    @staticmethod
    def _generateElectrodeDict(groups):
        """
        Generate a dictionary of all electrodes in the file.
        Use self._generateElectrodeKey(trace) for generating the key, the
        value will be the electrode number.
        """

        electrodes = {}
        index = 0

        for group in groups:
            for series in group:
                for sweep in series:
                    for trace in sweep:
                        key = DatConverter._generateElectrodeKey(trace)
                        if electrodes.get(key) is None:
                            electrodes[key] = index
                            index += 1

        return electrodes

    @staticmethod
    def _formatDeviceString(ampStateRecord):

        kind = ampStateRecord.AmplifierState.AmplKind
        numBoards = ampStateRecord.AmplifierState.E9Boards
        suffix = ampStateRecord.AmplifierState.IsEpc9N
        DAC = ampStateRecord.AmplifierState.ADBoard

        return f"{kind}-{numBoards}-{suffix} with {DAC}"

    @staticmethod
    def _convertTimestamp(heka_elapsed_seconds):
        """
        Convert a timestamp in heka format to datetime

        The documentation in Time.txt of FileFormat_v9.zip gives a working
        example in C but the comments are contradicting the code.

        The solution here is therefore reverse engineered and tested on a few examples.
        """

        JanFirst1990 = 1580970496.0
        delta = datetime(1970, 1, 1) - datetime(1904, 1, 1)
        secondsSinceUnixEpoch = heka_elapsed_seconds - JanFirst1990 - delta.total_seconds() + 16096

        return datetime.fromtimestamp(secondsSinceUnixEpoch)

    @staticmethod
    def _isValidAmplifierState(ampState):
        return len(ampState.StateVersion) > 0

    @staticmethod
    def _getAmplifierState(bundle, series, trace_index):
        """ Return the amplifier state object taking into account different PatchMaster versions """

        ampState = series.AmplifierState

        # try the default location first
        if DatConverter._isValidAmplifierState(ampState):
            return ampState

        # newer Patchmaster versions store it in the Amplifier tree
        ampState = bundle.amp[series.AmplStateSeries - 1][trace_index].AmplifierState

        if DatConverter._isValidAmplifierState(ampState):
            return ampState

        # and sometimes we got nothing at all
        return None

    def _check(self):
        """
        Check that all prerequisites are met.
        """

        if not self.bundle.header.IsLittleEndian:
            raise ValueError("Not tested with BigEndian data from a Mac.")
        elif not self.bundle.amp:
            raise ValueError("The amp tree does not exist.")
        elif not self.bundle.pul:
            raise ValueError("The pul tree does not exist.")
        elif not self.bundle.data:
            raise ValueError("The data element does not exist.")
        elif len(self.bundle.amp) < 1 or len(self.bundle.amp[0]) < 1:
            raise ValueError("Unexpected amplifier tree structure.")

        # check that the used device is unique
        deviceString = DatConverter._formatDeviceString(self.bundle.amp[0][0])

        for series_index, series in enumerate(self.bundle.amp):
            for state_index, state in enumerate(series):

                # skip invalid entries
                if not DatConverter._isValidAmplifierState(state.AmplifierState):
                    continue

                if deviceString != DatConverter._formatDeviceString(state):
                    raise ValueError(f"Device strings differ in tree structure " +
                                     f"({deviceString} vs {DatConverter._formatDeviceString(state)} " +
                                     f"at {series_index}.{state_index})")

        # check trace properties
        for group in self.bundle.pul:
            for series in group:
                for sweep in series:
                    for trace in sweep:
                        if trace.XUnit != "s":
                            raise ValueError(f"Expected unit 's' for x-axis of the trace")
                        elif trace.AverageCount != 1:
                            raise ValueError(f"Unexpected average count of {trace.AverageCount}")
                        elif trace.DataKind["IsLeak"]:
                            raise ValueError(f"Leak traces are not supported.")
                        elif trace.DataKind["IsVirtual"]:
                            raise ValueError(f"Virtual traces are not supported.")

    def _createFile(self):
        """
        Create a pynwb NWBFile object from the DAT file contents.
        """

        session_description = PLACEHOLDER
        identifier = sha256(b'%d_' % self.bundle.header.Time + str.encode(datetime.now().isoformat())).hexdigest()
        self.session_start_time = DatConverter._convertTimestamp(self.bundle.header.Time)
        creatorName = "PatchMaster"
        creatorVersion = self.bundle.header.Version
        experiment_description = f"{creatorName} {creatorVersion}"
        source_script_file_name = "run_x_to_nwb_conversion.py"
        source_script = json.dumps(getPackageInfo(), sort_keys=True, indent=4)
        session_id = PLACEHOLDER

        return NWBFile(session_description=session_description,
                       identifier=identifier,
                       session_start_time=self.session_start_time,
                       experimenter=None,
                       experiment_description=experiment_description,
                       session_id=session_id,
                       source_script=source_script,
                       source_script_file_name=source_script_file_name)

    def _createDevice(self):
        """
        Create a pynwb Device object from the DAT file contents.
        """

        name = DatConverter._formatDeviceString(self.bundle.amp[0][0])

        return Device(name)

    def _createElectrodes(self, device):
        """
        Create pynwb ic_electrodes objects from the DAT file contents.
        """

        return [IntracellularElectrode(f"Electrode {x:d}",
                                       device,
                                       description=PLACEHOLDER)
                for x in self.electrodeDict.values()]

    def _getStartingTime(self, sweep):
        """
        Get the starting time in seconds of the sweep relative to the NWB
        session start time.

        Parameters
        ----------
        sweep: SweepRecord

        Returns
        -------
        starting time: seconds since NWB file epoch
        """

        sweepTime = DatConverter._convertTimestamp(sweep.Time)
        return (sweepTime - self.session_start_time).total_seconds()

    def _createStimulusSeries(self, electrodes, groups):
        """
        Return a list of pynwb stimulus series objects created from the DAT file contents.
        """

        generator = StimSetGenerator(self.bundle)
        nwbSeries = []
        counter = 0

        for group in groups:
            for series in group:
                for sweep in series:
                    cycle_id = createCycleID([group.GroupCount, series.SeriesCount, sweep.SweepCount],
                                             total=self.totalSeriesCount)
                    stimRec = self.bundle.pgf[getStimulusRecordIndex(sweep)]
                    for trace_index, trace in enumerate(sweep):
                        stimset = generator.fetch(sweep, trace)

                        if not len(stimset):
                            print(f"Can not yet recreate stimset {series.Label}")
                            continue

                        name, counter = createSeriesName("index", counter, total=self.totalSeriesCount)

                        sweepIndex = sweep.SweepCount - 1
                        data = convertDataset(stimset[sweepIndex])

                        electrodeKey = DatConverter._generateElectrodeKey(trace)
                        electrode = electrodes[self.electrodeDict[electrodeKey]]
                        gain = 1.0
                        resolution = np.nan
                        stimulus_description = series.Label
                        starting_time = self._getStartingTime(sweep)
                        rate = 1.0 / stimRec.SampleInterval
                        description = json.dumps({"cycle_id": cycle_id,
                                                  "file": os.path.basename(self.bundle.file_name),
                                                  "group_label": group.Label,
                                                  "series_label": series.Label,
                                                  "sweep_label": sweep.Label},
                                                 sort_keys=True, indent=4)

                        channelRec_index = getChannelRecordIndex(self.bundle.pgf, sweep, trace)
                        assert channelRec_index is not None, "Unexpected channel record index"

                        ampState = DatConverter._getAmplifierState(self.bundle, series, trace_index)
                        clampMode = DatConverter._getClampMode(ampState, trace)

                        if clampMode == V_CLAMP_MODE:
                            conversion, unit = 1e-3, "V"
                        elif clampMode == I_CLAMP_MODE:
                            conversion, unit = 1e-12, "A"

                        seriesClass = getStimulusSeriesClass(clampMode)

                        timeSeries = seriesClass(name=name,
                                                 data=data,
                                                 sweep_number=np.uint64(cycle_id),
                                                 unit=unit,
                                                 electrode=electrode,
                                                 gain=gain,
                                                 resolution=resolution,
                                                 rate=rate,
                                                 stimulus_description=stimulus_description,
                                                 starting_time=starting_time,
                                                 conversion=conversion,
                                                 description=description)

                        nwbSeries.append(timeSeries)

        return nwbSeries

    def _createAcquiredSeries(self, electrodes, groups):
        """
        Return a list of pynwb acquisition series objects created from the DAT file contents.
        """

        nwbSeries = []
        counter = 0

        for group in groups:
            for series in group:
                for sweep in series:
                    cycle_id = createCycleID([group.GroupCount, series.SeriesCount, sweep.SweepCount],
                                             total=self.totalSeriesCount)
                    for trace_index, trace in enumerate(sweep):
                        name, counter = createSeriesName("index", counter, total=self.totalSeriesCount)
                        data = convertDataset(self.bundle.data[trace])

                        ampState = DatConverter._getAmplifierState(self.bundle, series, trace_index)

                        if ampState:
                            gain = ampState.Gain
                        else:
                            gain = np.nan

                        conversion, unit = parseUnit(trace.YUnit)
                        electrodeKey = DatConverter._generateElectrodeKey(trace)
                        electrode = electrodes[self.electrodeDict[electrodeKey]]

                        resolution = np.nan
                        starting_time = self._getStartingTime(sweep)
                        rate = 1.0 / trace.XInterval
                        description = json.dumps({"cycle_id": cycle_id,
                                                  "file": os.path.basename(self.bundle.file_name),
                                                  "group_label": group.Label,
                                                  "series_label": series.Label,
                                                  "sweep_label": sweep.Label},
                                                 sort_keys=True, indent=4)
                        clampMode = DatConverter._getClampMode(ampState, trace)
                        seriesClass = getAcquiredSeriesClass(clampMode)
                        stimulus_description = series.Label

                        # TODO check amplifier settings mapping from Patchmaster to NWB
                        if clampMode == V_CLAMP_MODE:

                            if ampState and ampState.RsOn:
                                resistance_comp_correction = ampState.RsFraction
                                whole_cell_series_resistance_comp = ampState.RsValue
                            else:
                                resistance_comp_correction = np.nan
                                whole_cell_series_resistance_comp = np.nan

                            whole_cell_capacitance_comp = np.nan
                            resistance_comp_bandwidth = np.nan
                            resistance_comp_prediction = np.nan

                            if ampState and (ampState.AutoCFast or (ampState.CanCCFast and ampState.CCCFastOn)):
                                # stored in two doubles for enhanced precision
                                capacitance_fast = ampState.CFastAmp1 + ampState.CFastAmp2
                            else:
                                capacitance_fast = np.nan

                            if ampState and (ampState.AutoCSlow or (ampState.CanCCFast and not ampState.CCCFastOn)):
                                capacitance_slow = ampState.CSlow
                            else:
                                capacitance_slow = np.nan

                            acquistion_data = seriesClass(name=name,
                                                          data=data,
                                                          sweep_number=np.uint64(cycle_id),
                                                          unit=unit,
                                                          electrode=electrode,
                                                          gain=gain,
                                                          resolution=resolution,
                                                          conversion=conversion,
                                                          starting_time=starting_time,
                                                          rate=rate,
                                                          description=description,
                                                          capacitance_slow=capacitance_slow,
                                                          capacitance_fast=capacitance_fast,
                                                          resistance_comp_correction=resistance_comp_correction,
                                                          resistance_comp_bandwidth=resistance_comp_bandwidth,
                                                          resistance_comp_prediction=resistance_comp_prediction,
                                                          whole_cell_capacitance_comp=whole_cell_capacitance_comp,
                                                          stimulus_description=stimulus_description,
                                                          whole_cell_series_resistance_comp=whole_cell_series_resistance_comp)  # noqa: E501

                        elif clampMode == I_CLAMP_MODE:
                            bias_current = trace.Holding

                            if ampState and (ampState.AutoCFast or (ampState.CanCCFast and ampState.CCFastOn)):
                                # stored in two doubles for enhanced precision
                                capacitance_compensation = ampState.CFastAmp1 + ampState.CFastAmp2
                            elif ampState and (ampState.AutoCSlow or (ampState.CanCCFast and not ampState.CCFastOn)):
                                capacitance_compensation = ampState.CSlow
                            else:
                                capacitance_compensation = np.nan

                            if ampState:
                                bridge_balance = ampState.RsValue * ampState.RsFraction
                            else:
                                bridge_balance = np.nan

                            acquistion_data = seriesClass(name=name,
                                                          data=data,
                                                          sweep_number=np.uint64(cycle_id),
                                                          unit=unit,
                                                          electrode=electrode,
                                                          gain=gain,
                                                          resolution=resolution,
                                                          conversion=conversion,
                                                          starting_time=starting_time,
                                                          rate=rate,
                                                          description=description,
                                                          bias_current=bias_current,
                                                          bridge_balance=bridge_balance,
                                                          stimulus_description=stimulus_description,
                                                          capacitance_compensation=capacitance_compensation)
                        else:
                            raise ValueError(f"Unsupported clamp mode {clampMode}.")

                        nwbSeries.append(acquistion_data)

        return nwbSeries
