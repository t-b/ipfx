"""
All supported nodes are listed here. The root node of each bundle call the
TreeNode constructor explicitly the other are plain children of the root nodes.

Documentation:
    * https://github.com/neurodroid/stimfit/blob/master/src/libstfio/heka/hekalib.cpp
    * ftp://server.hekahome.de/pub/FileFormat/Patchmasterv9/
"""

from hr_treenode import TreeNode
from hr_struct import Struct


def cstr(byte):
    """Convert C string bytes to python string.
    """
    try:
        ind = byte.index(b'\0')
    except ValueError:
        print("Could not find a trailing '\\0'!")
        return byte
    return byte[:ind].decode('utf-8', errors='ignore')


class Marker(TreeNode):

    field_info = [
        ('Version', 'i'),  # (* INT32 *)
        ('CRC', 'i'),      # (* CARD32 *)
    ]

    required_size = 8

    rectypes = [
        None
    ]

    def __init__(self, fh, endianess):
        TreeNode.__init__(self, fh, endianess, self.rectypes, None)


class Solutions(TreeNode):

    field_info = [
        ('RoVersion', 'H'),               # (* INT16 *)
        ('RoDataBaseName', '80s', cstr),  # (* SolutionNameSize *)
        ('RoSpare1', 'H', None),          # (* INT16 *)
        ('RoCRC', 'i'),                   # (* CARD32 *)
    ]

    required_size = 88

    rectypes = [
        None
    ]

    def __init__(self, fh, endianess):
        TreeNode.__init__(self, fh, endianess, self.rectypes, None)


class ProtocalMethod(TreeNode):

    field_info = [
        ('Version', 'i'),              # (* INT32 *)
        ('Mark', 'i'),                 # (* INT32 *)
        ('VersionName', '32s', cstr),  # (* String32Type *)
        ('MaxSamples', 'i'),           # (* INT32 *)
        ('Filler1', 'i', None),        # (* INT32 *)
        ('Params', '10s', cstr),       # (* ARRAY[0..9] OF LONGREAL
                                       # ('StimParams', ''),    *)
        ('ParamText', '320s', cstr),   # (* ARRAY[0..9],[0..31]OF CHAR
                                       # ('StimParamChars', '') *)
        ('Reserved', '128s', None),    # (* String128Type *)
        ('Filler2', 'i', None),        # (* INT32 *)
        ('CRC', 'i'),                  # (* CARD32 *)
    ]

    required_size = 514

    rectypes = [
        None
    ]

    def __init__(self, fh, endianess):
        TreeNode.__init__(self, fh, endianess, self.rectypes, None)


class AmplifierFile(TreeNode):

    field_info = [
        ('Version', 'i'),                # (* INT32 *)
        ('Mark', 'i'),                   # (* INT32 *)
        ('VersionName', '32s', cstr),    # (* String32Type *)
        ('AmplifierName', '32s', cstr),  # (* String32Type *)
        ('Amplifier', 'c'),              # (* CHAR *)
        ('ADBoard', 'c'),                # (* CHAR *)
        ('Creator', 'c'),                # (* CHAR *)
        ('Filler1', 'c', None),          # (* BYTE *)
        ('CRC', 'i')                     # (* CARD32 *)
    ]

    required_size = 80

    rectypes = [
        None
    ]

    def __init__(self, fh, endianess):
        TreeNode.__init__(self, fh, endianess, self.rectypes, None)


class UserParamDescrType(Struct):
    field_info = [
        ('Name', '32s', cstr),
        ('Unit', '8s', cstr),
    ]

    required_size = 40


class LockInParams(Struct):
    field_info = [
        ('ExtCalPhase', 'd'),      # (* LONGREAL *)
        ('ExtCalAtten', 'd'),      # (* LONGREAL *)
        ('PLPhase', 'd'),          # (* LONGREAL *)
        ('PLPhaseY1', 'd'),        # (* LONGREAL *)
        ('PLPhaseY2', 'd'),        # (* LONGREAL *)
        ('UsedPhaseShift', 'd'),   # (* LONGREAL *)
        ('UsedAttenuation', 'd'),  # (* LONGREAL *)
        ('Spares2', 'd', None),    # (* LONGREAL *)
        ('ExtCalValid', '?'),      # (* BOOLEAN *)
        ('PLPhaseValid', '?'),     # (* BOOLEAN *)
        ('LockInMode', 'c'),       # (* BYTE *)
        ('CalMode', 'c'),          # (* BYTE *)
        ('Spares', '28s', None),   # (* remaining *)
    ]

    required_size = 96


