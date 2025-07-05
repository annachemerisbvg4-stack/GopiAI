import requests

class SmartURLFinder:
    def __init__(self, search_query):
        self.search_query = search_query
        self.api_key = "BSAEcqmI0ZUDsktUV1FKYYYq7HaQlnt"

    def get_first_result_url(self):
        url = "https://api.search.brave.com/res/v1/web/search"
        params = {
            "q": self.search_query,
            "key": self.api_key,
            "count": 1
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json()
            # Verify if there's at least one result
            if "webPages" in results and "value" in results["webPages"]:
                first_result = results["webPages"]["value"][0]
                return first_result.get("url")
        return None

# Example usage:
if __name__ == "__main__":
    finder = SmartURLFinder("leonardo ai")
    url = finder.get_first_result_url()
    if url:
        print(f"Found URL: {url}")
    else:
        print("No URL found.")

