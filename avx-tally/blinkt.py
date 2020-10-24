from __future__ import absolute_import
from avx.devices import Device

from blinkt import clear, set_all, show


class BlinktTally(Device):

    def __init__(self, deviceID, **kwargs):
        super(BlinktTally, self).__init__(deviceID, **kwargs)
        self.brightness = kwargs.get('brightness', 0.1)

    def tallyStandby(self):
        set_all(0, 255, 0, self.brightness)
        show()

    def tallyLive(self):
        set_all(255, 0, 0, self.brightness)
        show()

    def tallyOff(self):
        clear()