class AmplifierState(Struct):
    field_info = [
        ('StateVersion', '8s', cstr),         # (* 8 = SizeStateVersion *)
        ('RealCurrentGain', 'd'),             # (* LONGREAL *)
        ('RealF2Bandwidth', 'd'),             # (* LONGREAL *)
        ('F2Frequency', 'd'),                 # (* LONGREAL *)
        ('RsValue', 'd'),                     # (* LONGREAL *)
        ('RsFraction', 'd'),                  # (* LONGREAL *)
        ('GLeak', 'd'),                       # (* LONGREAL *)
        ('CFastAmp1', 'd'),                   # (* LONGREAL *)
        ('CFastAmp2', 'd'),                   # (* LONGREAL *)
        ('CFastTau', 'd'),                    # (* LONGREAL *)
        ('CSlow', 'd'),                       # (* LONGREAL *)
        ('GSeries', 'd'),                     # (* LONGREAL *)
        ('StimDacScale', 'd'),                # (* LONGREAL *)
        ('CCStimScale', 'd'),                 # (* LONGREAL *)
        ('VHold', 'd'),                       # (* LONGREAL *)
        ('LastVHold', 'd'),                   # (* LONGREAL *)
        ('VpOffset', 'd'),                    # (* LONGREAL *)
        ('VLiquidJunction', 'd'),             # (* LONGREAL *)
        ('CCIHold', 'd'),                     # (* LONGREAL *)
        ('CSlowStimVolts', 'd'),              # (* LONGREAL *)
        ('CCTrackVHold', 'd'),                # (* LONGREAL *)
        ('TimeoutLength', 'd'),               # (* LONGREAL *)
        ('SearchDelay', 'd'),                 # (* LONGREAL *)
        ('MConductance', 'd'),                # (* LONGREAL *)
        ('MCapacitance', 'd'),                # (* LONGREAL *)
        ('SerialNumber', '8s', cstr),         # (* 8 = SizeSerialNumber *)
        ('E9Boards', 'h'),                    # (* INT16 *)
        ('CSlowCycles', 'h'),                 # (* INT16 *)
        ('IMonAdc', 'h'),                     # (* INT16 *)
        ('VMonAdc', 'h'),                     # (* INT16 *)
        ('MuxAdc', 'h'),                      # (* INT16 *)
        ('TstDac', 'h'),                      # (* INT16 *)
        ('StimDac', 'h'),                     # (* INT16 *)
        ('StimDacOffset', 'h'),               # (* INT16 *)
        ('MaxDigitalBit', 'h'),               # (* INT16 *)
        ('HasCFastHigh', 'c'),                # (* BYTE *)
        ('CFastHigh', 'c'),                   # (* BYTE *)
        ('HasBathSense', 'c'),                # (* BYTE *)
        ('BathSense', 'c'),                   # (* BYTE *)
        ('HasF2Bypass', 'c'),                 # (* BYTE *)
        ('F2Mode', 'c'),                      # (* BYTE *)
        ('AmplKind', 'c'),                    # (* BYTE *)
        ('IsEpc9N', 'c'),                     # (* BYTE *)
        ('ADBoard', 'c'),                     # (* BYTE *)
        ('BoardVersion', 'c'),                # (* BYTE *)
        ('ActiveE9Board', 'c'),               # (* BYTE *)
        ('Mode', 'c'),                        # (* BYTE *)
        ('Range', 'c'),                       # (* BYTE *)
        ('F2Response', 'c'),                  # (* BYTE *)
        ('RsOn', 'c'),                        # (* BYTE *)
        ('CSlowRange', 'c'),                  # (* BYTE *)
        ('CCRange', 'c'),                     # (* BYTE *)
        ('CCGain', 'c'),                      # (* BYTE *)
        ('CSlowToTstDac', 'c'),               # (* BYTE *)
        ('StimPath', 'c'),                    # (* BYTE *)
        ('CCTrackTau', 'c'),                  # (* BYTE *)
        ('WasClipping', 'c'),                 # (* BYTE *)
        ('RepetitiveCSlow', 'c'),             # (* BYTE *)
        ('LastCSlowRange', 'c'),              # (* BYTE *)
        ('Old2', 'c', None),                  # (* BYTE *)
        ('CanCCFast', 'c'),                   # (* BYTE *)
        ('CanLowCCRange', 'c'),               # (* BYTE *)
        ('CanHighCCRange', 'c'),              # (* BYTE *)
        ('CanCCTracking', 'c'),               # (* BYTE *)
        ('HasVmonPath', 'c'),                 # (* BYTE *)
        ('HasNewCCMode', 'c'),                # (* BYTE *)
        ('Selector', 'c'),                    # (* CHAR *)
        ('HoldInverted', 'c'),                # (* BYTE *)
        ('AutoCFast', 'c'),                   # (* BYTE *)
        ('AutoCSlow', 'c'),                   # (* CHAR *)
        ('HasVmonX100', 'c'),                 # (* BYTE *)
        ('TestDacOn', 'c'),                   # (* BYTE *)
        ('QMuxAdcOn', 'c'),                   # (* BYTE *)
        ('Imon1Bandwidth', 'd'),              # (* LONGREAL *)
        ('StimScale', 'd'),                   # (* LONGREAL *)
        ('Gain', 'c'),                        # (* BYTE *)
        ('Filter1', 'c'),                     # (* BYTE *)
        ('StimFilterOn', 'c'),                # (* BYTE *)
        ('RsSlow', 'c'),                      # (* BYTE *)
        ('Old1', 'c'),                        # (* BYTE *)
        ('CCCFastOn', 'c'),                   # (* BYTE *)
        ('CCFastSpeed', 'c'),                 # (* BYTE *)
        ('F2Source', 'c'),                    # (* BYTE *)
        ('TestRange', 'c'),                   # (* BYTE *)
        ('TestDacPath', 'c'),                 # (* BYTE *)
        ('MuxChannel', 'c'),                  # (* BYTE *)
        ('MuxGain64', 'c'),                   # (* BYTE *)
        ('VmonX100', 'c'),                    # (* BYTE *)
        ('IsQuadro', 'c'),                    # (* BYTE *)
        ('F1Mode', 'c'),                      # (* BYTE *)
        ('Old3', 'c', None),                  # (* BYTE *)
        ('StimFilterHz', 'd'),                # (* LONGREAL *)
        ('RsTau', 'd'),                       # (* LONGREAL *)
        ('DacToAdcDelay', 'd'),               # (* LONGREAL *)
        ('InputFilterTau', 'd'),              # (* LONGREAL *)
        ('OutputFilterTau', 'd'),             # (* LONGREAL *)
        ('vMonFactor', 'd', None),            # (* LONGREAL *)
        ('CalibDate', '16s', cstr),           # (* 16 = SizeCalibDate *)
        ('VmonOffset', 'd'),                  # (* LONGREAL *)
        ('EEPROMKind', 'c'),                  # (* BYTE *)
        ('VrefX2', 'c'),                      # (* BYTE *)
        ('HasVrefX2AndF2Vmon', 'c'),          # (* BYTE *)
        ('sSpare1', 'c'),                     # (* BYTE *)
        ('sSpare2', 'c'),                     # (* BYTE *)
        ('sSpare3', 'c'),                     # (* BYTE *)
        ('sSpare4', 'c'),                     # (* BYTE *)
        ('sSpare5', 'c'),                     # (* BYTE *)
        ('CCStimDacScale', 'd'),              # (* LONGREAL *)
        ('VmonFiltBandwidth', 'd'),           # (* LONGREAL *)
        ('VmonFiltFrequency', 'd'),           # (* LONGREAL *)
    ]

    required_size = 400


