# coding=utf-8

from selenium import webdriver
import time
import random
from PIL import Image
from PIL import ImageChops
import operator
import cv2
from selenium.webdriver.common.action_chains import ActionChains
import os

'''
失败有三种原因: 
1. 没对准: 可调整滑动list 
2. 被验出是机器: 可把滑动分成多段,并调试中间的等待时间,模拟成真人
3. 图片没处理好,导致没对准: 优化图片对比函数 
目前发现拼图距离越远成功率越高,太近有概率被检测出为机器,推测原因可能是近的也花费时间太久,导致被发现 
'''


def get_url(url):
    driver.get(url)
    driver.maximize_window()
    user_input = driver.find_element_by_id('input1').send_keys('xxxx')
    password_input = driver.find_element_by_id('input2').send_keys('xxxx')
    signin_button = driver.find_element_by_id('signin').click()
    time.sleep(1)
    get_png()


def get_png():
    '''''获取没缺口的图片'''
    geetest_verify_tip = driver.find_element_by_class_name('geetest_radar_tip').click()
    cut_png('get_png.png')
    get_nick_png()  # 调函数截缺口图


def cut_png(name):
    '''''截图操作'''
    time.sleep(1)
    driver.save_screenshot(name)  # 截整个网页
    url_png = driver.find_elements_by_xpath('//div/canvas')[0]  # 获取图片元素
    left = url_png.location['x']
    top = url_png.location['y']
    elementWidth = url_png.location['x'] + url_png.size['width']
    elementHeight = url_png.location['y'] + url_png.size['height']
    picture = Image.open(name)
    picture = picture.crop((left, top, elementWidth, elementHeight - 26))  # 截图保存 26px是把多余文字去掉
    print(left, top, elementWidth, elementHeight - 26)
    picture.save(name)


def get_nick_png():
    '''''获取有缺口的图片'''
    geetest_slider_button = driver.find_element_by_class_name('geetest_slider_button').click()
    cut_png('get_nick_png.png')
    compare_images()


def compare_images(png1='get_png.png', png2='get_nick_png.png', png3='zzz.png'):
    '''''对比图片,比较不同点,生成新图片'''
    image_one = Image.open(png1)
    image_two = Image.open(png2)
    diff = ImageChops.difference(image_one, image_two)
    # diff = ImageChops.invert(diff)      #反转颜色
    diff.save(png3)
    png_red()


def png_red(png_name='zzz.png'):
    '''''描红'''
    img = cv2.imread(png_name)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)
    binary, contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img, contours, -1, (0, 0, 255), 2)
    # cv2.imshow("img", img)          # 展示
    cv2.imwrite('img.png', img)  # 保存
    Clipping_loop('img.png')


def Clipping_loop(png_name):
    '''''得到需要滑动的距离'''
    picture = Image.open(png_name)
    width = picture.size[0]
    height = picture.size[1]
    width_list = [w for w in range(width)]
    heigth_list = [h for h in range(height)]

    for w in width_list[::-1]:
        for h in heigth_list[::-1]:
            pixel = picture.getpixel((w, h))
            if tuple(pixel) == (255, 0, 0):  # 得到从右边数第一个像素点
                print(w - 47, w)  # 1.需要滑动的距离  2.算出的实际距离
                distance = w - 47  # 得出需要滑动的距离
                get_distance(distance)
                return distance


def get_distance(distance):
    '''''算每次滑动多少'''
    num = 0
    distance += 19
    v = 0
    t = 0.2
    mid = distance * 7 / 8
    num_list = []
    while num < distance:
        if num < mid:
            a = 2
        else:
            a = -3

        s = v * t + 0.5 * a * (t ** 2)
        v = v + a * t
        num += s
        num_list.append(round(s))

    back_tracks = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -2, -1, -1, -0.5]
    tracks = {'num_list': num_list, 'back_tracks': back_tracks}
    print(tracks)
    run(tracks)


def run(tracks):
    '''''滑动'''
    '''''难点就在滑动上,策略是把滑动分为n段进行,模拟真人,现在拼图越远成功率越高'''
    dragger = driver.find_element_by_class_name('geetest_slider_button')  # 定位
    action = ActionChains(driver)
    action.click_and_hold(dragger).perform()  # 按住不松
    time.sleep(random.random())

    time.sleep(0.5)
    for num in tracks['num_list'][0:35]:  # 右滑
        action.move_by_offset(xoffset=num, yoffset=0)
        print(num)
    action.perform()  # 执行滑动
    time.sleep(0.005)

    dragger = driver.find_element_by_class_name('geetest_slider_button')  # 再次定位按钮
    action = ActionChains(driver)
    action.click_and_hold(dragger).perform()
    for num in tracks['num_list'][35:40]:  # 右滑
        action.move_by_offset(xoffset=num, yoffset=0)
        print(num)
    action.perform()  # 执行滑动
    time.sleep(0.004)

    dragger = driver.find_element_by_class_name('geetest_slider_button')  # 再次定位按钮
    action = ActionChains(driver)
    action.click_and_hold(dragger).perform()
    for num in tracks['num_list'][40:]:  # 右滑
        action.move_by_offset(xoffset=num, yoffset=0)
        print(num)
    action.perform()  # 执行滑动
    time.sleep(0.007)

    dragger = driver.find_element_by_class_name('geetest_slider_button')  # 再次定位按钮
    action = ActionChains(driver)
    action.click_and_hold(dragger).perform()  # 按住
    for back_track in tracks['back_tracks'][0:10]:  # 左滑
        action.move_by_offset(xoffset=back_track, yoffset=0)
        print(back_track)
    action.perform()  # 执行滑动
    time.sleep(0.04)

    dragger = driver.find_element_by_class_name('geetest_slider_button')  # 再次定位按钮
    action = ActionChains(driver)
    action.click_and_hold(dragger).perform()  # 按住
    for back_track in tracks['back_tracks'][10:]:  # 左滑
        action.move_by_offset(xoffset=back_track, yoffset=0)
        print(back_track)

    action.release().perform()  # 松开鼠标 执行滑动

    time.sleep(2)
    driver.quit()


if __name__ == '__main__':
    driver = webdriver.Chrome('F:\Google\Chrome\Application\chromedriver.exe')
    get_url('https://passport.cnblogs.com/user/signin')
