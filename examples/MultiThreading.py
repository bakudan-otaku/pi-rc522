#!/usr/bin/env python

import threading
import sys, os
import time

from pirc522 import RFIDLocked

"""
A "simple" example for multithreaded NFC Reading.
The SleepyThread is evil and will break after 10 secounds, that is to show how the shutdown works
Simply change the 10 sec if needed
"""


class SleepyThread(threading.Thread):
    def __init__(self):
        super(SleepyThread, self).__init__()
        self.daemon = True

    def __str__(self):
        return self.__class__.__name__

    def run(self):
        i = 0
        while True:
            time.sleep(1)
            if i > 10:
                # 10 sec of sleeping is enoght
                # This will end the Program because of healthcheck!
                break
            i += 1

class NfcReading(threading.Thread):
    def __init__(self):
        super(NfcReading, self).__init__()
        self.rdr = RFIDLocked()
        self.util = self.rdr.util()

    def stop(self):
        self.rdr.stop()

    def run(self):
        running = True
        while running:
            running = self.rdr.wait_for_tag()
            if not running:
                shutdown = False
                # Make shure the shutdown flag is set:
                with self.rdr.shutdown_lock:
                    shutdown = self.rdr.shutdown
                if shutdown:
                    break
                else:
                    # Don't know what happend, but try agian.
                    running = True
                    continue
            #
            (error, data) = self.rdr.request()
            if error:
                continue
            (error, uid) = self.rdr.anticoll()
            if error:
                continue
            # Set tag as used in util. This will call RFID.select_tag(uid)
            self.util.set_tag(uid)
            # Save authorization info (key B) to util. It doesn't call RFID.card_auth(), that's called when needed
            self.util.auth(self.rdr.auth_b, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
            
            error = self.util.dump_hex()
            if error:
                self.util.deauth()
                continue

            # We must stop crypto
            self.util.deauth()
            # that lib is too fast, slow down for the humans
            time.sleep(0.5)

        # Now we can cleanup:
        self.rdr.cleanup()

class MultiThreading:

    def __init__(self):
        self.threads = []

        self.threads.append(SleepyThread())
        self.threads.append(NfcReading())

    def main(self):
        for thread in self.threads:
            thread.start()

        running = True
        # Wait till something happens
        while running:
            time.sleep(1)
            for thread in self.threads:
                if not thread.isAlive():
                    print("Error Thread " +  str(thread) + " died")
                    running = False
                    break

        # Stop threads if they support it.
        self.shutdown()

    def shutdown(self):
        for thread in self.threads:
            if thread.isAlive() and hasattr(thread, 'stop') and callable( thread.stop ):
                thread.stop()
                thread.join()

if __name__ == "__main__":
    main = MultiThreading()
    try:
        main.main()
    except KeyboardInterrupt:
        try:
            main.shutdown()
            sys.exit(0)
        except SystemExit:
            main.shutdown()
            os._exit(0)
    
    
