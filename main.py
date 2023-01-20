#!/usr/bin/env python3
from pathlib import Path

from Exceptions import EdxLoginError, EdxRequestError
from Platforms.EdxPlatform import Edx

import validators
from os.path import expanduser
import os
import sys
from getpass import getpass
import argparse
import time

try:
    from debug import LogMessage as log, Debugger as d, DelayedKeyboardInterrupt
    log = log()
    d = d()
except ImportError:
    log = print
    d = print
    pass


parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),description="Simple web scraper for usage with Edx.org videos.")
parser.add_argument('-u', '--username', action='store_const' ,const=False,
                     help='username')
parser.add_argument('-p', '--password', action='store_const' ,const=False,
                     help='password')


parser.add_argument('-d', '--debug', action='store_const' ,const=False,
                    default=True, help='Disable debug messages to the terminal.')
parser.add_argument('-c', '--colored', action='store_const' ,const=False,
                    default=True, help='Disable colorful messages to the terminal.')
try:
    args = parser.parse_args()
except argparse.ArgumentError as e:
    print(e)






def main():
    try:
        email = args.username
        password = args.password
        save_to = None




        while email is None:
            email = str(input('EDX Email: ')).strip()
            if validators.email(email) is True:
                break
            else:
                print('Provided email is invalid.')
                email = None

        while password is None:
            password = str(getpass())

        edx = Edx(email=email, password=password)

        if not edx.is_authenticated:
            for i in reversed(range(6)):
                time.sleep(1)
                print (i)
            passhint = '*' * len(password)
            log('Attempting to sign in using {} and {}'.format(email, passhint), 'orange')
            try:
                edx.sign_in()

            except (EdxLoginError,EdxRequestError) as e:
                log('Sign-in failed. Error: '+str(e), 'red')
                sys.exit(1)
            log('Authentication successful!', 'green')

        log('Crawling dashboard content. This may take several minutes.')
        edx.dashboard_urls()
        count = 0
        [print( f"[{str(i)}]",j) for i,j in edx.courses]
        if False :
            edx.log_message('Crawling complete! Found {} videos. Downloading videos now.'.format(len(videos)), 'green')
            for vid in videos:
                vid_title = vid.get('title')
                course_name = vid.get('course_dir')
                count += 1
                if course_url and vid_title:
                    # if slugify
                    save_main_dir = os.path.join(os.getcwd(), slugify(course_name))
                    countstr = str(count)
                    save_as = os.path.join(save_main_dir, countstr+'{}.mp4'.format(slugify(vid_title)))
                    if not os.path.exists(save_main_dir):
                        os.makedirs(save_main_dir)
                    
                    if os.path.exists(save_as):
                        edx.log_message('Already downloaded. Skipping {}'.format(save_as))
                    else:
                        edx.log_message('Downloading video {}'.format(vid_title))
                        edx.download_video(vid.get('video'), save_as)
                        edx.download_video(vid.get('sub'), save_as)

                        edx.log_message('Downloaded and stored at {}'.format(save_as), 'green')
            edx.log_message('All done! Videos have been downloaded.')
        else:
            #TODO
            # experimental_choice = str(input('An experimental search might work on some courses. Try experimental search? [y/n]: ')).strip().lower()
            # if experimental_choice =="y":
            #     experimental_scrape()

            sys.exit(1)
    except EdxInvalidCourseError as e:
        edx.log_message('Looks like you have provided an invalid course_dir URL.', 'red')
        sys.exit(1)
    except EdxNotEnrolledError as e:
        edx.log_message('Looks like you are not enrolled in this course_dir or you are not authorized.')
        sys.exit(1)
    except KeyboardInterrupt:
        print('\n')
        print('Download cancelled by user.')
        sys.exit(1)
    # except Exception as e:
    #
    #     with open(os.path.join(os.getcwd(), 'edx-error.log'), 'a') as f:
    #         f.write((str(e)))
    #     print('Something unexpected occured. Please provide details present in', os.path.join(os.getcwd()),'edx-error.log file while opening an issue at GitHub.')
    #     sys.exit(1)

