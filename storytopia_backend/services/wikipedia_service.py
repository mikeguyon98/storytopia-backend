import requests


def wikipedia_search(query, limit=5):
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "srprop": "snippet",
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    results = []
    for item in data["query"]["search"]:
        title = item["title"]
        snippet = item["snippet"]
        url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        results.append({"title": title, "snippet": snippet, "url": url})

    return results


# # Example usage
# query = "Python programming"
# results = wikipedia_search(query)

# for result in results:
#     print(f"Title: {result['title']}")
#     print(f"URL: {result['url']}")
#     print(f"Snippet: {result['snippet']}")
#     print("---")