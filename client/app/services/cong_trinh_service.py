import requests
from ..routes import CongTrinhRoutes
from .base import API_URL, handle_response

def get_cong_trinhs(page: int = 1, take: int = 10, search: str = None, author_id: int = None, status: str = None):
    """Get all cong trinh with pagination and filtering"""
    url = f"{API_URL}{CongTrinhRoutes.LIST_CONG_TRINH.value}"
    params = {"page": page, "take": take}
    if search:
        params["search"] = search
    if author_id:
        params["author_id"] = author_id
    if status:
        params["status"] = status
    response = requests.get(url, params=params)
    return handle_response(response)

def get_cong_trinh_by_id(cong_trinh_id: int):
    """Get cong trinh by ID"""
    url = f"{API_URL}{CongTrinhRoutes.GET_CONG_TRINH_ID.value}"
    response = requests.get(url, params={"cong_trinh_id": cong_trinh_id})
    return handle_response(response)

def get_cong_trinh_by_slug(slug: str):
    """Get cong trinh by slug"""
    url = f"{API_URL}{CongTrinhRoutes.GET_CONG_TRINH_SLUG.value}"
    response = requests.get(url, params={"slug": slug})
    return handle_response(response)

def create_cong_trinh(title: str, description: str, content: str, author_id: int, status: str = "draft", slug: str = None):
    """Create new cong trinh"""
    url = f"{API_URL}{CongTrinhRoutes.CREATE_CONG_TRINH.value}"
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

def update_cong_trinh(cong_trinh_id: int, title: str = None, description: str = None, content: str = None, status: str = None, slug: str = None):
    """Update cong trinh"""
    url = f"{API_URL}{CongTrinhRoutes.UPDATE_CONG_TRINH.value}"
    data = {"id": cong_trinh_id}
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
    response = requests.put(url, json=data)
    return handle_response(response)

def update_cong_trinh_image(cong_trinh_id: int, image_file):
    """Update cong trinh image"""
    url = f"{API_URL}{CongTrinhRoutes.UPDATE_CONG_TRINH_IMAGE.value}"
    files = {"image": image_file}
    data = {"id": cong_trinh_id}
    response = requests.put(url, data=data, files=files)
    return handle_response(response)

def delete_cong_trinh(cong_trinh_id: int):
    """Delete cong trinh"""
    url = f"{API_URL}{CongTrinhRoutes.DELETE_CONG_TRINH.value}"
    response = requests.delete(url, params={"id": cong_trinh_id})
    return handle_response(response)
