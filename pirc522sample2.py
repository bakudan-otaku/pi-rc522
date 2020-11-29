from pirc522 import RFID, NdefMessage, MIFARE1k
import signal
import time


rdr = RFID()
util = rdr.util()
# Set util debug to true - it will print what's going on
util.debug = False
readNotDone = True


while readNotDone:
    # Wait for tag
    rdr.wait_for_tag()

    # Request tag
    (error, data) = rdr.request()
    if error:
        continue
    print("\nDetected")

    (error, uid) = rdr.anticoll()
    if error:
        continue
    # Print UID
    print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))

    # Set tag as used in util. This will call RFID.select_tag(uid)
    util.set_tag(uid)
    # Save authorization info (key B) to util. It doesn't call RFID.card_auth(), that's called when needed
    util.auth(rdr.auth_b, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    # Print contents of block 4 in format "S1B0: [contents in decimal]". RFID.card_auth() will be called now

    (error, data) = util.dump_data()
    if error:
        continue
    card = MIFARE1k(uid, data)
    
    print(str(card))
    messages = card.get_messages()
    print(str(messages))
    for m in messages:
        s = ""
        c = 0
        for b in m:
            s = s + " 0x" + format(b, '02x').upper()
        print(str(c) + ":" + s)
        u = "".join(map(chr, m))
        print(u)
        ndefm = NdefMessage(m)
        for r in ndefm.records:
            print(r)
            print(r.payload.get_contend())


    # We must stop crypto
    util.deauth()
    readNotDone = False
            
# Calls GPIO cleanup
rdr.cleanup()
