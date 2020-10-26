from avx.controller.Controller import DeviceProxy
from avx.devices import Device
from avx.devices.net.atem.constants import MessageTypes, VideoSource
from enum import Enum


DEFAULT_OPTIONS = {
    'tallyMessageType': MessageTypes.TALLY,
    'devices': []
}

DEVICE_DEFAULT_METHODS = {
    "standby": "tallyStandby",
    "live": "tallyLive",
    "off": "tallyOff"
}


class TallyState(Enum):
    STANDBY = 'standby'
    LIVE = 'live'
    OFF = 'off'

    @staticmethod
    def get(program, preview):
        if program:
            return TallyState.LIVE
        elif preview:
            return TallyState.STANDBY
        else:
            return TallyState.OFF


CONTROLLED_TALLY_MESSAGE = 'avx-tally.ControlledTally'


def _get_tally_method(device, program, preview):
    tallyState = TallyState.get(program, preview)

    return device['methods'].get(tallyState.value)


class TallyController(Device):
    def __init__(self, deviceID, controller=None, **options):
        super(TallyController, self).__init__(deviceID, controller=controller, **options)
        self._controller = controller
        self._options = DEFAULT_OPTIONS.copy()
        self._options.update(options)

        for device in self._options['devices']:
            if 'tallyInput' in device:
                device['tallyInputSource'] = VideoSource(device['tallyInput'])
            methods = DEVICE_DEFAULT_METHODS.copy()
            methods.update(device.get('methods', {}))
            device['methods'] = methods

    def receiveMessage(self, messageType, sender, payload):
        if messageType == self._options['tallyMessageType']:
            for device in self._options.get('devices', []):
                if device.get('tallyInputSource') in payload:
                    tally = payload[device['tallyInputSource']]
                    method = _get_tally_method(
                        device,
                        tally.get('pgm', False),
                        tally.get('prv', False)
                    )
                    actual_device = DeviceProxy(self._controller, device['deviceID'])
                    getattr(actual_device, method)()

            controlled_tally_message = {}
            for source, tally in payload.iteritems():
                controlled_tally_message[source.value] = TallyState.get(
                    tally.get('pgm', False),
                    tally.get('prv', False)
                )
            self.broadcast(CONTROLLED_TALLY_MESSAGE, controlled_tally_message)


class TallyLogger(Device):
    '''
    Simply logs to stdout when told to change tally state.
    '''
    def tallyStandby(self):
        print 'Stand by'

    def tallyLive(self):
        print 'Live'

    def tallyOff(self):
        print 'Off'
