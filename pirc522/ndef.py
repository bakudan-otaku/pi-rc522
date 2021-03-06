# Havyly influenced by pyndef: https://github.com/kichik/pyndef

class NdefMessage:

    def __init__(self, data=None):
        self.records = []
        # Creates the records:
        d = bytes(data)
        while data != None:
            record = NdefRecord(d)
            self.records.append(record)
            if record.flags.message_end:
                break

            d = d[record.length:]

    def get_record(self, pos):
        return self.records[pos]

    def len(self):
        return len(self.records)

class NdefRecordFlags:
    MB = 0x80
    ME = 0x40
    CHUNKED = 0x20
    SHORT = 0x10
    ID = 0x08
    TNF_MASK = 0x07

    
    def __init__(self,flags_raw):
        self.message_begin = bool(flags_raw & NdefRecordFlags.MB)
        self.message_end = bool(flags_raw & NdefRecordFlags.ME)
        self.chunked = bool(flags_raw & NdefRecordFlags.CHUNKED)
        self.short_record = bool(flags_raw & NdefRecordFlags.SHORT)
        self.id_pressend = bool(flags_raw & NdefRecordFlags.ID)
        self.tnf = int(flags_raw & NdefRecordFlags.TNF_MASK)

    def __str__(self):
        s = "MB: " + str(self.message_begin) + "; "
        s += "ME: " + str(self.message_end) + "; "
        s += "CF: " + str(self.chunked) + "; "
        s += "SR: " + str(self.short_record) + "; "
        s += "IL: " + str(self.id_pressend) + "; "
        s += "TNF: " + str(self.tnf) + ";"
        return s
        
class NdefRecord:

    def __init__(self, data):
        self.payload_length = 0
        self.payload_id_length = 0
        self.payload_type = ''
        self.payload_id = ''
        self.payload = None
        self.length = 0 # overall length, for simplicity, not part of the spec
        # Decode Header
        # copy payload
        self.flags = NdefRecordFlags(data[0])
        self.type_length = data[1]
        self.length = 2
        if self.flags.short_record:
            self.payload_length = data[2]
            self.length += 1
        else:
            self.payload_length = int.from_bytes(data[2:6], byteorder="big", signed=False)
            self.length = self.length + 4
        self.payload_id_length = 0
        if self.flags.id_pressend:
            self.payload_id_length = data[self.length]
            self.length += 1
        s = self.length
        e = s + self.type_length
        self.payload_type = data[s:e].decode(encoding="ascii")
        self.length += self.type_length
        s = e
        e = s + self.payload_id_length
        self.payload_id = data[s:e].decode(encoding="ascii")
        self.length += self.payload_id_length
        s = e
        e = s + self.payload_length
        if self.payload_type == 'T' and self.flags.tnf == 1:
            self.payload = RTD_Text(data[s:e], self.payload_length)
        elif self.payload_type == 'U' and self.flags.tnf == 1:
            self.payload = RTD_URI(data[s:e], self.payload_length)
        else:
            # payload unkown:
            self.payload = RTD(data[s:e], self.payload_length)
        
        self.length += self.payload_length

    def __str__(self):
        s = str(self.flags) + "\n"
        s = s + "type length: " + str(self.type_length) + "; "
        s = s + "payload length: " + str(self.payload_length) + "; "
        s = s + "payload id length: " + str(self.payload_id_length) + "; "
        s = s + "payload type: " + self.payload_type + "; "
        s = s + "payload id: " + self.payload_id + "; "
        s = s + "length: " + str(self.length) + ";\n"
        s = s + "payload:\n---\n" + str(self.payload) + "\n---"
        
        return s

    
class RTD:
    rtd_type = None

    def __init__(self, contend, length):
        self.contend = contend
        self.length = length

    def __str__(self):
        return str(self.length) + ": " + str(self.contend)

    def get_contend(self):
        return self.contend

class RTD_Text(RTD):
    rtd_type = "Text"

    UTF = 0x80
    LANG_MASK = 0x3F

    def __init__(self, contend, length):
        self.encoding = ""
        
        self.length = length
        self.lang_length = int(contend[0] & RTD_Text.LANG_MASK)
        self.lang = contend[1:1 + self.lang_length].decode(encoding="ascii")
        if contend[0] & RTD_Text.UTF:
            self.encoding = "UTF-16"
        else:
            self.encoding = "UTF-8"
        self.contend = contend[1 + self.lang_length:length].decode(encoding=self.encoding)

    def __str__(self):
        s = str(self.length) + ": encoding: '" + self.encoding
        s += "', lang: '" + self.lang
        s += "', contend: '" + self.contend + "'"
        return s

    def get_contend(self):
        return self.contend
    

class RTD_URI(RTD):
    rtd_type = "URI"
    PREFIX_CODES = [ "",
                     "http://www.",
                     "https://www.",
                     "http://",
                     "https://",
                     "tel:",
                     "mailto:",
                     "ftp://anonymous:anonymous@",
                     "ftp://ftp.",
                     "ftps://",
                     "sftp://",
                     "smb://",
                     "nfs://",
                     "ftp://",
                     "dav://",
                     "news:",
                     "telnet://",
                     "imap:",
                     "rtsp://",
                     "urn:",
                     "pop:",
                     "sip:",
                     "sips:",
                     "tftp:",
                     "btspp://",
                     "btl2cap://",
                     "btgoep://",
                     "tcpobex://",
                     "irdaobex://",
                     "file://",
                     "urn:epc:id:",
                     "urn:epc:tag:",
                     "urn:epc:pat:",
                     "urn:epc:raw:",
                     "urn:epc:",
                     "urn:nfc:" ]

    def __init__(self, contend, length):
        
        self.length = length
        self.uri_prefix = int(contend[0])
        self.contend = contend[1:length].decode(encoding="UTF-8")

    def get_contend(self):
        return RTD_URI.PREFIX_CODES[self.uri_prefix] + self.contend

    def __str__(self):
        return str(self.length) + ": '" + self.get_contend() + "'"

