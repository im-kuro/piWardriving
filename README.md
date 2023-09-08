# Raspberry pi wardriving web tool (EARLY RELEASE)
![image](https://github.com/im-kuro/piWardriving/assets/86091489/4c23b57c-ebf0-4979-8ec5-4e20f516f83b)

This is a web tool for wardriving with a raspberry pi. CURRENTLY still in very early development.
The reason im making this is to learn js and bootstrap mainly, plus it looks cool and i haven't seen 
any others like it. The project is about 65% working now, currently testing on wardriving and how itll
work along with adding bug fixes and cleaning up the code. soon we will have war driving functionality 

- NO the code is not pretty, i will clean it up later. and NO it does not emit a AP yet, it will be coming in soon updates.

## Installation
Please note that this MAY not work with some operating systems. Heres a chart of the known and tested OS's
if you would like to, you can dm me if you have tried it on a os and got it working.

- [x] Kali - NO
- [x] Raspian OS - YES
- [x] Ubuntu - Unknown

### Clone the repo using git.

```bash
git clone https://github.com/im-kuro/piwardriving
```

install py libs.
```bash
pip install -r requirements.txt
```

install tools
```bash
python run.py --install
```


Run the server (please note future installs will be easier)
```bash
python run.py
```

![IMG_0159](https://github.com/im-kuro/piWardriving/assets/86091489/85e43011-b679-4a57-a472-50c3fa0ffa41)


## Todo
- [x] clean up analytics page & add attacking analytics (captured packets, deauthed networks, ect) 40%
- [x] finish attack page
- [x] Add deticated page for attacking a specific AP
- [x] add dynamic deauth procs based on cpu usage
- [x] 