class GroupRecord(TreeNode):
    field_info = [
        ('Mark', 'i'),              # (* INT32 *)
        ('Label', '32s', cstr),     # (* String32Size *)
        ('Text', '80s', cstr),      # (* String80Size *)
        ('ExperimentNumber', 'i'),  # (* INT32 *)
        ('GroupCount', 'i'),        # (* INT32 *)
        ('CRC', 'i'),               # (* CARD32 *)
        ('MatrixWidth', 'd'),       # (* LONGREAL *)
        ('MatrixHeight', 'd'),      # (* LONGREAL *)
    ]

    required_size = 144


class SeriesRecord(TreeNode):
    field_info = [
        ('Mark', 'i'),                                       # (* INT32 *)
        ('Label', '32s', cstr),                              # (* String32Type *)
        ('Comment', '80s', cstr),                            # (* String80Type *)
        ('SeriesCount', 'i'),                                # (* INT32 *)
        ('NumberSweeps', 'i'),                               # (* INT32 *)
        ('AmplStateOffset', 'i'),                            # (* INT32 *)
        ('AmplStateSeries', 'i'),                            # (* INT32 *)
        ('MethodTag', 'i'),                                  # (* INT32 *)
        ('Time', 'd'),                                       # (* LONGREAL *)
        ('PageWidth', 'd'),                                  # (* LONGREAL *)
        ('SwUserParamDescr', UserParamDescrType.array(4)),   # (* ARRAY[0..3] OF UserParamDescrType = 4*40 *)
        ('MethodName', '32s', None),                         # (* String32Type *)
        ('UserParams', '4d'),                                # (* ARRAY[0..3] OF LONGREAL *)
        ('LockInParams', LockInParams),                      # (* SeLockInSize = 96, see "Pulsed.de" *)
        ('AmplifierState', AmplifierState),                  # (* AmplifierStateSize = 400 *)
        ('Username', '80s', cstr),                           # (* String80Type *)
        ('SeUserParamDescr1', UserParamDescrType.array(4)),  # (* ARRAY[0..3] OF UserParamDescrType = 4*40 *)
        ('Filler1', 'i', None),                              # (* INT32 *)
        ('CRC', 'i'),                                        # (* CARD32 *)
        ('SeUserParams2', '4d'),                             # (* ARRAY[0..3] OF LONGREAL *)
        ('SeUserParamDescr2', UserParamDescrType.array(4)),  # (* ARRAY[0..3] OF UserParamDescrType = 4*40 *)
        ('ScanParams', '96s', cstr),                         # (* ScanParamsSize = 96 *)
    ]

    required_size = 1408


