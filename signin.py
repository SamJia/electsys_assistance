import urllib.request, urllib.parse, urllib.error
import pytesseract
from PIL import Image
import urllib.request, urllib.error, urllib.parse
from splinter.browser import Browser

# image = Image.open('captcha.png')
# image.load()
# vcode = pytesseract.image_to_string(image)
# print vcode


captcha_url = 'https://jaccount.sjtu.edu.cn/jaccount/captcha'
# req = urllib.urlretrieve(url, 'captcha.jpg')

# fp = open('test.html', 'w')
# fp.write(content)
# fp.close()

browser = Browser('chrome')
browser.visit('http://electsys.sjtu.edu.cn/edu/index.aspx')
browser.find_link_by_href('login.aspx').click()
print(browser.cookies.all())
cookie = '; '.join([('%s=%s' % x) for x in list(browser.cookies.all().items())])
print(cookie)

req = urllib.request.Request(captcha_url, headers={'cookie': cookie})
res = urllib.request.urlopen(req);
content = res.read()
fp = open('captcha.jpg', 'wb')
fp.write(content)
fp.close()

image = Image.open('captcha.jpg')
image.load()
vcode = pytesseract.image_to_string(image)
print(vcode)

browser.fill('user', 'hnxxjyt')
browser.fill('pass', 'Sam229')
browser.fill('captcha', vcode)
browser.find_by_name('imageField').click()

# opener = urllib2.build_opener()
# opener.addheaders.append(('Cookie', 'cookiename=cookievalue'))
# f = opener.open("http://example.com/")
