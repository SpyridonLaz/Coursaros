# Coursaros (currently for edx.org)
This is a command-line downloader written in Python. This relies on Selenium. Moreover, at the moment this downloader supports just [https://edx.org](https://edx.org) website only, and it doesn't support other similar websites, but planning to add Coursera in the future. 

**Disclaimer**: You should not use this software to abuse EDX website. I have written this software with a positive intention, that is to help learners download EDX course videos altogether quickly and easily. I am not responsible if anyway regarding the way you use this software. 

## Installation
```bash
//TODO pip3 install coursaros (not yet released) 
```

Or clone this repo and install manually:

```bash
git clone https://github.com/SpyridonLaz/Coursaros.git
cd coursaros
pip3 install -r requirements.txt
python3 setup.py install
```

## Usage
Once installed, a command `coursaros` becomes available in your terminal. Typing `coursaros` and hitting enter in your terminal should bring up the downloader menu. /todo

## Storing Login Credentials ##//todo me config

On a private computer, it is always better if the software doesn't repeatedly ask you for your credentials.
By default, no credentials or cookies are stored, unless explicitly specified.
An option exists to save an authenticated session in Coursaros/{platform}/.cookie so the session will persist even after closing the program. 



## Bugs & Issues
I have developed this package for my own use and now I have uploaded it for the community. Please expect bugs and issues. Bug fixing and improvements are highly appreciated. Send a pull request if you want to improve it or if you have fixed a bug.

Normal users can use the issues section to report bugs and issues for this software. Before opening a new issue, please go through existing ones to be sure that your question has not been asked and answered yet.

## Credits
- [Python](https://www.python.org/) - The programming language that it was written in.
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - For HTML parsing
- [fake-useragent](https://pypi.org/project/fake-useragent/) - For a dynamic user-agent
- [Selenium](https://github.com/SeleniumHQ/selenium) - For dynamic HTML-javascript parsing
- [requests](https://github.com/psf/requests) - To make HTTP requests
- [tqdm](https://github.com/tqdm/tqdm) - To show download progress bar
- [validators](https://github.com/kvesteri/validators) - To validate URL and email input

And thanks to several indirect dependencies that the main dependencies are relying on.
