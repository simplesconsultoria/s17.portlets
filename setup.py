from setuptools import setup, find_packages
import os


setup(name='s17.person.portlets',
      version='0.1',
      description="White pages, birthday and profile portlets for person",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Plone :: 4.1",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='portlet person portlets',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='https://github.com/simplesconsultoria/s17.person.portlets',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['s17', 's17.person'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'collective.person',
      ],
      extras_require={
        'test': ['plone.app.testing'],
        },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
