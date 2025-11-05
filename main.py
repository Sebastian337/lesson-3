import requests
from urllib.parse import urlparse
from decouple import config
import argparse


def shorten_link(token, url):
    api_url = "https://api.vk.com/method/utils.getShortLink"
    params = {
        "access_token": token,
        "url": url,
        "v": "5.199",
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()

    vk_response = response.json()

    if "error" in vk_response:
        raise requests.exceptions.HTTPError(vk_response["error"])

    return vk_response["response"]["short_url"]


def count_clicks(token, short_url):
    key = urlparse(short_url).path.lstrip("/")
    api_url = "https://api.vk.com/method/utils.getLinkStats"
    params = {
        "access_token": token,
        "key": key,
        "interval": "forever",
        "v": "5.199",
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()

    vk_response = response.json()
    if "error" in vk_response:
        raise requests.exceptions.HTTPError(vk_response["error"])

    stats = vk_response["response"]["stats"]
    return sum(item["views"] for item in stats)


def is_shorten_link(token, url):
    key = urlparse(url).path.lstrip("/")
    api_url = "https://api.vk.com/method/utils.getLinkStats"
    params = {
        "access_token": token,
        "key": key,
        "interval": "day",
        "v": "5.199",
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()

    vk_response = response.json()
    return "response" in vk_response


def build_parser():
    parser = argparse.ArgumentParser(
        description="Создаёт короткую ссылку VK (vk.cc) или показывает количество переходов по короткой ссылке."
    )
    parser.add_argument(
        "url",
        help="Обычная ссылка (для сокращения) или короткая vk.cc (для статистики)"
    )
    return parser


def main():
    token = config("VK_TOKEN")

    parser = build_parser()
    args = parser.parse_args()
    user_url = args.url

    try:
        if is_shorten_link(token, user_url):
            clicks = count_clicks(token, user_url)
            print("Всего переходов по ссылке:", clicks)
        else:
            short_link = shorten_link(token, user_url)
            print("Сокращенная ссылка:", short_link)
    except requests.exceptions.RequestException as e:
        print("Некорректная ссылка или ошибка HTTP:", e)
    except requests.exceptions.HTTPError as e:
        print("Ошибка VK API:", e)


if __name__ == "__main__":
    main()