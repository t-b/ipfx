# Converter from X to NWB V2.0

# Plan for converting the PClamp/Patchmaster files to NWB

We want to convert the data from two proprietary data formats `ABF` (PClamp
[Axon, Moleclular Devices] and `DAT` (Patchmaster [Heka, Harvard Bioscience])
to NeuroDataWithoutBorders v2.0.

Based on our current understanding and perlimiary tests we have devised the
following plan forward.

## ABF

Read the acquired data using [pyABF](https://github.com/swharden/pyABF). This
library has a compatible license (MIT-license) and does not use the proprietary
ABFFIO.dll (so we can freely distribute everything). It supports reconstructing
the protocol from its parametric form (as stored in the ABF file) to array data
for the most commonly used setups. It does not support reconstructing the
protocol if Waveform Epochs are used, but we plan to add that support.

## DAT

Read the acquired data using
[heka_reader](https://github.com/campagnola/heka_reader) as starting point.
There is no license attached to the project, but the author of that package
works at the Allen Institute. No proprietary libraries are used as well. The
script does currently not support protocol reconstruction, we plan at the
moment to get the protocol in array form using the Matlab export of
Patchmaster. We might revisit the decision for using the Matlab export, based on
our experience with the ABF format, as the exported Matlab files are in the
range of giga bytes.

## Patchmaster file format

### Versions

* 2x90, 2x73 and 2x65
* Demo version available from http://www.heka.com/downloads/downloads_main.html

### Manufacturer documentation

* ftp://server.hekahome.de/pub/FileFormat/Patchmasterv9/

* Sample data (DemoV9Bundle.dat): http://www.heka.com/downloads/software/demodata/patchmaster_demodata.zip

### Existing tools for reading patchmaster files

* http://sigtool.sourceforge.net/
* https://github.com/neurodroid/stimfit
* https://github.com/campagnola/heka_reader

#### Files and their versions

'v2x90.1, 29-feb-2016'

* H18.28.015.11.12.dat
* H18.28.015.11.14.dat
* H18.28.015.11.17.dat
* H18.28.016.11.06.dat
* H18.28.018.11.04.dat
* H18.28.018.11.05.dat
* H18.28.018.11.06.dat
* H18.28.018.11.07.dat

v2x73

* none yet

'v2x65, 19-Dec-2011'

* H18.28.019.11.04.dat
* H18.28.019.11.06.dat

#### Observations

* Traces mention the stimset they were acquired with in `SeriesRecord.Label`
  matching `StimulationRecord.EntryName`
* Stimsets are stored in parametric form and not as numeric array data

* Patchmaster: How to Export
  * Open file
  * Export settings:
    * Check `Replay->Export Mode->Traces`
    * Check `Replay->Export Mode->Stimuli`
    * Select `Replay->Export Format->Igor Pro`
    * Select `Replay->Export Format->Trace Time relative to Sweep`
    * Select `Replay->Export Format->Create Text Wave`
  * Select Replay Window
  * Select root node
  * Choose `Replay->Export`

And likewise for ASCII and Matlab export.

##### Comparison of different export formats

Export of file `H18.28.015.11.12.dat`

Igor Pro: Uses Igor Text file format (itx) as only that is self contained
          without referencing the binary dat file itself. Using the export option `Create
          Binary Wave` uses a mixture of data in the itx file (stimulus data) and ibw
          (Igor Binary files for the Traces) which only complicates things.

          Properties:
            * File Size: 1.5GB
            * Separate waves for data and stimuli
            * Clear text (but includes Igor Code)

          Comparison:
            + Can be parsed with any language
            + Trace and Stimulus has SI units attached

ASCII: Custom ASCII format, resembling a mixture of CSV format and blocks

        Properties:
          * File Size: 5.1GB
          * Multi column csv files with varying column number
          * Includes pseudo-header

        Comparison:
          + Can be parsed with any language
          + Trace and Stimulus has SI units attached
          - Data in columns includes si prefixes (not always though)

mat: Matlab files

        Properties:
        * File Size: 2GB
        * Format: M5, old style proprietary and not HDF5

        Comparison:
          + Can be read with python
            (https://scipy-cookbook.readthedocs.io/items/Reading_mat_files.html)
            and Igor Pro without manual parsing
          - Trace and Stimulus does not contain units. The units can be read
            out from the dat file though.

Thomas' suggestion would be to use the matlab file as that is the easiest to
read and smaller than the ASCII file. For the metadata we have to inspect the
dat file anyway so we can read the units as well.

## pClamp fileformat

### Manufacturer documentation

* http://mdc.custhelp.com/app/answers/detail/a_id/18881/kw/abf includes the ABF User Guide and a tool to view the metadata
* https://www.moleculardevices.com/products/axon-patch-clamp-system/acquisition-and-analysis-software/pclamp-software-suite#Resources
* See also https://github.com/swharden/pyABF/tree/master/docs/advanced/abf-file-format
* ATF file format: https://mdc.custhelp.com/app/answers/detail/a_id/18883/~/genepix%C2%AE-file-formats

### Versions

* Fileformat: ABF V2.06
* Acquiring Software: Clampex 10.7

### Software for reading ABF files

There is no way to export the raw protocol data from Clampex/Axoscope.

pyABF is pure python code which reversed engineered the ABF2 file format.
License is MIT.

One ABF file per protocol.

* git clone https://github.com/swharden/pyABF
* cd pyABF/src
* pip install -e .

Example invocation:
```
>>> import pyabf
>>> abf = pyabf.ABF('../sample_data/PHS4_180320_201/2018_03_20_0000.abf')
>>> print(abf)
ABF file (2018_03_20_0000.abf) with 2 channels, 1 sweep, and a total length of 0.30 min.
>>> abf.setSweep(0)
>>> print(abf.sweepX)
[0.000000e+00 2.000000e-05 4.000000e-05 ... 1.799994e+01 1.799996e+01 1.799998e+01]
>>> print(abf.sweepY)
[-1332.6415 -1332.2753 -1331.2987 ... -1354.0038 -1354.0038 -1353.5155]
>>> print(abf.sweepC)
[0. 0. 0. ... 0. 0. 0.]
>>> print(abf.sweepD)
<bound method ABFcore.sweepD of <pyabf.abf.ABF object at 0x0000000002A4C048>>
>>> abf._fileOpen()
>>> abf._readHeaders()
>>> abf.getInfoPage().launchTempWebpage()
C:\Users\thomas\AppData\Local\Temp\tmpm5gh9gvd/header.html
```

#### Abandoned projects

https://bitbucket.org/cleemesser/python-axonbinaryfile (requires ABFFIO.dll)
https://sourceforge.net/projects/libaxon/

### pCLamp issues

* Latest version 11.x can not recreate the protocol from clampex 10.7. The scaling of
  the levels has to be manually changed from mV to V (aka divide the numbers by 1e3).

# TODO

# Merged PRs
- Fix display of icephys example: https://github.com/NeurodataWithoutBorders/pynwb/pull/548
- Create a separate file for the Device object: https://github.com/NeurodataWithoutBorders/pynwb/pull/573
- Feature/enhance protocol section: https://github.com/swharden/pyABF/pull/26
- Feature/better epoch handling: https://github.com/swharden/pyABF/pull/23
- Feature/better header parsing: https://github.com/swharden/pyABF/pull/22
- Format string in ISO8601 format: https://github.com/swharden/pyABF/pull/27
- Enhance set sweep: https://github.com/swharden/pyABF/pull/28
- Epochs/Support loading custom waveforms from ATF files: https://github.com/swharden/pyABF/pull/29
- TimeSeries: Rename rate_unit variable and use it correctly :https://github.com/NeurodataWithoutBorders/pynwb/pull/581

# Open PRs
- Prefer device over device name and use links: https://github.com/NeurodataWithoutBorders/pynwb/pull/582
- Use NaN as default resolution for TimeSeries objects: https://github.com/NeurodataWithoutBorders/pynwb/pull/417
