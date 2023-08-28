# Raspberry pi wardriving web tool

This is a web tool for wardriving with a raspberry pi. CURREENTLY still in very early development.
The reason im making this is to learn js and bootstrap mainly, plus it looks cool and i haven't seen 
many others like it. 

- NO the code is not pretty, i will clean it up later. and NO it does not emit a AP yet, it will be coming in soon updates.

## Installation

Clone the repo using git.
![image](https://github.com/im-kuro/piWardriving/assets/86091489/be2873dd-5eb5-4559-92bf-d955a8851a53)

```bash
git clone https://github.com/im-kuro/piwardriving
```

install py libs.
![image](https://github.com/im-kuro/piWardriving/assets/86091489/ac2c2496-c6db-4002-a338-17605fd98a3b)

```bash
pip install -r requirements.txt
```
![image](https://github.com/im-kuro/piWardriving/assets/86091489/61127d6d-9a7d-4d14-8826-435ab0e23e4b)

Run the server (please note future installs will be easier)
```bash
python run.py
```



## Todo
- [x] clean up analytics page & add attacking analytics (captured packets, deauthed networks, ect)
- [x] finish attack page
- [x] finish settings options
- [x] Add deticated page for attacking a specific AP
- [x] add dynamic deauth procs based on cpu usage