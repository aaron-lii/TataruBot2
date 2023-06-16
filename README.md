# TataruBot2

基于NoneBot2的FF14机器人塔塔露

## 当前功能

0. 塔塔露帮帮忙：显示所有功能
1. 暖暖：本周时尚品鉴作业
2. 选门：帮你选藏宝洞的门
3. 仙人彩：帮你选每周仙人仙彩数字
4. 物品 物品名：查询物品信息，例：`物品 铁矿`
5. 价格 大区 物品名：查询板子物价，大区不写默认豆豆柴，例：`价格 陆行鸟 铁矿`、`价格 叶小妖`
6. 看看微博：获取FF微博新闻
7. 新物品 物品名：查物品异常时可以尝试这个版本
8. 新价格 大区 物品名：查物价异常时可以尝试这个版本
9. 房子 服务器名 主城名 房子大小：查询空房。主城名为：森都、海都、沙都、白银、雪都。房子大小为：S、M、L。例: `房子 银泪湖 森都 S`
10. 输出 boss名 职业名 (国服) (rdps) (day2): 查询logs上对应boss和职业的dps分段，括号内为可选的参数，默认国际服、adps、截止最后一天。
例: `输出 海德林 武士`，`输出 海德林 武士 国服 day10`
11. 攻略 (副本等级) 副本名关键字 (文本)：查简单副本攻略，括号内为可选参数，默认输出图片攻略
12. 日历：获取FF近期活动日历

## chatgpt聊天功能

前提：该电脑或服务器科学上网(才能连接上chatgpt_api)，有chatgpt账号。

指令：`塔塔露问问 你想说的话`，例如`塔塔露问问 武士是ff14里的最强职业吗`

设置：配置文件`tatarubot2_conf.json`里开启该插件功能后，`"api_key"`改为自己的chatgpt api key。

chatgpt_api官方文档：https://platform.openai.com/docs/api-reference/chat

## Bing聊天功能

前提：该电脑或服务器科学上网(打开[必应聊天主页](https://bing.com/chat)，能够使用聊天功能)。
好处是不需要Bing账号，但因为Bing是通过搜索网页来生成回答，响应速度较慢。

指令：`bing 你想说的话`，例如`bing 今天天气怎么样？`

会记忆聊天上下文，使用指令：`bing 重置/reset`，可以重置聊天上下文。

设置：依赖 [EdgeGPT](https://github.com/acheong08/EdgeGPT)
1. 安装依赖 `pip install EdgeGPT --upgrade`
2. 配置文件`tatarubot2_conf.json`里开启该插件功能

## 依赖

1. python >= 3.7.3
2. 如果有NoneBot v1则卸载 `pip uninstall nonebot`
3. 本代码测试使用的NoneBot版本是 nonebot2==2.0.0b4
4. 其他依赖安装`pip install -r requirements.txt`
5. 如果要用chatgpt则多安装一个`pip install openai`

## 使用

如果想作为插件使用，请看 https://github.com/aaron-lii/TataruBot2/blob/main/README_PIP.md

1. 安装脚手架nb-cli

   ```shell
   pip install nb-cli
   
   # 国内速度慢可以用阿里源加速，或者别的源，命令如下
   pip install nb-cli -i https://mirrors.aliyun.com/pypi/simple/
   ```

2. 安装适配器

   ```
   nb adapter install nonebot-adapter-onebot
   ```
   
   若要使用debug模式（供开发者使用，普通用户可以跳过这步）
   ```
   nb adapter install nonebot-adapter-console
   ```
   nonebot-adapter-console是基于终端的交互式适配器，可以在本地命令行界面测试插件功能。
   注意：仅用于调试，若代码中使用了其他平台适配器（如onebot）的特定消息类型，使用该适配器时可能会出现异常。

   可以使用以下命令查看可用适配器：
   ```
   nb adapter list
   ```

3. 下载本项目代码，并进入文件夹

   ```
   git clone https://github.com/aaron-lii/TataruBot2.git
   cd TataruBot2
   ```

4. 根据需要修改配置文件`.env.prod`，（开发/调试环境则使用`.env.dev`，使用的配置在`.env`文件中指定）。
    更多信息见[NoneBot2官方文档](https://v2.nonebot.dev/docs/appendices/config)


5. 启动一次机器人，自动生成配置文件`tatarubot2_conf.json`，如果旧版配置文件造成了错误，请删除旧版配置文件。根据需要把想开启的功能下面的"enable"改成true

   ```
   nb run
   ```

6. 再次启动机器人


8. 使用go-cqhttp连接机器人，该部分参考go-cqhttp官方文档。需要注意的是配置中反向websocket设置参考文档https://adapter-onebot.netlify.app/docs/guide/setup

## 备注

NoneBot2官方文档：https://v2.nonebot.dev/

NoneBot2 github：https://github.com/nonebot/nonebot2

go-cqhttp连接配置：https://adapter-onebot.netlify.app/docs/guide/setup

go-cqhttp github：https://github.com/Mrs4s/go-cqhttp