class SweepRecord(TreeNode):
    field_info = [
        ('Mark', 'i'),               # (* INT32 *)
        ('Label', '32s', cstr),      # (* String32Type *)
        ('AuxDataFileOffset', 'i'),  # (* INT32 *)
        ('StimCount', 'i'),          # (* INT32 *)
        ('SweepCount', 'i'),         # (* INT32 *)
        ('Time', 'd'),               # (* LONGREAL *)
        ('Timer', 'd'),              # (* LONGREAL *)
        ('SwUserParams', '4d'),      # (* ARRAY[0..3] OF LONGREAL *)
        ('Temperature', 'd'),        # (* LONGREAL *)
        ('OldIntSol', 'i'),          # (* INT32 *)
        ('OldExtSol', 'i'),          # (* INT32 *)
        ('DigitalIn', 'h'),          # (* SET16 *)
        ('SweepKind', 'h'),          # (* SET16 *)
        ('DigitalOut', 'h'),         # (* SET16 *)
        ('Filler1', 'h', None),      # (* INT16 *)
        ('Markers', '4d'),           # (* ARRAY[0..3] OF LONGREAL, see SwMarkersNo *)
        ('Filler2', 'i', None),      # (* INT32 *)                                    ),
        ('CRC', 'i'),                # (* CARD32 *)
        ('SwHolding', '16d')         # (* ARRAY[0..15] OF LONGREAL, see SwHoldingNo *)
    ]

    required_size = 288


