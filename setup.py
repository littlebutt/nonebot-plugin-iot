from setuptools import setup

setup(
    python_requires=">=3.8",
    name='nonebot-plugin-iot',
    version='1.1.0',
    packages=['iot', 'iot.devices'],
    install_requires=['nonebot2>=2.0.0a1', 'nonebot-adapter-onebot>=2.1.0'],
    url='https://github.com/littlebutt/nonebot-plugin-iot',
    license='MIT License',
    author='littlebutt',
    author_email='luogan199686@gmail.com',
    description='A nonebot2 plugin for IOT devices'
)
