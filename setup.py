from setuptools import setup
from pathlib import Path




BASE_DIR = Path(__file__).parent.absolute()
with BASE_DIR.open( 'README.md', encoding='utf-8') as f:
    long_description = f.read()
with BASE_DIR.open( 'license.md', encoding='utf-8') as f:
    license = f.read()

setup(name='Coursaros',
      version='2.0.1',
      description='CLI downloader for EDX video courses. Download videos and subtitles from https://edx.org to your computer easily.',
      author='Spyridon Lazanas',
      author_email='contact@rehmat.works',
      url='https://github.com/SpyridonLaz/Coursaros',
      long_description=long_description,
      long_description_content_type='text/markdown',
      license=license,
      entry_points={
          'console_scripts': [
              'coursaros = coursaros.edx_platform:Edx'
          ],
      },
      packages=[
          'Coursaros'
      ],
      install_requires=[
          'beautifulsoup4>=4.9',
          'bs4>=0.0',
          'certifi>=2020.12',
          'chardet>=4.0.0',
          'colorful>=0.5.4',
          'decorator>=4.4',
          'fake-useragent>=0.1',
          'idna>=2.10',
          'lxml>=4.6',
          'requests>=2.25',
          'six>=1.15',
          'soupsieve>=2.2',
          'tqdm>=4.57.0',
          'urllib3>=1.26',
          'validators>=0.18',
          'python-slugify>=4.0'
      ]
      )