class TraceRecord(TreeNode):
    field_info = [
        ('Mark', 'i'),                  # (* INT32 *)
        ('Label', '32s', cstr),         # (* String32Type *)
        ('TraceCount', 'i'),            # (* INT32 *)
        ('Data', 'i'),                  # (* INT32 *)
        ('DataPoints', 'i'),            # (* INT32 *)
        ('InternalSolution', 'i'),      # (* INT32 *)
        ('AverageCount', 'i'),          # (* INT32 *)
        ('LeakCount', 'i'),             # (* INT32 *)
        ('LeakTraces', 'i'),            # (* INT32 *)
        ('DataKind', 'h'),              # (* SET16 *)
        ('UseXStart', 'c'),             # (* BOOLEAN *)
        ('TcKind', 'c'),                # (* BYTE *)
        ('RecordingMode', 'c'),         # (* BYTE *)
        ('AmplIndex', 'c'),             # (* BYTE *)
        ('DataFormat', 'c'),            # (* CHAR *)
        ('DataAbscissa', 'c'),          # (* BYTE *)
        ('DataScaler', 'd'),            # (* LONGREAL *)
        ('TimeOffset', 'd'),            # (* LONGREAL *)
        ('ZeroData', 'd'),              # (* LONGREAL *)
        ('YUnit', '8s', cstr),          # (* String8Type *)
        ('XInterval', 'd'),             # (* LONGREAL *)
        ('XStart', 'd'),                # (* LONGREAL *)
        ('XUnit', '8s', cstr),          # (* String8Type *)
        ('YRange', 'd'),                # (* LONGREAL *)
        ('YOffset', 'd'),               # (* LONGREAL *)
        ('Bandwidth', 'd'),             # (* LONGREAL *)
        ('PipetteResistance', 'd'),     # (* LONGREAL *)
        ('CellPotential', 'd'),         # (* LONGREAL *)
        ('SealResistance', 'd'),        # (* LONGREAL *)
        ('CSlow', 'd'),                 # (* LONGREAL *)
        ('GSeries', 'd'),               # (* LONGREAL *)
        ('RsValue', 'd'),               # (* LONGREAL *)
        ('GLeak', 'd'),                 # (* LONGREAL *)
        ('MConductance', 'd'),          # (* LONGREAL *)
        ('LinkDAChannel', 'i'),         # (* INT32 *)
        ('ValidYrange', 'c'),           # (* BOOLEAN *)
        ('AdcMode', 'c'),               # (* CHAR *)
        ('AdcChannel', 'h'),            # (* INT16 *)
        ('Ymin', 'd'),                  # (* LONGREAL *)
        ('Ymax', 'd'),                  # (* LONGREAL *)
        ('SourceChannel', 'i'),         # (* INT32 *)
        ('ExternalSolution', 'i'),      # (* INT32 *)
        ('CM', 'd'),                    # (* LONGREAL *)
        ('GM', 'd'),                    # (* LONGREAL *)
        ('Phase', 'd'),                 # (* LONGREAL *)
        ('DataCRC', 'i'),               # (* CARD32 *)
        ('CRC', 'i'),                   # (* CARD32 *)
        ('GS', 'd'),                    # (* LONGREAL *)
        ('SelfChannel', 'i'),           # (* INT32 *)
        ('TrInterleaveSize', 'i'),      # (* INT32 *)
        ('TrInterleaveSkip', 'i'),      # (* INT32 *)
        ('TrImageIndex', 'i'),          # (* INT32 *)
        ('TrTrMarkers', '10d'),         # (* ARRAY[0..9] OF LONGREAL *)
        ('TrSECM_X', 'd'),              # (* LONGREAL *)
        ('TrSECM_Y', 'd'),              # (* LONGREAL *)
        ('TrSECM_Z', 'd'),              # (* LONGREAL *)
        ('TrTrHolding', 'd'),           # (* LONGREAL *)
        ('TrTcEnumerator', 'i'),        # (* INT32 *)
        ('TrXTrace', 'i'),              # (* INT32 *)
        ('TrIntSolValue', 'd'),         # (* LONGREAL *)
        ('TrExtSolValue', 'd'),         # (* LONGREAL *)
        ('TrIntSolName', '32s', cstr),  # (* String32Size *)
        ('TrExtSolName', '32s', cstr),  # (* String32Size *)
        ('TrDataPedestal', 'd'),        # (* LONGREAL *)
    ]

    required_size = 512


class Pulsed(TreeNode):
    field_info = [
        ('Version', 'i'),              # (* INT32 *)
        ('Mark', 'i'),                 # (* INT32 *)
        ('VersionName', '32s', cstr),  # (* String32Type *)
        ('AuxFileName', '80s', cstr),  # (* String80Type *)
        ('RootText', '400s', cstr),    # (* String400Type *)
        ('StartTime', 'd'),            # (* LONGREAL *)
        ('MaxSamples', 'i'),           # (* INT32 *)
        ('CRC', 'i'),                  # (* CARD32 *)
        ('Features', 'h'),             # (* SET16 *)
        ('Filler1', 'h', None),        # (* INT16 *)
        ('Filler2', 'i', None),        # (* INT32 *)
        ('RoTcEnumerator', '32h'),     # (* ARRAY[0..Max_TcKind_M1] OF INT16 *)
        ('RoTcKind', '32s', cstr)      # (* ARRAY[0..Max_TcKind_M1] OF INT8 *)
    ]

    required_size = 640

    rectypes = [
        None,
        GroupRecord,
        SeriesRecord,
        SweepRecord,
        TraceRecord
    ]

    def __init__(self, fh, endianess):
        TreeNode.__init__(self, fh, endianess, self.rectypes, None)


