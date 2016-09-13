# Electsys Assistance 上海交大选课助手

## 环境

该项目基于python，环境配置信息如下：

* 版本：64bit python3.5
* 依赖库：splinter, PIL, pytesseract
* 依赖软件：chromedriver.exe, Tesseract-OCR

注：依赖软件已经包含在项目中，无需重新安装

## 打包

项目使用pyinstaller进行打包，打包配置文件为pyinstaller.spec，打包代码文件为pyinstaller.py

打包后项目放在release中，下载后解压即可使用

## 使用

根据readme.txt编写config.txt，执行electsys_assistance.py或release版本的electsys_assistance.exe即可
