from __future__ import absolute_import
from argparse import ArgumentParser
from avx.Client import Client
from avx.controller.Controller import Controller
from avx.devices import Device
from avx_tally import CONTROLLED_TALLY_MESSAGE, DEVICE_DEFAULT_METHODS
from blinkt import clear, set_all, show

import atexit


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


class BlinktTallyClient(Client):

    def __init__(self, tally_input):
        super(BlinktTallyClient, self).__init__()
        self._tally_input = tally_input
        self._device = BlinktTally('tally')

    def handleMessage(self, msgType, source, payload):
        if msgType == CONTROLLED_TALLY_MESSAGE:
            if self._tally_input in payload:
                method = DEVICE_DEFAULT_METHODS[payload[self._tally_input].value]
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
    args = parser.parse_args()

    controller = Controller.fromPyro(args.controller)
    client = BlinktTallyClient(args.tally)
    client.start()
    client.started.wait()
    atexit.register(lambda: controller.unregisterClient(client.uri))

    controller.registerClient(client.uri)
