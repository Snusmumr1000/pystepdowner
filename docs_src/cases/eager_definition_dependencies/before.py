def main() -> str:
    service = Service()
    return service.handle()


def instrument(func):
    return func


def normalize(value: str) -> str:
    return value.strip().upper()


class Service:
    normalizer = normalize

    @instrument
    def handle(self, normalizer=normalize) -> str:
        return normalizer(" ok ")
