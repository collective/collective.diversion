from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.diversion',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("CHANGES.txt")).read() +
                       open(os.path.join("CONTRIBUTORS.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python",
        ],
      keywords='Zope ZODB',
      author='Matthew Wilkes',
      author_email='matthew@matthewwilkes.co.uk',
      url='https://github.com/collective/collective.diversion',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )