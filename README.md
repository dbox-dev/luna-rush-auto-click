# luna-rush-auto-click
![Luna Rush auto click](https://badgen.net/badge/LunaRushAutoClick/main/green?icon=pypi) 
![Windows](https://badgen.net/badge/Windows/Support/green?icon=windows)
![Linux](https://badgen.net/badge/Linux/Not%20Support/red?icon=terminal) 
![Release](https://badgen.net/github/release/dbox-dev/luna-rush-auto-click)
![License](https://badgen.net/github/license/dbox-dev/luna-rush-auto-click)
![Last Commit](https://badgen.net/github/last-commit/dbox-dev/luna-rush-auto-click/main)
![Fork](https://badgen.net/github/forks/dbox-dev/luna-rush-auto-click)
![Stars](https://badgen.net/github/stars/dbox-dev/luna-rush-auto-click)

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
- Team arrangement system
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
# config.yml

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

### Team arrangement system configurations
> [Download Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

```yaml
# config.yml

enable_team_arrangement: True # Set true to enable team arrangement
tesseract_cmd: 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe' # Set tesseract execute (path to exe)
teams: # Set teams with array
  - # team (auto map in initial function)
    a: # Team name
      heros: # Heroes in team
        - 699997
        - 699998
        - 699999
      fight_map_10: True # set True/False fight on map 10/10
    ---
  - # team (auto map in initial function)
    a: # Team name
      heros: # Heroes in team
        - 789997
        - 789998
        - 789999
      fight_map_10: True # set True/False fight on map 10/10
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
