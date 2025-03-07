# *************************************
# author: leonard.yu@teledyne.com
# *************************************

from enum import IntEnum

class Cursor(IntEnum):
    Precursor = 0
    Postcursor = 1
    Amplitude = 2

class ConfigStatus(IntEnum):
    ConfigUndefined = 0x00
    """No status information available (initial register value)
    """
    ConfigSuccess = 0x01
    """Positive Result Status: The last accepted configuration command has been completed successfully
    """
    ConfigRejected = 0x02
    """Configuration rejected: unspecific validation failure
    """
    ConfigRejectedInvalidAppSel = 0x03
    """Configuration rejected: invalid AppSel code
    """
    ConfigRejectedInvalidDataPath = 0x04
    """Configuration rejected: invalid set of lanes for AppSel
    """ 
    ConfigRejectedInvalidSI = 0x05
    """Configuration rejected: invalid SI control settings
    """
    ConfigRejectedLanesInUse = 0x06
    """Configuration rejected: some lanes not in DPDeactivated
    """
    ConfigRejectedPartialDataPath = 0x07
    """Configuration rejected: lanes are only subset of DataPath
    """
    ConfigInProgress = 0x0C
    """Configuration in progress
    """
