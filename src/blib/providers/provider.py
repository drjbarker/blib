class Provider:
    def request(self,url):
        raise NotImplementedError(
            "Provider subclasses must implement the `request()` method."
        )