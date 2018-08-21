import pyabf
import sys
from scipy.io import loadmat
import pynwb

# TODO
# add PoC pynwb

# IC Electrode
# ------------
#
# create_ic_electrode(name, device, source, description, slice=None, seal=None,
# location=None, resistance=None, filtering=None,
# initial_access_resistance=None)
#
# NWB File
# --------
#
# class pynwb.file.NWBFile(source, session_description, identifier,
# session_start_time, file_create_date=None, experimenter=None,
# experiment_description=None, session_id=None, institution=None, notes=None,
# pharmacology=None, protocol=None, related_publications=None, slices=None,
# source_script=None, source_script_file_name=None, data_collection=None,
# surgery=None, virus=None, stimulus_notes=None, lab=None, acquisition=None,
# stimulus=None, stimulus_template=None, epochs=None, epoch_tags=set(),
# trials=None, modules=None, ec_electrodes=None, ec_electrode_groups=None,
# ic_electrodes=None, imaging_planes=None, ogen_sites=None, devices=None,
# subject=None)
#
# source -> None
# session_start_time -> abfDateTime
# session_description -> abfFileComment
# identifier -> sha256(fileGUID + abfDateTime)
# experimenter -> None
# experiment_description -> uCreatorName + ABFcore.creatorVersion
# session_id -> abfID
#
# Device
# ------
#
# class pynwb.ecephys.Device(name, source, parent=None)
#
# name -> sTelegraphInstrument and sDigitizerType
# source -> None

def outputmetadata(filename):
    abf = pyabf.ABF(filename, preLoadData=False)
    abf._fileOpen()
    abf._readHeaders()
    abf.getInfoPage().generateHTML(saveAs=filename + ".meta.html")

    # for i in range(abf.sweepCount):
        # for j in range(abf.channelCount):
            # abf.setSweep(i, channel=j)
            # calculatedStimulus = abf.sweepC

    abf._fileClose()

def main(argv):
    for filename in argv[1:]:
        print(filename)
        outputmetadata(filename)
        # return

if __name__ == "__main__":
    main(sys.argv)
