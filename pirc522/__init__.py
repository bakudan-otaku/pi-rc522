__version__ = "2.2.1"

try:
    from .rfid import RFID
    from .util import RFIDUtil
    from .ndef import NdefMessage, NdefRecordFlags, NdefRecord
    from .ndef import RTD, RTD_Text, RTD_URI
    from .mifare1k import MIFARE1k
except RuntimeError:
    print("Must be used on Raspberry Pi or Beaglebone")


