import pytesseract
from os import system
from PIL import Image
import urllib.request
from splinter.browser import Browser

browser = Browser('chrome')
login_page = "http://electsys.sjtu.edu.cn/edu/"
user_name='hnxxjyt'
password='Sam229'



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
            browser.find_by_name('imageField').click()
    except Exception as e:
        pass
    else:
        pass
login()
browser.windows.current.close_others()
system('pause')
try:
    browser.quit()
except:
    pass