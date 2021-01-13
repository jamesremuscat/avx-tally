from __future__ import absolute_import
from argparse import ArgumentParser
from avx import PyroUtils
from avx.Client import Client
from avx.controller.Controller import Controller
from avx.devices import Device
from avx_tally import CONTROLLED_TALLY_MESSAGE, DEVICE_DEFAULT_METHODS
from blinkt import clear, set_pixel, set_all, show, NUM_PIXELS

import atexit
import time


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
        show()


class BlinktTallyClient(Client):

    def __init__(self, tally_input, brightness=0.1):
        super(BlinktTallyClient, self).__init__()
        self._tally_input = tally_input
        self._device = BlinktTally('tally', brightness=brightness)

    def handleMessage(self, msgType, source, payload):
        if msgType == CONTROLLED_TALLY_MESSAGE:
            if self._tally_input in payload:
                method = DEVICE_DEFAULT_METHODS[payload[self._tally_input]]
                getattr(self._device, method)()
            else:
                self._device.tallyOff()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        '--controller',
        help="Specify the controller ID to connect to",
        metavar="CONTROLLERID",
        default=""
    )
    parser.add_argument(
        '-t', '--tally', help='Tally input number to monitor', type=int, required=True
    )
    parser.add_argument(
        '-b', '--brightness', help='Brightness of LEDs, between 0 and 1',
        type=float,
        default=0.1
    )
    args = parser.parse_args()

    clear()
    set_pixel(NUM_PIXELS - 1, 0, 0, 255, 0.05)
    show()

    controller = Controller.fromPyro(args.controller)
    client = BlinktTallyClient(args.tally, args.brightness)
    client.run()
