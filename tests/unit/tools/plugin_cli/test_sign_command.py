"""
Tests for the sign command.
"""

import json
import sys
import zipfile
from pathlib import Path

import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "plugin-cli"))

from cli import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


def create_test_package(path: Path) -> Path:
    """Create a valid .vspkg package for testing (schema v4)."""
    # Create plugin directory structure
    plugin_dir = path / "test_plugin"
    plugin_dir.mkdir()
    
    manifest = {
        "schema_version": "4.0",
        "id": "com.test.sign_plugin",
        "name": "Sign Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin for signing",
        "author": {"name": "Test Author", "email": "test@example.com"},
        "license": "MIT",
        "plugin_type": "backend_only",  # Architecture type
        "category": "utilities",         # Functional category
    }
    
    (plugin_dir / "plugin.json").write_text(json.dumps(manifest, indent=2))
    
    # Create module
    module_dir = plugin_dir / "sign_plugin"
    module_dir.mkdir()
    (module_dir / "__init__.py").write_text("# Init")
    (module_dir / "main.py").write_text("# Main module")
    
    (plugin_dir / "README.md").write_text("# Test Plugin")
    
    # Create package
    package_path = path / "com.test.sign_plugin-1.0.0.vspkg"
    
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in plugin_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(plugin_dir)
                zf.write(file_path, arcname)
        
        # Add VSPKG manifest
        vspkg_manifest = {
            "format_version": "1.0",
            "plugin": manifest,
            "created_at": "2026-02-16T00:00:00Z",
        }
        zf.writestr("VSPKG-MANIFEST.json", json.dumps(vspkg_manifest, indent=2))
    
    return package_path


class TestSignGenerate:
    """Tests for keypair generation."""
    
    def test_generate_keypair(self, runner, tmp_path):
        """Test generating a new keypair."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["sign", "--generate-key", "--key-output", "test-key"])
            
            assert result.exit_code == 0, f"Output: {result.output}"
            assert Path("test-key.private").exists()
            assert Path("test-key.public").exists()
            
            # Check file sizes are reasonable (Ed25519 keys)
            assert Path("test-key.private").stat().st_size > 0
            assert Path("test-key.public").stat().st_size > 0
    
    def test_generate_keypair_custom_output(self, runner, tmp_path):
        """Test generating keypair with custom output directory."""
        keys_dir = tmp_path / "keys"
        keys_dir.mkdir()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli,
                ["sign", "--generate-key", "--key-output", str(keys_dir / "my-key")]
            )
            
            assert result.exit_code == 0, f"Output: {result.output}"
            assert (keys_dir / "my-key.private").exists()
            assert (keys_dir / "my-key.public").exists()


class TestSignPackage:
    """Tests for package signing."""
    
    @pytest.fixture
    def test_package(self, tmp_path):
        """Create a test package."""
        return create_test_package(tmp_path)
    
    @pytest.fixture
    def test_keypair(self, tmp_path, runner):
        """Generate a test keypair."""
        runner.invoke(cli, ["sign", "--generate-key", "--key-output", str(tmp_path / "test-key")])
        return tmp_path / "test-key"
    
    def test_sign_package(self, runner, tmp_path, test_package, test_keypair):
        """Test signing a package."""
        result = runner.invoke(
            cli,
            ["sign", str(test_package), "-k", str(test_keypair) + ".private"]
        )
        
        assert result.exit_code == 0
        
        # Check signature file was created
        sig_path = test_package.with_suffix(".vspkg.sig")
        assert sig_path.exists()
        
        # Check signature content
        sig_content = json.loads(sig_path.read_text())
        assert "signature" in sig_content
        assert "public_key" in sig_content
        assert "signature_algorithm" in sig_content
        assert sig_content["signature_algorithm"] == "ed25519"
    
    def test_sign_package_missing_key(self, runner, tmp_path, test_package):
        """Test signing without a key file."""
        result = runner.invoke(
            cli,
            ["sign", str(test_package), "-k", str(tmp_path / "nonexistent.private")]
        )
        
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()


class TestVerifySignature:
    """Tests for signature verification."""
    
    @pytest.fixture
    def signed_package(self, tmp_path, runner):
        """Create and sign a test package."""
        # Create package
        package_path = create_test_package(tmp_path)
        
        # Generate keypair
        runner.invoke(cli, ["sign", "--generate-key", "--key-output", str(tmp_path / "test-key")])
        
        # Sign package
        runner.invoke(
            cli,
            ["sign", str(package_path), "-k", str(tmp_path / "test-key.private")]
        )
        
        return package_path, tmp_path / "test-key.public"
    
    def test_verify_valid_signature(self, runner, signed_package):
        """Test verifying a valid signature."""
        package_path, public_key = signed_package
        
        result = runner.invoke(
            cli,
            ["sign", "--verify", str(package_path), "--public-key", str(public_key)]
        )
        
        assert result.exit_code == 0, f"Output: {result.output}"
        assert "valid" in result.output.lower()
    
    def test_verify_missing_signature(self, runner, tmp_path):
        """Test verifying a package without a signature."""
        package_path = create_test_package(tmp_path)
        
        # Generate just a public key for verification
        runner.invoke(cli, ["sign", "--generate-key", "--key-output", str(tmp_path / "test-key")])
        
        result = runner.invoke(
            cli,
            ["sign", "--verify", str(package_path), "--public-key", str(tmp_path / "test-key.public")]
        )
        
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "signature" in result.output.lower()


class TestSignJsonOutput:
    """Tests for JSON output format."""
    
    def test_sign_json_output(self, runner, tmp_path):
        """Test JSON output for sign operations."""
        # Create package
        package_path = create_test_package(tmp_path)
        
        # Generate keypair
        runner.invoke(cli, ["sign", "--generate-key", "--key-output", str(tmp_path / "test-key")])
        
        # Sign with JSON output
        result = runner.invoke(
            cli,
            [
                "sign", str(package_path),
                "-k", str(tmp_path / "test-key.private"),
                "--json"
            ]
        )
        
        assert result.exit_code == 0, f"Output: {result.output}"
        
        # Parse JSON output
        output = json.loads(result.output)
        assert "success" in output
        assert output["success"] is True
