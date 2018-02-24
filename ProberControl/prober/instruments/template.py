common = [
    'close',
    'whoAmI',
]

sample = ['sample']

reqs = {
    'sample': sample
}

def instrument(instrument_type):
    def instrument_internal(cls):
        if type(cls) is not type:
            raise ValueError('Illegal use of \'instrument\' decorator: {} is not an instrument class.'.format(cls))
        error = ''
        if instrument_type not in reqs:
            raise ValueError('Illegal instrument type: {} defined as {}.'.format(cls, instrument_type))
        for requirement in common + reqs[instrument_type]:
            if getattr(cls, requirement, None) is None:
                error += '\t-> {}\n'.format(requirement)
        if len(error) != 0:
            error = 'Instrument driver {} missing the following methods from definition:\n'.format(cls) + error
            raise AttributeError(error)
        return cls

    return instrument_internal
