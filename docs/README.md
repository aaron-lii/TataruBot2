# TataruBot2

基于NoneBot2的FF14机器人塔塔露

此分支为开黑啦(KOOK)机器人的简单移植

## 使用

基本流程参考主分支，以下是补充步骤

kook平台机器人适配器插件由nonebot2社区提供，
[插件文档参考](https://github.com/Tian-que/nonebot-adapter-kaiheila/blob/master/MANUAL.md)

1. 安装适配器时请安装以下适配器，主文档中适配器可以不安装

```shell
pip install nonebot-adapter-kaiheila
```

2. 额外需要安装驱动器

```shell
nb driver install httpx
```

3. 将kook机器人的token填入`.env.prod`文件中的对应位置

```
kaiheila_bots=[{"token": "此处填入token"}]
```

4. 启动机器人

```shell
nb run
```

## 针对kook移植做的文件修改

```angular2html

```