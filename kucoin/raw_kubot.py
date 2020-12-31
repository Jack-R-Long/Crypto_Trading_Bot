import requests


def request_public_socket_token():
    url='https://api.kucoin.com//api/v1/bullet-public'
    myobj = {'somekey': 'somevalue'}

    x = requests.post(url, myobj)

    print(x.text)

if __name__=='__main__':
    request_public_socket_token()



SOCKET = "wss://push1-v2.kucoin.com/endpoint"
