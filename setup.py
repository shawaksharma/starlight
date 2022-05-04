from setuptools import setup

setup(name='starlight',
      version='0.0.1',
      description='A simplified command-line interface for the official UK police API.',
      url='https://github.com/Shaka1011/starlight',
      author='shawaksharma',
      license='MIT',
      packages=['starlight'],
      install_requires=["requests", "tabulate"],
      entry_points = {'console_scripts': ['starlight = starlight:main']},
      keywords = ['starlight', 'uk', 'police', 'API', 'command-line', 'cli', 'data'],
      zip_safe=False)