class StimulationRecord(TreeNode):
    field_info = [
        ('Mark', 'i'),                   # (* INT32 *)
        ('EntryName', '32s', cstr),      # (* String32Type *)
        ('FileName', '32s', cstr),       # (* String32Type *)
        ('AnalName', '32s', cstr),       # (* String32Type *)
        ('DataStartSegment', 'i'),       # (* INT32 *)
        ('DataStartTime', 'd'),          # (* LONGREAL *)
        ('SampleInterval', 'd'),         # (* LONGREAL *)
        ('SweepInterval', 'd'),          # (* LONGREAL *)
        ('LeakDelay', 'd'),              # (* LONGREAL *)
        ('FilterFactor', 'd'),           # (* LONGREAL *)
        ('NumberSweeps', 'i'),           # (* INT32 *)
        ('NumberLeaks', 'i'),            # (* INT32 *)
        ('NumberAverages', 'i'),         # (* INT32 *)
        ('ActualAdcChannels', 'i'),      # (* INT32 *)
        ('ActualDacChannels', 'i'),      # (* INT32 *)
        ('ExtTrigger', 'c'),             # (* BYTE *)
                                         #  ExtTriggerType = ( TrigNone,
                                         #   TrigSeries,
                                         #   TrigSweep,
                                         #   TrigSweepNoLeak );
        ('NoStartWait', '?'),            # (* BOOLEAN *)
        ('UseScanRates', '?'),           # (* BOOLEAN *)
        ('NoContAq', '?'),               # (* BOOLEAN *)
        ('HasLockIn', '?'),              # (* BOOLEAN *)
        ('OldStartMacKind', 'c'),        # (* CHAR *)
        ('OldEndMacKind', '?'),          # (* BOOLEAN *)
        ('AutoRange', 'c'),              # (* BYTE *)
                                         #  AutoRangingType = ( AutoRangingOff,
                                         #    AutoRangingPeak,
                                         #    AutoRangingMean,
                                         #    AutoRangingRelSeg );
        ('BreakNext', '?'),              # (* BOOLEAN *)
        ('IsExpanded', '?'),             # (* BOOLEAN *)
        ('LeakCompMode', '?'),           # (* BOOLEAN *)
        ('HasChirp', '?'),               # (* BOOLEAN *)
        ('OldStartMacro', '32s', cstr),  # (* String32Type *)
        ('OldEndMacro', '32s', cstr),    # (* String32Type *)
        ('IsGapFree', '?'),              # (* BOOLEAN *)
        ('HandledExternally', '?'),      # (* BOOLEAN *)
        ('Filler1', '?', None),          # (* BOOLEAN *)
        ('Filler2', '?', None),          # (* BOOLEAN *)
        ('CRC', 'i')                     # (* CARD32 *)
    ]

    required_size = 248


