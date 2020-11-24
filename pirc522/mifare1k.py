
class MIFARE1k(object):
    SECTORS = 16
    BLOCKSIZE = 4
    BLOCKWITH = 16

    uid = None
    data = []


    def __init__(self, uid, data):
        self.uid = uid
        self.data = data

    def __str__(self):
        """
        Get a nice printout for debugging and dev.
        """
        ret = "Card: "
        for i in range(4):
            if i > 0:
                ret = ret + ":"
            ret = ret + format(self.uid[i], '02x').upper()
        ret = ret + "\n"
        for sector in range(self.SECTORS):
            ret = ret + "------------------------Sector " + str(sector)
            if sector < 10:
                ret = ret + "-"
            ret = ret + "------------------------\n"
            for b in range(self.BLOCKSIZE):
                block = b + self.BLOCKSIZE * sector
                ret = ret + "Block " + str(block)
                if (block) < 10:
                    ret = ret + " "
                for i in range(self.BLOCKWITH):
                    pos = i + block * self.BLOCKWITH
                    he = "0x" + format(self.data[pos], '02x').upper()
                    ret = ret + " " + he
                ret = ret + "  "
                
                for i in range(self.BLOCKWITH):
                    pos = i + block * self.BLOCKWITH
                    a = "."
                    if self.data[pos] > 0:
                        a = chr(self.data[pos])
                    ret = ret + a
                ret = ret + "\n"
        return ret

    def get_data(self):
        """
        Userdata is Sector 1 til 16, and only the first 3 blocks.
        """
        ret = []
        for sector in range(1, self.SECTORS):
            for b in range(self.BLOCKSIZE - 1):
                block = b + self.BLOCKSIZE * sector
                for i in range(self.BLOCKWITH):
                    pos = i + block * self.BLOCKWITH
                    ret.append(self.data[pos])
        return ret
        

    def get_messages(self):
        """
        give back all data blocks inside a TLV Messageblock:
          0x03 0x00-0xFE => 1 byte for message length
          0x03 0xFF 0x0000-0xFFFE => 2 bytes for message length
          0xFE => Terminator
          0x00 => Ignore
          0xFD => Proprietary TLV => Ignore / To Implement
        """
        ret = []
        data = self.get_data()
        buf = []
        T = 0x00 # Store the current tag field
        L = 0x00 # Store the length 1 byte format
        L2 = 0x00 # Store the length 3 bytes format, temp value (MSB)
        Lc = 0  # current length
        for val in data:
            if T == 0x03:
                if L == 0x00:
                    L = val
                    continue
                if L == 0xFF:
                    if L2 == 0x00:
                        L2 = val << 8
                        continue
                    else:
                        L = L2 + val
                        L2 = 0x00
                        continue
                # length is set:
                if Lc < L:
                    buf.append(val)
                    Lc = Lc + 1
                    continue
                if Lc == L:
                    if not val == 0xFE:
                        print("Error: Length and Terminator did not fit!")
                    ret.append(buf)
                    buf = []
                    Lc = 0x00
                    L = 0x00
                    T = val
                    continue
            T = val # should be 0x00 or 0x03, we only care if it is 0x03 for the next val.

        return ret

        
        
        
    
