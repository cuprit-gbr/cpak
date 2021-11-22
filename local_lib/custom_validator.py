import click
import requests

class URL(click.ParamType):
    name = "url"

    def convert(self, value, param, ctx):
        if not isinstance(value, tuple):
            try:
                response = requests.get(value)
                print(f"{value} is valid and exists on the internet")
            except Exception as e:
                self.fail(
                    f"invalid URL scheme ({value}). Only HTTP(s) provided URL does not exist on Internet",
                    param,
                    ctx,
                )
        return value