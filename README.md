#### 打包exe的命令

`pyinstaller  -n awsBilling -i favicon.ico -p E:\Code\Python\awsBilling\venv\Lib\site-packages -F -c main.py`

- -n 指定exe名称
- -i 指定exe的icon图标
- -p 指定本地导入的包的路径（没有自动打包脚本里导入的第三方包，所以只能手动自定路径）
- -F 打包为一个单独的exe文件
- -c exe运行时显示命令行窗口
- main.py 要打包的脚本文件

##### 部署准备(只需要配置一次)
1. 在本地创建一个文件夹用来放置脚本（awsBill.exe）和配置文件(config.json)
2. 查看本地chrome浏览器的版本和用户配置文件夹目录
   - chrome 中访问 [chrome://version/](chrome://version/)
   - 使用页面中“个人资料路径”的值（去掉最后的“\Default"）,替换配置文件（config.json文件）中“chrome_user_data_path”的值
   - 记下页面中“Google Chrome”中的版本
3. 访问 [chromedriver 镜像地址](http://npm.taobao.org/mirrors/chromedriver/) 下载与 chrome 版本（上一步中记录的版本）一致的 chromedriver
   - 将下载的chromedriver压缩包解压后文件放到脚本文件（awsBill.exe）相同目录下
   - 创建的文件夹目录添加到系统环境变量的path中
   - 用chromedriver.exe的全路径（如：D:\Users\yuyong\Desktop\awsBilling）替换 config.json 文件中“chromedriver_path”的值
   
##### 日常运行使用
1. 打开chrome浏览器，访问aws网站
2. 登录aws网站
3. 双击”awsBilling.exe"文件运行脚本

##### 正常运行情况
1. 自动关闭当前打开的chrome浏览器
2. 自动重新打开chrome浏览器，并访问aws网站
3. 页面会自动进行元素操作，如：展开账单详情
4. 脚本运行结束，自动关闭chrome浏览器
5. 脚本运行完成后，在exe文件相同路径下，生成csv文件，文件命名规则：aws_bill_{year}_{month}.csv  
注：
   - 浏览器关闭后注意查看运行日志，日志末尾打印“脚本执行成功！”才是正常完成，否则会有报错信息。
   - 脚本运行过程中，不要关闭当前的chrome浏览器

##### 查看运行日志
1. awsBill运行后会在系统任务栏显示一个图标，点击图标可以切换到命令行窗口，窗口中会实时打印脚本运行的日志
   注：该日志不会保留，窗口关闭后无法再次查看
   
##### 脚本报错处理
1. 如果运行日志末尾有明确、清晰的提示信息，请按照提示操作
2. 如果运行日志中错误信息看不明白，可以再重复运行两次，如果还是运行不成功，请联系脚本维护人员，并提供日志报错的截图