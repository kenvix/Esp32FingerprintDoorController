import os
import threading
import struct
import logging

import as608 as as608


class FingerMain:
    thread: threading.Thread

    def __init__(self, device=os.getenv("FINGERPRINT_DEVICE"), save_path=os.getenv("FINGERPRINT_SAVE_PATH")):
        self.compare_num = 10
        self.session = as608.connect_serial_session(device)
        self.device = device
        self.log = logging.getLogger("FingerMain for device %s" % self.device)
        self.save_path = save_path
        self.should_stop = False
        self.session._debug = False
        self.on_finger_refused = lambda finger_id, confidence: logging.info("Finger #%d Refused with confidence %f" % (finger_id, confidence))
        self.on_finger_accepted = lambda finger_id, confidence: logging.info("Finger #%d Accepted with confidence %f" % (finger_id, confidence))

    def get_session(self):
        return self.session

    def set_on_finger_accepted(self, callback):
        self.on_finger_accepted = callback

    def set_on_finger_refused(self, callback):
        self.on_finger_refused = callback

    def set_compare_num(self, compare_num):
        self.compare_num = compare_num

    def set_security_level(self, level):
        self.session.set_sysparam(5, int(level))

    def stop_loop(self):
        self.should_stop = True

    def start_loop_async(self):
        self.thread = threading.Thread(target=self.start_loop)
        self.thread.name = "Finger Loop for device %s" % self.device
        self.thread.start()

    def start_loop(self):
        self.should_stop = False

        while self.should_stop is False:
            if as608.search_fingerprint_on_device(self.session, as608) and self.on_finger_accepted is not None:
                self.on_finger_accepted(self.session.finger_id, self.session.confidence)
            elif self.on_finger_refused is not None:
                self.on_finger_refused(self.session.finger_id, self.session.confidence)

    def add_fingerprint(self, add_num=1):
        self.log.info("Add Finger: Num : %d" % add_num)
        as608.enroll_finger_to_device(self.session, as608)