class ChannelRecordStimulus(TreeNode):
    field_info = [
        ('Mark', 'i'),                # (* INT32 *)
        ('LinkedChannel', 'i'),       # (* INT32 *)
        ('CompressionFactor', 'i'),   # (* INT32 *)
        ('YUnit', '8s', cstr),        # (* String8Type *)
        ('AdcChannel', 'H'),          # (* INT16 *)
        ('AdcMode', 'c'),             # (* BYTE *)
                                      # AdcType = ( AdcOff,
                                      #             Analog,
                                      #             Digitals,
                                      #             Digital,
                                      #             AdcVirtual );
        ('DoWrite', '?'),             # (* BOOLEAN *)
        ('LeakStore', 'c'),           # (* BYTE *)
                                      # LeakStoreType = ( LNone,
                                      #                   LStoreAvg,
                                      #                   LStoreEach,
                                      #                   LNoStore );
        ('AmplMode', 'c'),            # (* BYTE *)
                                      # AmplModeType         = ( AnyAmplMode,
                                      #                          VCAmplMode,
                                      #                          CCAmplMode,
                                      #                          IDensityMode );
        ('OwnSegTime', '?'),          # (* BOOLEAN *)
        ('SetLastSegVmemb', '?'),     # (* BOOLEAN *)
        ('DacChannel', 'H'),          # (* INT16 *)
        ('DacMode', 'c'),             # (* BYTE *)
        # todo missing docu
        ('HasLockInSquare', 'c'),     # (* BYTE *)
        # todo missing docu
        ('RelevantXSegment', 'i'),    # (* INT32 *)
        ('RelevantYSegment', 'i'),    # (* INT32 *)
        ('DacUnit', '8s', cstr),      # (* String8Type *)
        ('Holding', 'd'),             # (* LONGREAL *)
        ('LeakHolding', 'd'),         # (* LONGREAL *)
        ('LeakSize', 'd'),            # (* LONGREAL *)
        ('LeakHoldMode', 'c'),        # (* BYTE *)
                                      # LeakHoldType = ( Labs,
                                      #                  Lrel,
                                      #                  LabsLH,
                                      #                  LrelLH );
        ('LeakAlternate', '?'),       # (* BOOLEAN *)
        ('AltLeakAveraging', '?'),    # (* BOOLEAN *)
        ('LeakPulseOn', '?'),         # (* BOOLEAN *)
        ('StimToDacID', 'H'),         # (* SET16 *)
                                      # StimToDacID :
                                      #   Specifies how to convert the Segment
                                      #   "Voltage" to the actual voltage sent to the DAC
                                      #   -> meaning of bits:
                                      #      bit 0 (UseStimScale)    -> use StimScale
                                      #      bit 1 (UseRelative)     -> relative to Vmemb
                                      #      bit 2 (UseFileTemplate) -> use file template
                                      #      bit 3 (UseForLockIn)    -> use for LockIn computation
                                      #      bit 4 (UseForWavelength)
                                      #      bit 5 (UseScaling)
                                      #      bit 6 (UseForChirp)
                                      #      bit 7 (UseForImaging)
                                      #      bit 14 (UseReserved)
                                      #      bit 15 (UseReserved)
        ('CompressionMode', 'H'),     # (* SET16 *)
                                      # CompressionMode : Specifies how to the data
                                      #    -> meaning of bits:
                                      #       bit 0 (CompReal)   -> high = store as real
                                      #                             low  = store as int16
                                      #       bit 1 (CompMean)   -> high = use mean
                                      #                             low  = use single sample
                                      #       bit 2 (CompFilter) -> high = use digital filter
        ('CompressionSkip', 'i'),     # (* INT32 *)
        ('DacBit', 'H'),              # (* INT16 *)
        ('HasLockInSine', '?'),       # (* BOOLEAN *)
        ('BreakMode', 'c'),           # (* BYTE *)
                                      # BreakType = ( NoBreak,
                                      #               BreakPos,
                                      #               BreakNeg );
        ('ZeroSeg', 'i'),             # (* INT32 *)
        ('StimSweep', 'i'),           # (* INT32 *)
        ('Sine_Cycle', 'd'),          # (* LONGREAL *)
        ('Sine_Amplitude', 'd'),      # (* LONGREAL *)
        ('LockIn_VReversal', 'd'),    # (* LONGREAL *)
        ('Chirp_StartFreq', 'd'),     # (* LONGREAL *)
        ('Chirp_EndFreq', 'd'),       # (* LONGREAL *)
        ('Chirp_MinPoints', 'd'),     # (* LONGREAL *)
        ('Square_NegAmpl', 'd'),      # (* LONGREAL *)
        ('Square_DurFactor', 'd'),    # (* LONGREAL *)
        ('LockIn_Skip', 'i'),         # (* INT32 *)
        ('Photo_MaxCycles', 'i'),     # (* INT32 *)
        ('Photo_SegmentNo', 'i'),     # (* INT32 *)
        ('LockIn_AvgCycles', 'i'),    # (* INT32 *)
        ('Imaging_RoiNo', 'i'),       # (* INT32 *)
        ('Chirp_Skip', 'i'),          # (* INT32 *)
        ('Chirp_Amplitude', 'd'),     # (* LONGREAL *)
        # todo missing docu
        ('Photo_Adapt', 'c'),         # (* BYTE *)
        # todo missing docu
        ('Sine_Kind', 'c'),           # (* BYTE *)
        # todo missing docu
        ('Chirp_PreChirp', 'c'),      # (* BYTE *)
        # todo missing docu
        ('Sine_Source', 'c'),         # (* BYTE *)
        # todo missing docu
        ('Square_NegSource', 'c'),    # (* BYTE *)
        # todo missing docu
        ('Square_PosSource', 'c'),    # (* BYTE *)
        # todo missing docu
        ('Chirp_Kind', 'c'),          # (* BYTE *)
        # todo missing docu
        ('Chirp_Source', 'c'),        # (* BYTE *)
        ('DacOffset', 'd'),           # (* LONGREAL *)
        ('AdcOffset', 'd'),           # (* LONGREAL *)
        # todo missing docu
        ('TraceMathFormat', 'c'),     # (* BYTE *)
        ('HasChirp', '?'),            # (* BOOLEAN *)
        # todo missing docu
        ('Square_Kind', 'c'),         # (* BYTE *)
        ('Filler1', '5s', cstr),      # (* ARRAY[0..5] OF CHAR *)
        ('Square_BaseIncr', 'd'),     # (* LONGREAL *)
        ('Square_Cycle', 'd'),        # (* LONGREAL *)
        ('Square_PosAmpl', 'd'),      # (* LONGREAL *)
        ('CompressionOffset', 'i'),   # (* INT32 *)
        ('PhotoMode', 'i'),           # (* INT32 *)
        ('BreakLevel', 'd'),          # (* LONGREAL *)
        ('TraceMath', '128s', cstr),  # (* String128Type *)
        ('Filler2', 'i', None),       # (* INT32 *)
        ('CRC', 'i'),                 # (* CARD32 *)
        ('UnknownFiller', '?'),       # Undocumented
    ]

    # todo documented size is incorrect
    required_size = 401


