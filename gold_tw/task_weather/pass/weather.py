import requests


def main():
    try:
        r = requests.get('https://wttr.in/Taipei?format=j1')
        print(r.json())
    except Exception as e:
        print('error', e)


if __name__ == '__main__':
    main()
