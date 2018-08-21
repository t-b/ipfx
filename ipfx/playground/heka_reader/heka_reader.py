#!/usr/bin/env python

"""
Heka Patchmaster .dat file reader

Structure definitions adapted from StimFit hekalib.cpp

Brief example::

    # Load a .dat file
    bundle = Bundle(file_name)

    # Select a trace
    trace = bundle.pul[group_ind][series_ind][sweep_ind][trace_ind]

    # Print meta-data for this trace
    print(trace)

    # Load data for this trace
    data = bundle.data[group_id, series_id, sweep_ind, trace_ind]

"""

import numpy as np
import sys

from hr_nodes import (Pulsed, StimulusTemplate, AmplifierFile, ProtocalMethod,
                      Solutions, Marker, BundleHeader)


class Data():
    def __init__(self, bundle, offset=0, size=None):
        self.bundle = bundle
        self.offset = offset

    def __getitem__(self, *args):
        index = args[0]
        assert len(index) == 4
        pul = self.bundle.pul
        trace = pul[index[0]][index[1]][index[2]][index[3]]
        bundle.fh.seek(trace.Data)
        fmt = bytearray(trace.DataFormat)[0]
        dtype = [np.int16, np.int32, np.float16, np.float32][fmt]
        data = np.fromfile(fh, count=trace.DataPoints, dtype=dtype)
        return data * trace.DataScaler + trace.ZeroData


class Bundle():

    item_classes = {
        '.pul': Pulsed,
        '.dat': Data,
        '.pgf': StimulusTemplate,
        '.amp': AmplifierFile,
        '.mth': ProtocalMethod,
        '.sol': Solutions,
        '.mrk': Marker
    }

    def __init__(self, file_name):
        self.file_name = file_name
        self.fh = open(file_name, 'rb')

        # Read header assuming little endian
        endian = '<'
        self.header = BundleHeader(self.fh, endian)

        # If the header is bad, re-read using big endian
        if not self.header.IsLittleEndian:
            endian = '>'
            self.fh.seek(0)
            self.header = BundleHeader(self.fh, endian)

        # catalog extensions of bundled items
        self.catalog = {}
        for item in self.header.BundleItems:
            item.instance = None
            ext = item.Extension
            self.catalog[ext] = item

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fh.close()

    @property
    def pul(self):
        """The Pulsed object from this bundle.
        """
        return self._get_item_instance('.pul')

    @property
    def data(self):
        """The Data object from this bundle.
        """
        return self._get_item_instance('.dat')

    @property
    def pgf(self):
        """The Stimulus Template object from this bundle.
        """
        return self._get_item_instance('.pgf')

    @property
    def amp(self):
        """The Amplifier object from this bundle.
        """
        return self._get_item_instance('.amp')

    @property
    def mth(self):
        """The ProtocalMethod object from this bundle.
        """
        return self._get_item_instance('.mth')

    @property
    def sol(self):
        """The Solutions object from this bundle.
        """
        return self._get_item_instance('.sol')

    @property
    def mrk(self):
        """The Solutions object from this bundle.
        """
        return self._get_item_instance('.mrk')

    def _get_item_instance(self, ext):
        if ext not in self.catalog:
            return None

        item = self.catalog[ext]
        if item.instance is not None:
            return item.instance

        self.fh.seek(item.Start)

        # read endianess magic
        magic = self.fh.read(4)
        if magic == b'eerT':
            endianess = '<'
        elif magic == b'Tree':
            endianess = '>'
        else:
            raise RuntimeError('Bad file magic: %s' % magic)

        cls = self.item_classes[ext]
        item.instance = cls(self.fh, endianess)

        return item.instance

    def __repr__(self):
        return "Bundle(%r)" % list(self.catalog.keys())

    def _all_info(self, outputFile=None):

        if outputFile is not None:
            fh = open(outputFile, 'w')
        else:
            fh = None

        print(self.header, file=fh)
        print(self.pul, file=fh)
        print(self.pgf, file=fh)
        print(self.amp, file=fh)
        # ProtocalMethods are empty
        # print(self.mth, file=fh)
        print(self.sol, file=fh)
        print(self.mrk, file=fh)

        print('#' * 80, file=fh)

        # Root
        #   Groups
        #     Series
        #       Sweeps
        #         Traces

        for group in self.pul:
            print(group, file=fh)
            for series in group:
                print(series, file=fh)
                for sweep in series:
                    print(sweep, file=fh)
                    for trace in sweep:
                        print(trace, file=fh)

        print('#' * 80, file=fh)

        # Root
        #   Stimulation
        #     Channel
        #       StimSegment

        for stimulation in self.pgf:
            print(stimulation, file=fh)
            for channel in stimulation:
                print(channel, file=fh)
                for stimsegment in channel:
                    print(stimsegment, file=fh)


def main(argv):
    for filename in argv[1:]:
        with Bundle(filename) as bundle:
            bundle._all_info(filename + ".pymeta")


if __name__ == "__main__":
    main(sys.argv)