class StimSegmentRecord(TreeNode):
    field_info = [
        ('Mark', 'i'),             # (* INT32 *)
        ('Class', 'c'),            # (* BYTE *)
                                   #  SegmentClass = ( SegmentConstant,
                                   #                   SegmentRamp,
                                   #                   SegmentContinuous,
                                   #                   SegmentConstSine,
                                   #                   SegmentSquarewave,
                                   #                   SegmentChirpwave );
        ('StoreKind', 'c'),        # (* BYTE *)
                                   #  SegStoreType = ( SegNoStore,
                                   #                   SegStore,
                                   #                   SegStoreStart,
                                   #                   SegStoreEnd );
        ('VoltageIncMode', 'c'),   # (* BYTE *)
        # todo missing docu
        ('DurationIncMode', 'c'),  # (* BYTE *)
        # todo missing docu
        ('Voltage', 'd'),          # (* LONGREAL *)
        ('VoltageSource', 'i'),    # (* INT32 *)
        ('DeltaVFactor', 'd'),     # (* LONGREAL *)
        ('DeltaVIncrement', 'd'),  # (* LONGREAL *)
        ('Duration', 'd'),         # (* LONGREAL *)
        ('DurationSource', 'i'),   # (* INT32 *)
        ('DeltaTFactor', 'd'),     # (* LONGREAL *)
        ('DeltaTIncrement', 'd'),  # (* LONGREAL *)
        ('Filler1', 'i', None),    # (* INT32 *)
        ('CRC', 'i'),              # (* CARD32 *)
        ('ScanRate', 'd'),         # (* LONGREAL *)
    ]

    required_size = 80


class StimulusTemplate(TreeNode):
    field_info = [
        ('Version', 'i'),              # (* INT32 *)
        ('Mark', 'i'),                 # (* INT32 *)
        ('VersionName', '32s', cstr),  # (* String32Type *)
        ('MaxSamples', 'i'),           # (* INT32 *)
        ('roFiller1', 'i', None),      # (* INT32 *)
        ('Params', '10d'),             # (* ARRAY[0..9] OF LONGREAL *), (* StimParams     = 10  *)
        ('ParamText', '320s', cstr),   # (* ARRAY[0..9],[0..31]OF CHAR *), (* StimParamChars = 320 *)
        ('Reserved', '128s', None),    # (* String128Type *)
        ('roFiller2', 'i', None),      # (* INT32 *)
        ('CRC', 'i')                   # (* CARD32 *)
    ]

    required_size = 584

    rectypes = [
        None,
        StimulationRecord,
        ChannelRecordStimulus,
        StimSegmentRecord,
    ]

    def __init__(self, fh, endianess):
        TreeNode.__init__(self, fh, endianess, self.rectypes, None)


class BundleItem(Struct):
    field_info = [
        ('Start', 'i'),             # (* INT32 *)
        ('Length', 'i'),            # (* INT32 *)
        ('Extension', '8s', cstr),  # (* ARRAY[0..7] OF CHAR *)
    ]

    required_size = 16


class BundleHeader(Struct):
    field_info = [
        ('Signature', '8s', cstr),              # (* ARRAY[0..7] OF CHAR *)
        ('Version', '32s', cstr),               # (* ARRAY[0..31] OF CHAR *)
        ('Time', 'd'),                          # (* LONGREAL *)
        ('Items', 'i'),                         # (* INT32 *)
        ('IsLittleEndian', '?'),                # (* BOOLEAN *)
        ('Reserved', '11s', None),              # (* ARRAY[0..10] OF CHAR *)
        ('BundleItems', BundleItem.array(12)),  # (* ARRAY[0..11] OF BundleItem *)
    ]

    required_size = 256
