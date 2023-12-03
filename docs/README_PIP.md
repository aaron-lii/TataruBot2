# TataruBot2

基于NoneBot2的最终幻想14机器人塔塔露

这里是塔塔露功能作为nonebot2插件安装的指南

## 当前功能

0. 塔塔露帮帮忙：显示所有功能
1. 暖暖：本周时尚品鉴作业
2. 选门：帮你选藏宝洞的门
3. 仙人彩：帮你选每周仙人仙彩数字
4. 物品 物品名：查询物品信息，例：`物品 铁矿`
5. 价格 大区 物品名：查询板子物价，大区不写默认豆豆柴，例：`价格 陆行鸟 铁矿`、`价格 叶小妖`
6. 看看微博：获取FF微博新闻
7. 房子 服务器名 主城名 房子大小：查询空房。主城名为：森都、海都、沙都、白银、雪都。房子大小为：S、M、L。例: `房子 银泪湖 森都 S`
8. 输出 boss名 职业名 (国服) (rdps) (day2): 查询logs上对应boss和职业的dps分段，括号内为可选的参数，默认国际服、adps、截止最后一天。
例: `输出 海德林 武士`，`输出 海德林 武士 国服 day10`
9. 攻略 (副本等级) 副本名关键字 (文本)：查简单副本攻略，括号内为可选参数，默认输出图片攻略
10. 日历：获取FF近期活动日历
11. 招募 大区名：获取指定大区招募板信息
12. 抽卡：随机抽取一张FF14塔罗牌

## 依赖

1. python >= 3.7.3
2. 如果有NoneBot v1则卸载 `pip uninstall nonebot`
3. 本代码测试使用的NoneBot版本是 nonebot2==2.0.0b4

↑↑↑ 既然是作为nonebot2的插件，上面的1.2.3.你应该都已经达到了，姑且放在这里提一下

## 使用

1. 安装塔塔露机器人插件包

   ```shell
   # 为了防止出啥意外先把旧的删了吧
   pip uninstall tatarubot2
   # 如果以前装过塔塔露机器人，把配置文件也删了
   rm tatarubot2_conf.json
   
   # 安装最新插件
   pip install -U tatarubot2
   ```

2. 进入你的机器人文件夹，根据需要修改配置文件`.env.dev`，更多信息见NoneBot2官方文档

   ```shell
   # 注意配置命令起始字符
   # 我的习惯是直接纯中文作为命令，所以添加了一个空 ""，如下所示
   COMMAND_START=["/", ""]  
   ```

3. 在`bot.py`中加载插件

   ```python
   nonebot.load_builtin_plugins("tatarubot2")
   ```
   
5. 首次启动机器人，会自动在机器人文件夹内生成一个插件的配置文件`tatarubot2_conf.json`

   ```shell
   nb run
   ```

6. 根据需要选择开启哪些插件，修改`tatarubot2_conf.json`，将对应"enable"改为true


7. 启动机器人

   ```shell
   nb run
   ```

8. 使用go-cqhttp连接机器人，该部分参考go-cqhttp官方文档。需要注意的是配置中反向websocket设置参考文档https://adapter-onebot.netlify.app/docs/guide/setup

## 备注

NoneBot2官方文档：https://v2.nonebot.dev/

NoneBot2 github：https://github.com/nonebot/nonebot2

go-cqhttp连接配置：https://adapter-onebot.netlify.app/docs/guide/setup

go-cqhttp github：https://github.com/Mrs4s/go-cqhttp
