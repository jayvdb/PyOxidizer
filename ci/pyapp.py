try:
    import poetry
    raise RuntimeError('NameError required')
except NameError as e:
    print('poetry uses __file__: {!r}'.format(e))
