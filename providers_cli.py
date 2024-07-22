from typing import Optional, List, Dict

import typer
import requests

from cli.utils import console, parse_headers, error, check_url_method, print_response

from app.models.provider import Provider

app = typer.Typer(context_settings={ "help_option_names": ["-h", "--help"] })

def post_provider_to_url(name: str, endpoint_url: str,
                         headers: Optional[Dict[str, str]], timeout: int = 120, verbose: bool = True):
    request_headers = { 'Content-Type': 'application/json' }

    if headers:
        request_headers.update(headers)

    provider_data = Provider(name=name).model_dump(mode='json')

    if verbose:
        console.print('POST', end=' ')
        console.print(endpoint_url, style="file", highlight=False)  

    try:
        response = requests.post(endpoint_url, json=provider_data, headers=request_headers, timeout=timeout)

        if response.status_code == 201:
            console.print(f"Added Provider: {name}", style="green")
        elif response.status_code == 200:
            if verbose:
                console.print(f"Provider {name} already added", style="cyan")
        
        if verbose:
            print_response(response)
        
        response.raise_for_status()
    except requests.RequestException as e:
        error(f"Failed to add provider: {e}")

@app.command()
def add_provider(
    name: str = typer.Argument(..., help="Name of the provider to add"),
    post: str = typer.Option(..., help="URL to POST the provider data"),
    headers: Optional[List[str]] = typer.Option(None, "--header", help="Headers to include in the request"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Display only important information"),
):
    """
    Add a new provider by making a POST request to the specified URL with optional headers.
    """
    check_url_method(post, 'POST')

    post_provider_to_url(name, post, headers=parse_headers(headers), verbose=not quiet)

if __name__ == "__main__":
    app()
