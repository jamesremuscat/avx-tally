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
                    method = None
                    if tally.get('pgm', False):
                        method = device['methods'].get('live')
                    elif tally.get('prv', False):
                        method = device['methods'].get('standby')
                    else:
                        method = device['methods'].get('off')

                    actual_device = self._controller.getDevice(device['deviceID'])
                    if hasattr(actual_device, method):
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
