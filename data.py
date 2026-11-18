import requests

# Справочник жанров для быстрых кнопок
GENRES = {
    "🎸 Rock": "rock",
    "🎤 Pop": "pop",
    "🎧 Hip-Hop": "hip-hop",
    "🎹 Electronic": "electronic",
    "🎷 Jazz": "jazz"
}


class MusicAPIClient:
    BASE_URL = "https://itunes." + "apple.com" + "/search"



    def search_songs(self, query: str, limit: int = 10, country: str = "US") -> list[dict]:
        """Выполняет GET-запрос к iTunes API и возвращает список словарей с информацией о треках."""
        if not query.strip():
            raise ValueError("Поисковый запрос не может быть пустым.")

        params = {
            "term": query.strip(),
            "media": "music",
            "entity": "song",
            "limit": limit,
            "country": country
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()  # Вызовет ошибку, если статус код 4xx или 5xx
            data = response.json()
            return self._parse_tracks(data.get("results", []))

        except requests.exceptions.Timeout:
            raise ConnectionError("Превышено время ожидания ответа от сервера iTunes.")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ошибка сети при подключении к API: {e}")
        except ValueError:
            raise RuntimeError("Сервер вернул некорректные данные (не JSON).")

    def _parse_tracks(self, raw_results: list) -> list[dict]:
        """Извлекает только нужные поля из сырого ответа API."""
        parsed = []
        for idx, item in enumerate(raw_results, start=1):
            duration_ms = item.get("trackTimeMillis", 0)
            minutes = duration_ms // 60000
            seconds = (duration_ms % 60000) // 1000

            parsed.append({
                "num": idx,
                "artist": item.get("artistName", "Неизвестен"),
                "title": item.get("trackName", "Без названия"),
                "album": item.get("collectionName", "Сингл"),
                "genre": item.get("primaryGenreName", "—"),
                "year": item.get("releaseDate", "—")[:4],
                "duration": f"{minutes}:{seconds:02d}",
                "url": item.get("trackViewUrl", "")
            })
        return parsed
