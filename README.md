# Raspberry pi wardriving web tool
![image](https://github.com/im-kuro/piWardriving/assets/86091489/4c23b57c-ebf0-4979-8ec5-4e20f516f83b)

This is a web tool for wardriving with a raspberry pi. CURRENTLY still in very early development.
The reason im making this is to learn js and bootstrap mainly, plus it looks cool and i haven't seen 
any others like it. 

- NO the code is not pretty, i will clean it up later. and NO it does not emit a AP yet, it will be coming in soon updates.

## Installation

Clone the repo using git.

```bash
git clone https://github.com/im-kuro/piwardriving
```

install py libs.

```bash
pip install -r requirements.txt
```

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
