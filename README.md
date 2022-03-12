# luna-rush-auto-click
![Luna Rush auto click](https://badgen.net/badge/LunaRushAutoClick/main/green?icon=terminal) 
![Windows](https://badgen.net/github/checks/node-formidable/node-formidable/master/windows)
![Release](https://badgen.net/github/release/dbox-dev/luna-rush-auto-click)
![License](https://badgen.net/github/license/dbox-dev/luna-rush-auto-click)
![Last Commit](https://badgen.net/github/last-commit/dbox-dev/luna-rush-auto-click/main)
![Fork](https://badgen.net/github/forks/dbox-dev/luna-rush-auto-click)
## Donate
#### Smart Chain Wallet(BUSD/BNB)
> 0xc0A75D88D49D38fFa0E96EA2ec808965cF090521

### Warning
- Suitable for people who do not have time to play

### Features
- Login to the game automatically
- Automatically find heroes with energy and go to boss hunt.
- Automatically change the map
- Switch to another tab to save the computer energy and switch back when it's time to boss hunt
- Support multiple screen
- Team arrangement system (Coming soon)
- Brake time system

### Computer and Browser settings
- Unlock your Metamask
- Change your chrome browser color to default color.
- Chrome browser zoom 100%
- Chrome browser Open 2 tabs first tab is game and second tab is another(empty tab or anything)
- Windows display zoom size 100%
- Windows display resolution 1280 x 900 or higher.


### Download and install Python first if you don't have a runtime yet.
> [Download Python](https://www.python.org/downloads/)

### Install python library via pip command
```shell
pip install -r requirements.txt
```
### Break time system configurations
```yaml
---
enable_break_time: True
breaks:
  -
    start: '06:58:00'
    end: '07:10:00'
  -
    start: '23:30:00'
    end: '00:30:00'
---
```

### Run auto click
```shell
python3 index.py
```
or 
```shell
python index.py
```
Have fund with the game.
