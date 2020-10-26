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


def _get_tally_method(device, program, preview):
    if program:
        return device['methods'].get('live')
    elif preview:
        return device['methods'].get('standby')
    else:
        return device['methods'].get('off')


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
