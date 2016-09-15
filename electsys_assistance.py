# Copyright (C) 2016  Sam Jia

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from splinter.browser import Browser
from time import sleep
from os import system
import os
import logging
import sys
import queue
import threading
import urllib.request
import urllib.error
import urllib.parse
from PIL import Image
import pytesseract


class NeedRelogin(Exception):

    def __str__(self):
        return 'need_relogin'


login_page = "http://electsys.sjtu.edu.cn/edu/"
select_page = "http://electsys.sjtu.edu.cn/edu/student/elect/warning.aspx?&xklc=%d&lb=%d"
restart_after = 0
user_name = ''
password = ''
nth_round_text = ['一专海选', '一专抢选', '一专第三轮', '暑假小学期海选', '暑假小学期抢选', '暑假小学期第3轮', '二专抢选', '二专重修']
parameter = {}
lesson_type_text = ['必修课', '限选课', '通识课', '任选课', '新生研讨课']
select_page_parameter = [(1, 1), (2, 1), (3, 1), (1, 3), (2, 3), (3, 3), (4, 2), (5, 2)]
queue = queue.Queue()
no_response = False


class ReloadThread(threading.Thread):

    def __init__(self):
        super(ReloadThread, self).__init__()
        self.restart = False

    def run(self):
        global browser
        try:
            # print 'restart', self.restart
            if self.restart:
                try:
                    browser.quit()
                except:
                    pass
                browser = Browser('chrome')
            else:
                browser.reload()
        except Exception as e:
            logging.getLogger().info('reload page falied')
            logging.getLogger('exception').exception(e)
        else:
            logging.getLogger().info('reload page successfully')


class CheckThread(threading.Thread):

    def __init__(self):
        global no_response
        super(CheckThread, self).__init__()
        self.continue_reload_time = 0
        no_response = False

    def run(self):
        global no_response
        while True:
            # print 'no_response', no_response
            if no_response:
                self.continue_reload_time += 1
                t = ReloadThread()
                t.restart = (self.continue_reload_time > 3)
                print((t.restart))
                t.setDaemon(True)
                t.run()
            else:
                self.continue_reload_time = 0
            no_response = True
            sleep(20)


def initLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ABSPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    fh = logging.FileHandler('%s/electsys.log' % ABSPATH)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(sh)

    logging.getLogger('exception').addHandler(fh)


def readConfig():
    try:
        fp = open('config.txt', 'r', encoding='ascii')
        global user_name, password, restart_after
        user_name = fp.readline().strip()
        password = fp.readline().strip()
        restart_after = int(fp.readline().strip())
        if restart_after == -1:
            restart_after = 1000000
        elif restart_after == 0:
            restart_after = 60
        elif restart_after < -1:
            raise Exception()
        for line in fp:
            if line.strip() != '':
                content = line.split()
                dic = {
                    'nth_round': int(content[0]) - 1,
                    'lesson_type': int(content[1]) - 1,
                    'radio_num': int(content[2]) - 1,
                    'grade_num': content[3],
                    'lesson_code': content[4],
                    'teacher_num': int(content[5]) - 1
                }
                queue.put(dic)
    except Exception as e:
        logging.getLogger().info("load config failed.")
        logging.getLogger('exception').exception(e)
        raise e
    else:
        logging.getLogger().info("load config successfully")


def getCaptcha(cookie):
    captcha_url = 'https://jaccount.sjtu.edu.cn/jaccount/captcha'
    req = urllib.request.Request(captcha_url, headers={'cookie': cookie})
    res = urllib.request.urlopen(req)
    fp = open('captcha.jpg', 'wb')
    fp.write(res.read())
    fp.close()

    image = Image.open('captcha.jpg')
    image.load()
    captcha = pytesseract.image_to_string(image)
    return captcha


def login():
    global browser, no_response
    no_response = False
    try:
        browser.visit(login_page)
        browser.find_link_by_href('login.aspx').click()
        while 'jaccount' in browser.url:
            cookie = '; '.join([('%s=%s' % x) for x in list(browser.cookies.all().items())])
            captcha = getCaptcha(cookie)
            browser.fill('user', user_name)
            browser.fill('pass', password)
            browser.fill('captcha', captcha)
            browser.find_by_value('登 录').click()
            browser.windows.current.close_others()
    except Exception as e:
        logging.getLogger().info("%s login failed." % user_name)
        logging.getLogger('exception').exception(e)
        raise e
    else:
        logging.getLogger().info("%s login successfully" % user_name)
        return


def selectRound(first_time):
    global no_response
    no_response = False
    try:
        browser.visit(select_page % select_page_parameter[parameter['nth_round']])
        if ('message' in browser.url) or ('outTimePage' in browser.url):
            raise NeedRelogin()
        if browser.is_element_present_by_id('btnContinue'):
            browser.find_by_id('CheckBox1').click()
            browser.find_by_id('btnContinue').click()
    except Exception as e:
        logging.getLogger().info("select round %d failed." % (parameter['nth_round'] + 1))
        logging.getLogger('exception').exception(e)
        raise e
    else:
        logging.getLogger().info("select round %d successfully" % (parameter['nth_round'] + 1))


