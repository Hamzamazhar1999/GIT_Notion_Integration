import requests
from rich.tree import Tree
from rich.console import Console

def fetch_repo_structure(url, parent_node, headers):
    """ Recursively fetch and visualize repository structure """
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        contents = response.json()
        
        for item in contents:
            if item["type"] == "dir":  # If folder, recursively fetch
                folder_node = parent_node.add(f"[bold cyan]📂 {item['name']}[/bold cyan]")
                fetch_repo_structure(item["url"], folder_node, headers)
            else:
                parent_node.add(f"[green]📄 {item['name']}[/green] ({item['size']} bytes)")
    else:
        print(f"Failed to fetch {url}: {response.status_code}")

def visualize_repo(repo_url, token):
    """ Visualize the repo structure using Rich """
    headers = {"Authorization": f"Bearer {token}"}
    console = Console()
    root = Tree(f"[bold yellow]📦 Repository: {repo_url.split('/')[-2]}[/bold yellow]")
    fetch_repo_structure(repo_url, root, headers)
    console.print(root)


def fetch_file_url(repo_url, file_name, token):
    """ Fetch the URL(s) of a specific file in the GitHub repository """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 200:
        contents = response.json()
        file_urls = []  # List to store file URLs
        for item in contents:
            if item["type"] == "dir":  # If it's a directory, recurse
                folder_url = item["url"]
                file_urls.extend(fetch_file_url(folder_url, file_name, token))  # Add results to list
            else:
                if item["name"] == file_name:
                    file_urls.append(item['url'])  # Add file URL to list
        
        return file_urls  # Return the list of file URLs
    else:
        print(f"Failed to fetch {repo_url}: {response.status_code}")
    
    return []  # Return empty list if no file is found
