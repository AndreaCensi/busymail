from setuptools import setup

setup(name='BusyMail',
	  version="0.2",
	  license="GPL",
      package_dir={'':'src'},
      packages=['busymail'],
      install_requires=['pyyaml','numpy', 'matplotlib', 'imapclient'],
      entry_points={
         'console_scripts': [
           'busymail_log  = busymail.download:main',
           'busymail_plot = busymail.plot:main'
        ]
      }, 
)
