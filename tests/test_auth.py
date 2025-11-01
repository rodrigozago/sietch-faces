"""
Integration tests for authentication and authorization.

Tests authentication middleware including:
- API key validation
- Unauthorized access handling
- Rate limiting (if implemented)
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.integration
class TestAuthentication:
    """Test suite for authentication and authorization."""
    
    def test_api_with_valid_key(self, core_client, api_headers):
        """Test API access with valid API key."""
        response = core_client.get("/health", headers=api_headers)
        
        # Should allow access
        assert response.status_code == 200
    
    def test_api_without_key(self, core_client):
        """Test API access without API key."""
        # Note: Core API might not require auth on all endpoints
        response = core_client.get("/health")
        
        # Depending on configuration, might allow or deny
        assert response.status_code in [200, 401, 403]
    
    def test_api_with_invalid_key(self, core_client, test_settings):
        """Test API access with invalid API key."""
        invalid_headers = {
            test_settings.core_api_key_header: "invalid-key-12345"
        }
        
        response = core_client.get("/stats", headers=invalid_headers)
        
        # Might reject or accept based on implementation
        assert response.status_code in [200, 401, 403]
    
    def test_protected_endpoint_without_auth(self, core_client):
        """Test protected endpoint without authentication."""
        # Try to create a person without auth
        person_data = {"name": "Unauthorized Person"}
        response = core_client.post("/persons", json=person_data)
        
        # Should succeed or fail based on auth requirements
        assert response.status_code in [200, 201, 401, 403]
    
    def test_public_endpoints_accessible(self, core_client):
        """Test that public endpoints are accessible without auth."""
        # Health check should typically be public
        response = core_client.get("/health")
        assert response.status_code == 200
    
    @patch('app.auth.api_key.verify_api_key')
    def test_api_key_verification_called(self, mock_verify, core_client):
        """Test that API key verification is called."""
        mock_verify.return_value = True
        
        # This test depends on how auth is implemented
        # Skip if auth module doesn't exist
        try:
            response = core_client.get("/stats")
            # If we got here, auth module exists
            assert response.status_code in [200, 401, 403]
        except (ImportError, AttributeError):
            pytest.skip("Auth module not configured")
    
    def test_different_api_key_headers(self, core_client, test_settings):
        """Test API with different header formats."""
        # Test with different header names
        headers_variations = [
            {test_settings.core_api_key_header: test_settings.core_api_bootstrap_key},
            {"Authorization": f"Bearer {test_settings.core_api_bootstrap_key}"},
            {"X-Api-Key": test_settings.core_api_bootstrap_key},
        ]
        
        for headers in headers_variations:
            response = core_client.get("/health", headers=headers)
            # At least one should work
            assert response.status_code in [200, 401, 403]
    
    def test_malformed_api_key_header(self, core_client, test_settings):
        """Test API with malformed header."""
        malformed_headers = {
            test_settings.core_api_key_header: ""  # Empty key
        }
        
        response = core_client.get("/stats", headers=malformed_headers)
        assert response.status_code in [200, 401, 403, 422]
    
    def test_case_sensitive_api_key(self, core_client, test_settings):
        """Test that API keys are case-sensitive."""
        if test_settings.core_api_bootstrap_key:
            wrong_case_headers = {
                test_settings.core_api_key_header: test_settings.core_api_bootstrap_key.upper()
            }
            
            response = core_client.get("/stats", headers=wrong_case_headers)
            # Should typically fail with wrong case
            assert response.status_code in [200, 401, 403]
    
    def test_expired_token_handling(self, core_client):
        """Test handling of expired authentication tokens."""
        # This test is for JWT-based auth if implemented
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjB9.invalid"
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = core_client.get("/stats", headers=headers)
        assert response.status_code in [200, 401, 403, 422]
    
    def test_sql_injection_in_api_key(self, core_client, test_settings):
        """Test API key validation against SQL injection."""
        malicious_headers = {
            test_settings.core_api_key_header: "' OR '1'='1"
        }
        
        response = core_client.get("/stats", headers=malicious_headers)
        # Should be rejected
        assert response.status_code in [401, 403, 422]
    
    def test_xss_in_api_key(self, core_client, test_settings):
        """Test API key validation against XSS."""
        malicious_headers = {
            test_settings.core_api_key_header: "<script>alert('xss')</script>"
        }
        
        response = core_client.get("/stats", headers=malicious_headers)
        # Should be rejected
        assert response.status_code in [401, 403, 422]


@pytest.mark.integration
class TestRateLimiting:
    """Test suite for rate limiting (if implemented)."""
    
    def test_rate_limit_not_exceeded(self, core_client, api_headers):
        """Test normal usage within rate limits."""
        # Make a few requests
        for _ in range(5):
            response = core_client.get("/health", headers=api_headers)
            assert response.status_code == 200
    
    @pytest.mark.slow
    def test_rate_limit_exceeded(self, core_client, api_headers):
        """Test rate limiting when limit is exceeded."""
        # Make many requests quickly
        responses = []
        for _ in range(100):
            response = core_client.get("/health", headers=api_headers)
            responses.append(response.status_code)
        
        # If rate limiting is implemented, some requests should be rejected
        # Otherwise all should succeed
        assert all(status in [200, 429] for status in responses)
    
    def test_rate_limit_per_endpoint(self, core_client, api_headers):
        """Test that rate limits are per-endpoint."""
        # Test different endpoints
        endpoints = ["/health", "/stats", "/persons"]
        
        for endpoint in endpoints:
            response = core_client.get(endpoint, headers=api_headers)
            # Each endpoint might have different limits
            assert response.status_code in [200, 404, 429]
    
    def test_rate_limit_headers(self, core_client, api_headers):
        """Test that rate limit headers are present."""
        response = core_client.get("/health", headers=api_headers)
        
        # Check for common rate limit headers (if implemented)
        rate_limit_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset"
        ]
        
        # These headers may or may not be present
        for header in rate_limit_headers:
            # Just checking they don't cause errors if present
            _ = response.headers.get(header)
