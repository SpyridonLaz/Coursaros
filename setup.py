from setuptools import setup
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
print(BASE_DIR)
with open(BASE_DIR.joinpath('README.md'), encoding='utf-8') as f:
    long_description = f.read()
with open(BASE_DIR.joinpath('license.md'), encoding='utf-8') as f:
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
          "beautifulsoup4>=4.11.2",
          "lxml>=4.9.2",
          "pdfkit>=1.0.0",
          "requestium>=0.2.0",
          "requests>=2.28.2",
          "selenium>=4.8.2",
          "validators>=0.20.0",
          "setuptools~=65.5.1",
      ]
      )
