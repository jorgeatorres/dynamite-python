# encoding: utf-8


class WithSettings(object):
    
    @property
    def settings(self):
        return self._settings['current']

    @settings.setter
    def settings(self, values={}):
        if not hasattr(self, '_settings'):
            self._settings = {'defaults': {}, 'current': {}}
            self._settings['defaults'] = dict(values)

        # TODO: do not overwrite (merge!)
        self._settings['current'] = dict(values)

    def resetSettings(self):
        if hasattr(self, '_settings'):
            self._settings['current'] = self._settings['defaults']