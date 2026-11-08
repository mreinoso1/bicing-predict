import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import status

from api.main import app


@pytest_asyncio.fixture
async def test_client():
    async with LifespanManager(app), httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url = "https://app.io") as test_client:
            yield test_client



@pytest.mark.asyncio
class TestCreatePerson:
    async def test_valid(self, test_client: httpx.AsyncClient, token:dict):
        request = {"station": 2, "hour": 5, "day_of_week": 6}
        response = await test_client.post("/predict", json=request, headers= token)
        assert response.status_code == status.HTTP_200_OK
    
    async def test_missing_token(self, test_client: httpx.AsyncClient):
        request = {"station": 2, "hour": 5, "day_of_week": 6}
        response = await test_client.post("/predict", json=request)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_wrong_token(self, test_client: httpx.AsyncClient):
        request = {"station": 2, "hour": 5, "day_of_week": 6}
        response = await test_client.post("/predict", json=request, headers={"Token":"incorrect"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_wrong_station(self, test_client: httpx.AsyncClient,token:dict):
        request = {"station": 612, "hour": 5, "day_of_week": 6} #Station 612 doesn't exist
        response = await test_client.post("/predict", json=request, headers=token)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_hor(self, test_client: httpx.AsyncClient,token:dict):
        request = {"station": 2, "hour": 220, "day_of_week": 6}
        response = await test_client.post("/predict", json=request,headers= token)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        
