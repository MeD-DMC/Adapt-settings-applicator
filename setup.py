from setuptools import setup

setup(name='applicator',
      version='0.1',
      description='Patch for Adapt course packages',
      url='https://github.com/MeD-DMC/Adapt-settings-applicator',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['applicator'],
      install_requires=[
          'filetype',
      ],
      zip_safe=False)

      