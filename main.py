#!/usr/bin/env python3


from EdxPlatform import *
import validators
from os.path import expanduser
import os
import sys
from getpass import getpass
from slugify import slugify
import argparse
import traceback
import time
d = Debugger()


parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),description="Simple web scraper for usage with Edx.org videos.")
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
        course_url = None
        email = None
        password = None
        while course_url is None:
            #course_url = str(input('EdxCourse URL: ')).strip()
            #todo start
            course_url = "https://courses.edx.org/courses/course-v1:NYUx+CYB.PEN.3+1T2021/"
            # course_url = "https://courses.edx.org/courses/course-v1:MITx+6.00.2x+1T2022/"
            #todo end
            if validators.url(course_url):
                break
            print('Please provide a valid URL.')
            course_url = None

        auth_file = os.path.join(expanduser('~'), '.coursetk')
        confirm_auth_use = ''

        if os.path.exists(auth_file):
            while confirm_auth_use not in ['y', 'n']:

                #TODO
                # confirm_auth_use = str(input('Do you want to use configured EDX account? [y/n]: ')).strip().lower()
                confirm_auth_use = "n"
            if confirm_auth_use == 'y':
                with open(auth_file) as f:
                    content = f.read().splitlines()
                    if len(content) >= 2 and validators.email(content[0]) is True:
                        email = str(content[0]).strip()
                        password = str(content[1]).strip()
                    else:
                        print('Auth configuration file is invalid.')

        while email is None:
            email = str(input('EDX Email: ')).strip()
            if validators.email(email) is True:
                break
            else:
                print('Provided email is invalid.')
                email = None

        while password is None:
            password = str(getpass())
        
        dont_ask_again = os.path.join(expanduser('~'), '.edxdontask')
        if confirm_auth_use != 'y' and not os.path.exists(dont_ask_again):
            save_ask_answer = ''
            while save_ask_answer not in ['y', 'n', 'never']:
                save_ask_answer = str(input('Do you want to save this login info? Choose n if it is a shared computer. [y/n/never]: ')).strip().lower()
        
            if save_ask_answer == 'y':
                with open(auth_file, 'w') as f:
                    f.write(email + '\n')
                    f.write(password + '\n')
            elif save_ask_answer == 'never':
                with open(dont_ask_again, 'w') as f:
                    f.write('never-ask-again')

        edx = Edx(email=email, password=password)

        if not edx.is_authenticated:
            for i in reversed(range(6)):
                time.sleep(1)
                print (i)
            passhint = '*' * len(password)
            edx.log_message('Attempting to sign in using {} and {}'.format(email, passhint), 'orange')
            try:
                edx.sign_in()

            except (EdxLoginError,EdxRequestError) as e:
                edx.log_message('Sign-in failed. Error: '+str(e), 'red')
                sys.exit(1)
            edx.log_message('Authentication successful!', 'green')

        edx.log_message('Crawling course content. This may take several minutes.')


        videos = edx.get_course(course_url)

        count = 0
        len(videos)
        if type(videos) is list and len(videos) :
            edx.log_message('Crawling complete! Found {} videos. Downloading videos now.'.format(len(videos)), 'green')
            for vid in videos:
                vid_title = vid.get('title')
                course_name = vid.get('course')
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
        edx.log_message('Looks like you have provided an invalid course URL.', 'red')
        sys.exit(1)
    except EdxNotEnrolledError as e:
        edx.log_message('Looks like you are not enrolled in this course or you are not authorized.')
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

