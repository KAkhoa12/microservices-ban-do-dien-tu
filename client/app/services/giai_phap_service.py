import requests
from ..routes import GiaiPhapRoutes
from .base import API_URL, handle_response

def get_giai_phaps(page: int = 1, take: int = 10, search: str = None, author_id: int = None, status: str = None):
    """Get all giai phap with pagination and filtering"""
    url = f"{API_URL}{GiaiPhapRoutes.LIST_GIAI_PHAP.value}"
    params = {"page": page, "take": take}
    if search:
        params["search"] = search
    if author_id:
        params["author_id"] = author_id
    if status:
        params["status"] = status
    response = requests.get(url, params=params)
    return handle_response(response)

def get_giai_phap_by_id(giai_phap_id: int):
    """Get giai phap by ID"""
    url = f"{API_URL}{GiaiPhapRoutes.GET_GIAI_PHAP_ID.value}"
    response = requests.get(url, params={"giai_phap_id": giai_phap_id})
    return handle_response(response)

def get_giai_phap_by_slug(slug: str):
    """Get giai phap by slug"""
    url = f"{API_URL}{GiaiPhapRoutes.GET_GIAI_PHAP_SLUG.value}"
    response = requests.get(url, params={"slug": slug})
    return handle_response(response)

def create_giai_phap(title: str, description: str, content: str, author_id: int, status: str = "draft", slug: str = None):
    """Create new giai phap"""
    url = f"{API_URL}{GiaiPhapRoutes.CREATE_GIAI_PHAP.value}"
    data = {
        "title": title,
        "description": description,
        "content": content,
        "author_id": author_id,
        "status": status
    }
    if slug:
        data["slug"] = slug
    response = requests.post(url, json=data)
    return handle_response(response)

def update_giai_phap(
    giai_phap_id: int,
    title: str = None,
    description: str = None, 
    content: str = None,
    status: str = None, 
    slug: str = None,
    youtube_url: str = None
    ):
    """Update giai phap"""
    url = f"{API_URL}{GiaiPhapRoutes.UPDATE_GIAI_PHAP.value}"
    data = {"id": giai_phap_id}
    if title is not None:
        data["title"] = title
    if description is not None:
        data["description"] = description
    if content is not None:
        data["content"] = content
    if status is not None:
        data["status"] = status
    if slug is not None:
        data["slug"] = slug
    if youtube_url is not None:
        data["youtube_url"] = youtube_url
    response = requests.put(url, json=data)
    return handle_response(response)

def update_giai_phap_image(giai_phap_id: int, image_file):
    """Update giai phap image"""
    url = f"{API_URL}{GiaiPhapRoutes.UPDATE_GIAI_PHAP_IMAGE.value}"
    files = {"image": image_file}
    data = {"id": giai_phap_id}
    response = requests.put(url, data=data, files=files)
    return handle_response(response)

def delete_giai_phap(giai_phap_id: int):
    """Delete giai phap"""
    url = f"{API_URL}{GiaiPhapRoutes.DELETE_GIAI_PHAP.value}"
    response = requests.delete(url, params={"id": giai_phap_id})
    return handle_response(response)
