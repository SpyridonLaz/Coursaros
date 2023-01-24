#!/usr/bin/env python3


from pathlib import Path
from Exceptions import EdxLoginError, EdxRequestError
from Platforms.EdxPlatform import Edx
import validators
import os
import sys
from getpass import getpass
import argparse
import time

try:
    from debug import *

except ImportError:
    log = print
    d = print
    pass


parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                 description="Simple web scraper for usage with Edx.org videos.")

parser.add_argument('-u', '--username', action='store_const' ,const=False,
                     help='username')
parser.add_argument('-p', '--password', action='store_const' ,const=False,
                     help='password')
parser.add_argument('-s', '--save-to', action='store_const' ,const=False,
                     help='password')

parser.add_argument('-pl', '--platform', action='store_const' ,const=False,
                    default=True, help='Platform of choice[edx=Edx.org]')
parser.add_argument('-d', '--debug', action='store_const' ,const=False,
                    default=True, help='Disable debug messages to the terminal.')
parser.add_argument('-c', '--colored', action='store_const' ,const=False,
                    default=True, help='Disable colorful messages to the terminal.')
parser.add_argument('-o', '--output', action='store_const' ,const=False,
                    default=True, help="Output messages to the terminal.")
parser.add_argument('-w', '--workers', action='store_const' ,const=False,
                    default=True, help='Number of thread workers.')
try:
    args = parser.parse_args()
except argparse.ArgumentError as e:
    print(e)






def main():
    try:
        email = args.username
        password = args.password
        save_to = args.get('save_to',None)
        while email is None:
            email = str(input('EDX Email: ')).strip()
            if validators.email(email) is True:
                break
            else:
                print('Provided email is invalid.')
                email = None

        while password is None:
            password = str(getpass())

            for i in reversed(range(6)):
                time.sleep(1)
                print (i)
            passhint = '*' * len(password)
            log('Attempting to sign in using {} and {}'.format(email, passhint), 'orange')




        platform = Edx(email=email, password=password, save_to=save_to)
        try:
            platform.sign_in()

        except (EdxLoginError,EdxRequestError) as e:
            log('Sign-in failed. Error: '+str(e), 'red')
            sys.exit(1)
        log('Authentication successful!', 'green')





        number_of_courses = len(platform.courses)
        choices = set()
        if platform.is_authenticated():
            log('Crawling Dashboard content. Please wait..')

            # Show dashboard items and multiple choice.
            [print(f"[{i + 1}]  {course.title}") for i, course in enumerate(platform.courses)]

            while True:
                choice = input(
                    f"\nType [ALL] to select all courses or type it's respective integer between 0 and {number_of_courses} and type[OK] to finalize your choices: ").strip()

                if choice.lower() == 'all':
                    log('Scraping courses. Please wait..')
                    [course.walk() for course in platform.courses]

                if choice.lower() == 'ok':
                    if not choices:
                        log(" Select one or more courses, then type [OK] to finalize your choices.")
                    else:
                        [course.walk() for i, course in enumerate(platform.courses) if i in choices]

                    break

                if choice.isdecimal() and int(choice) <= number_of_courses:
                    choice = int(choice)
                    if choice - 1 not in choices:
                        choices.add(choice - 1)
                        log(f"\n{platform.courses[choice - 1].title} added.\nCurrently selected courses: {choices}\n")
                        continue
                    else:
                        log("You have already chosen this course.")
                else:
                    log("Not a valid number. Retry.", "red")
                    continue
        else:
            log("Loading only previous results.  ")
        count = 0
        [print( f"[{str(i)}]",j) for i,j in platform.courses]
        if False :
            log('Crawling complete! Found {} videos. Downloading videos now.'.format(len(videos)), 'green')
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
                        log('Already downloaded. Skipping {}'.format(save_as))
                    else:
                        log('Downloading video {}'.format(vid_title))
                        edx.download_video(vid.get('video'), save_as)
                        edx.download_video(vid.get('sub'), save_as)

                        log('Downloaded and stored at {}'.format(save_as), 'green')
            log('All done! Videos have been downloaded.')
        else:
            #TODO
            # experimental_choice = str(input('An experimental search might work on some courses. Try experimental search? [y/n]: ')).strip().lower()
            # if experimental_choice =="y":
            #     experimental_scrape()

            sys.exit(1)
    except EdxInvalidCourseError as e:
        log('Looks like you have provided an invalid course_dir URL.', 'red')
        sys.exit(1)
    except EdxNotEnrolledError as e:
        log('Looks like you are not enrolled in this course_dir or you are not authorized.')
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

