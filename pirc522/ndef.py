# Havyly influenced by pyndef: https://github.com/kichik/pyndef

FLAGS_MB = 0x80
FLAGS_ME = 0x40
FLAGS_CHUNKED = 0x20
FLAGS_SHORT = 0x10
FLAGS_ID = 0x08
FLAGS_TNF_MASK = 0x07

class NdefMessage:
    records = []

    def __init__(self, data=None):
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
    message_begin = False
    message_end = False
    chunked = False
    short_record = False
    id_pressend = False
    tnf = 0
    
    def __init__(self,flags_raw):
        self.message_begin = bool(flags_raw & FLAGS_MB)
        self.message_end = bool(flags_raw & FLAGS_ME)
        self.chunked = bool(flags_raw & FLAGS_CHUNKED)
        self.short_record = bool(flags_raw & FLAGS_SHORT)
        self.id_pressend = bool(flags_raw & FLAGS_ID)
        self.tnf = int(flags_raw & FLAGS_TNF_MASK)

    def __str__(self):
        s = "MB: " + str(self.message_begin) + "; "
        s = s + "ME: " + str(self.message_end) + "; "
        s = s + "CF: " + str(self.chunked) + "; "
        s = s + "SR: " + str(self.short_record) + "; "
        s = s + "IL: " + str(self.id_pressend) + "; "
        s = s + "TNF: " + str(self.tnf) + ";"
        return s
        
class NdefRecord:
    flags = None
    type_length = 0
    payload_length = 0
    payload_id_length = 0
    payload_type = ''
    payload_id = ''
    payload = None
    length = 0 # overall length, for simplicity, not part of the spec

    def __init__(self, data):
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
        if True:
            # payload unkown:
            self.payload = RTD(data[s:e], self.payload_length)
        # if self.payload_type == 'T' && self.flags.tnf = 1:
        #     self.payload = RTD_Text(data[s:e], self.payload_length)
        
        # if self.payload_type == 'U' && self.flags.tnf = 1:
        #     self.payload = RTD_URI(data[s:e], self.payload_length)
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
    contend = None
    length = 0

    def __init__(self, contend, length):
        self.contend = contend
        self.length = length

    def __str__(self):
        return str(self.length) + ": " + str(self.contend)

class RTD_Text:
    pass

class RTD_URI:
    pass
    
