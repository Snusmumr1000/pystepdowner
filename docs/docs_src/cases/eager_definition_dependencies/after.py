def main() -> str:
    service = Service()
    return service.handle()


def normalize(value: str) -> str:
    return value.strip().upper()


def instrument(func):
    return func


class Service:
    normalizer = normalize

    @instrument
    def handle(self, normalizer=normalize) -> str:
        return normalizer(" ok ")
