# iotbot: Nonebot2物联网插件

 ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nonebot2) ![](https://img.shields.io/badge/nonebot2-plugin-green) ![PyPI - License](https://img.shields.io/pypi/l/nonebot-plugin-iot)

## 简介

iotbot提供了一套Nonebot2接入物联网的解决方案，目前只包含天猫精灵终端接入，后续会接入树莓派打造属于Nonebot2自己的物联网环境。

## 快速上手

- 第一步：下载本项目至本地

```shell script
git clone
```

- 第二步：运行项目

可以通过docker在容器中运行
```shell script
docker built -t iotbot .
```

也可以在本地直接运行
```shell script
pip install -r requirements.txt
python bot.py
```

## 项目配置和搭建

- [天猫精灵终端](./docs/ali_genie.md)