def selectLessonType():
    global no_response
    no_response = False
    try:
        browser.find_by_value(lesson_type_text[parameter['lesson_type']]).click()
    except Exception as e:
        logging.getLogger().info("select lesson type %d failed." % (parameter['lesson_type'] + 1))
        logging.getLogger('exception').exception(e)
    else:
        logging.getLogger().info("select lesson type %d successfully" % (parameter['lesson_type'] + 1))


def selectLessonTag():
    global no_response
    no_response = False
    try:
        # print('lesson_type', parameter['lesson_type'])
        if parameter['lesson_type'] == 1 or parameter['lesson_type'] == 2:
            browser.find_by_value('radioButton')[parameter['radio_num']].click()
        elif parameter['lesson_type'] == 3:
            school_select = browser.find_by_tag('select')[0]
            school_select.click()
            school_select.find_by_tag('option')[parameter['radio_num']].click()
            grade_select = browser.find_by_tag('select')[1]
            grade_select.click()
            grade_select.find_by_value(parameter['grade_num']).click()
            browser.find_by_value('查 询').click()
    except Exception as e:
        logging.getLogger().info("select lesson tag %s failed." % parameter['radio_num'])
        logging.getLogger('exception').exception(e)
    else:
        logging.getLogger().info("select lesson tag %s successfully" % parameter['radio_num'])


def selectLesson():
    global no_response
    no_response = False
    try:
        if(browser.find_by_value(parameter['lesson_code'])):
            browser.find_by_value(parameter['lesson_code'])[0].click()
            browser.find_by_value('课程安排').click()
    except Exception as e:
        logging.getLogger().info("check lesson %s failed." % parameter['lesson_code'])
        logging.getLogger('exception').exception(e)
        raise e
    else:
        logging.getLogger().info("check lesson %s successfully" % parameter['lesson_code'])


def selectTeacher():
    global no_response
    no_response = False
    try:
        teacher_list = browser.find_by_name('myradiogroup')
        if not teacher_list[parameter['teacher_num']].checked:
            lines = browser.find_by_id('LessonTime1_gridMain').find_by_tag('tr')
            if lines[parameter['teacher_num'] + 1].find_by_tag('td')[-1].text != '人数满':
                teacher_list[parameter['teacher_num']].click()
                browser.find_by_value('选定此教师').click()
                if 'message' in browser.url:
                    raise Exception()
                browser.find_by_value('选课提交').click()
            else:
                browser.back()
                logging.getLogger().info("select teacher %d failed." % (parameter['teacher_num'] + 1))
                return False
        else:
            logging.getLogger().info("lesson %s has been choosed" % parameter['lesson_code'])
            return True
    except Exception as e:
        logging.getLogger().info("select teacher %d failed." % (parameter['teacher_num'] + 1))
        logging.getLogger('exception').exception(e)
        raise e
    else:
        logging.getLogger().info("select teacher %d successfully" % (parameter['teacher_num'] + 1))
    return False


def main():
    t = CheckThread()
    t.setDaemon(True)
    t.start()
    readConfig()
    global browser, no_response
    # browser = Browser(driver)
    while not queue.empty():
        try:
            login()
        except Exception as e:
            continue
        for i in range(restart_after):
            global parameter
            if queue.empty():
                return
            parameter = queue.get()
            try:
                if not (browser.find_by_value(parameter['lesson_code'])):
                    selectRound(i == 0)
                    selectLessonType()
                    selectLessonTag()
                selectLesson()
                if not selectTeacher():
                    queue.put(parameter)
                else:
                    logging.getLogger().info("select lesson %s successfully!!!!!" % parameter['lesson_code'])
                sleep(1.5)
            except Exception as e:
                queue.put(parameter)
                if isinstance(e, NeedRelogin):
                    logging.getLogger().info('Sorry, I have to relogin. Please wait for 30 seconds...')
                    for i in range(30):
                        no_response = False
                        sleep(1)
                    break
            no_response = False
            # sleep(1)
        try:
            browser.quit()
        except:
            pass
        browser = Browser(driver)


if __name__ == '__main__':
    # ABSPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    # os.environ['PATH'] += ';%s\\Tesseract-OCR' % ABSPATH
    # system('path')
    # system('pause')
    initLogger()
    driver = 'firefox'
    try:
        browser = Browser('fi1refox')
    except:
        try:
            browser = Browser('chrome')
        except:
            logging.getLogger().fatal('No browser driver!!! Please make sure that \'chromedriver.exe\' does exist.')
            exit(0)
        driver = 'chrome'
    main()
    logging.getLogger().info('All lessons have been chosen successfully, congratulations!!!')
    browser.quit()
    system('PAUSE')
