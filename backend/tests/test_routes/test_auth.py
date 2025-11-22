import pytest
from httpx import AsyncClient


@pytest.mark.routes
class TestAuthRoutes:
    """Test authentication routes"""

    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        """Test user registration"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Test registering with duplicate username"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": test_user.username,
                "email": "different@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registering with duplicate email"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "different",
                "email": test_user.email,
                "password": "password123",
            },
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login"""
        response = await client.post(
            "/api/auth/login",
            json={"username": test_user.username, "password": "testpass123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password"""
        response = await client.post(
            "/api/auth/login",
            json={"username": test_user.username, "password": "wrongpassword"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user"""
        response = await client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "password123"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_basic_auth(self, client: AsyncClient, test_user):
        """Test login using HTTP Basic Auth"""
        response = await client.post(
            "/api/auth/token",
            auth=(test_user.username, "testpass123"),
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_logout(self, client: AsyncClient, test_user):
        """Test logout"""
        # Login first
        login_response = await client.post(
            "/api/auth/login",
            json={"username": test_user.username, "password": "testpass123"},
        )
        assert login_response.status_code == 200

        # Logout
        response = await client.post("/api/auth/logout")

        assert response.status_code == 200
        assert response.json() == {"message": "Logged out successfully"}

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, test_user):
        """Test getting current user info"""
        # Login first
        login_response = await client.post(
            "/api/auth/login",
            json={"username": test_user.username, "password": "testpass123"},
        )

        token = login_response.json()["access_token"]

        # Get current user
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without auth"""
        response = await client.get("/api/auth/me")

        assert response.status_code == 401
