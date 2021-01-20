from avx.controller.Controller import DeviceProxy
from avx.devices import Device
from avx.devices.net.atem.constants import MessageTypes, VideoSource
from enum import Enum


class TallyControlMode(Enum):
    DISABLED = 0
    ENABLED = 1


DEFAULT_OPTIONS = {
    'tallyMessageType': MessageTypes.TALLY,
    'devices': [],
    'initialMode': TallyControlMode.DISABLED.value
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
TALLY_CONTROL_MODE_UPDATE = 'avx-tally.TallyControlModeUpdate'


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

            self._mode = TallyControlMode(
                self._options.get('initialMode', TallyControlMode.DISABLED.value)
            )

        self._previous_message = {}

    def initialise(self):
        super(TallyController, self).initialise()
        self.broadcast(TALLY_CONTROL_MODE_UPDATE, self._mode.value)

    def setMode(self, mode):
        if isinstance(mode, TallyControlMode):
            self._mode = mode
            self.broadcast(TALLY_CONTROL_MODE_UPDATE, self._mode.value)
            self.receiveMessage(
                self._options['tallyMessageType'],
                self.deviceID,
                self._previous_message
            )
        else:
            raise Exception('Invalid control mode: {}'.format(mode))

    def receiveMessage(self, messageType, sender, payload):
        if messageType == self._options['tallyMessageType']:
            for device in self._options.get('devices', []):
                if self._mode == TallyControlMode.DISABLED:
                    tally = {}
                else:
                    if 'tallyInputSource' not in device:
                        print device
                    tally = payload.get(device.get('tallyInputSource'), {})

                method = _get_tally_method(
                    device,
                    tally.get('pgm', False),
                    tally.get('prv', False)
                )
                actual_device = DeviceProxy(self._controller, device['deviceID'])
                try:
                    getattr(actual_device, method)()
                except Exception:
                    pass  # I guess they don't want to know...
                    # More usefully: this could be a device that has gone
                    # away, been switched off, etc - we should try it
                    # again next time, so nothing more to do here.

            controlled_tally_message = {}
            if self._mode != TallyControlMode.DISABLED:
                for source, tally in payload.iteritems():
                    controlled_tally_message[source.value] = TallyState.get(
                        tally.get('pgm', False),
                        tally.get('prv', False)
                    ).value
            self.broadcast(CONTROLLED_TALLY_MESSAGE, controlled_tally_message)
            self._previous_message = payload


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
