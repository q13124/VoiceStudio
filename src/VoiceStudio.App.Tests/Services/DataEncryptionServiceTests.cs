using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Text;
using System.Text.Json;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Tests.Services;

[TestClass]
public class DataEncryptionServiceTests
{
    private static byte[] CreateTestMasterKey()
    {
        // Use a fixed test key for deterministic testing
        return Convert.FromBase64String("dGVzdGtleWZvcmVuY3J5cHRpb250ZXN0aW5nb25seQ==");
    }

    #region Byte Encryption/Decryption Tests

    [TestMethod]
    public void Encrypt_WithBytes_ReturnsEncryptedData()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = new byte[] { 1, 2, 3, 4, 5 };

        // Act
        var encrypted = service.Encrypt(plaintext);

        // Assert
        Assert.IsNotNull(encrypted);
        Assert.IsNotNull(encrypted.Ciphertext);
        Assert.IsNotNull(encrypted.Nonce);
        Assert.IsNotNull(encrypted.Tag);
        Assert.IsNotNull(encrypted.Salt);
        Assert.AreEqual(plaintext.Length, encrypted.Ciphertext.Length);
    }

    [TestMethod]
    public void Decrypt_WithValidEncryptedData_ReturnsOriginalBytes()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = new byte[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
        var encrypted = service.Encrypt(plaintext);

        // Act
        var decrypted = service.Decrypt(encrypted);

        // Assert
        CollectionAssert.AreEqual(plaintext, decrypted);
    }

    [TestMethod]
    public void Encrypt_EmptyBytes_EncryptsAndDecrypts()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = Array.Empty<byte>();

        // Act
        var encrypted = service.Encrypt(plaintext);
        var decrypted = service.Decrypt(encrypted);

        // Assert
        Assert.AreEqual(0, decrypted.Length);
    }

    [TestMethod]
    public void Encrypt_LargeData_EncryptsAndDecrypts()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = new byte[100000]; // 100KB
        new Random(42).NextBytes(plaintext);

        // Act
        var encrypted = service.Encrypt(plaintext);
        var decrypted = service.Decrypt(encrypted);

        // Assert
        CollectionAssert.AreEqual(plaintext, decrypted);
    }

    [TestMethod]
    public void Encrypt_SamePlaintext_ProducesDifferentCiphertexts()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = new byte[] { 1, 2, 3, 4, 5 };

        // Act
        var encrypted1 = service.Encrypt(plaintext);
        var encrypted2 = service.Encrypt(plaintext);

        // Assert - due to random nonce, ciphertexts should differ
        Assert.IsFalse(AreByteArraysEqual(encrypted1.Ciphertext, encrypted2.Ciphertext));
        Assert.IsFalse(AreByteArraysEqual(encrypted1.Nonce, encrypted2.Nonce));
    }

    #endregion

    #region String Encryption/Decryption Tests

    [TestMethod]
    public void Encrypt_String_ReturnsEncryptedData()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = "Hello, World!";

        // Act
        var encrypted = service.Encrypt(plaintext);

        // Assert
        Assert.IsNotNull(encrypted);
        Assert.IsTrue(encrypted.Ciphertext.Length > 0);
    }

    [TestMethod]
    public void DecryptToString_ReturnsOriginalString()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = "Secret message with special chars: äöü 中文 🎵";
        var encrypted = service.Encrypt(plaintext);

        // Act
        var decrypted = service.DecryptToString(encrypted);

        // Assert
        Assert.AreEqual(plaintext, decrypted);
    }

    [TestMethod]
    public void Encrypt_EmptyString_EncryptsAndDecrypts()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = string.Empty;

        // Act
        var encrypted = service.Encrypt(plaintext);
        var decrypted = service.DecryptToString(encrypted);

        // Assert
        Assert.AreEqual(plaintext, decrypted);
    }

    [TestMethod]
    public void Encrypt_LongString_EncryptsAndDecrypts()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = new string('A', 100000);

        // Act
        var encrypted = service.Encrypt(plaintext);
        var decrypted = service.DecryptToString(encrypted);

        // Assert
        Assert.AreEqual(plaintext, decrypted);
    }

    #endregion

    #region Object Encryption/Decryption Tests

    [TestMethod]
    public void EncryptObject_SimpleObject_EncryptsAndDecrypts()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var obj = new TestObject { Id = 42, Name = "Test", Value = 3.14 };

        // Act
        var encrypted = service.EncryptObject(obj);
        var decrypted = service.DecryptObject<TestObject>(encrypted);

        // Assert
        Assert.IsNotNull(decrypted);
        Assert.AreEqual(obj.Id, decrypted.Id);
        Assert.AreEqual(obj.Name, decrypted.Name);
        Assert.AreEqual(obj.Value, decrypted.Value);
    }

    [TestMethod]
    public void EncryptObject_ComplexObject_EncryptsAndDecrypts()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var obj = new ComplexTestObject
        {
            Id = 1,
            Items = new[] { "A", "B", "C" },
            Nested = new TestObject { Id = 2, Name = "Nested", Value = 1.23 }
        };

        // Act
        var encrypted = service.EncryptObject(obj);
        var decrypted = service.DecryptObject<ComplexTestObject>(encrypted);

        // Assert
        Assert.IsNotNull(decrypted);
        Assert.AreEqual(obj.Id, decrypted.Id);
        CollectionAssert.AreEqual(obj.Items, decrypted.Items);
        Assert.IsNotNull(decrypted.Nested);
        Assert.AreEqual(obj.Nested.Id, decrypted.Nested.Id);
    }

    [TestMethod]
    public void EncryptObject_NullableProperty_EncryptsAndDecrypts()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var obj = new TestObject { Id = 1, Name = null!, Value = 0 };

        // Act
        var encrypted = service.EncryptObject(obj);
        var decrypted = service.DecryptObject<TestObject>(encrypted);

        // Assert
        Assert.IsNotNull(decrypted);
        Assert.AreEqual(obj.Id, decrypted.Id);
        Assert.IsNull(decrypted.Name);
    }

    #endregion

    #region EncryptedData Serialization Tests

    [TestMethod]
    public void EncryptedData_ToBytes_FromBytes_RoundTrip()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = "Test data for serialization";
        var encrypted = service.Encrypt(plaintext);

        // Act
        var bytes = encrypted.ToBytes();
        var restored = EncryptedData.FromBytes(bytes);

        // Assert
        CollectionAssert.AreEqual(encrypted.Salt, restored.Salt);
        CollectionAssert.AreEqual(encrypted.Nonce, restored.Nonce);
        CollectionAssert.AreEqual(encrypted.Tag, restored.Tag);
        CollectionAssert.AreEqual(encrypted.Ciphertext, restored.Ciphertext);
    }

    [TestMethod]
    public void EncryptedData_ToBase64_FromBase64_RoundTrip()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = "Test data for Base64 serialization";
        var encrypted = service.Encrypt(plaintext);

        // Act
        var base64 = encrypted.ToBase64();
        var restored = EncryptedData.FromBase64(base64);
        var decrypted = service.DecryptToString(restored);

        // Assert
        Assert.AreEqual(plaintext, decrypted);
    }

    [TestMethod]
    public void EncryptedData_Serialized_CanBeDecrypted()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = "Serialized and restored";
        var encrypted = service.Encrypt(plaintext);
        var bytes = encrypted.ToBytes();

        // Act - simulate storing and loading from disk
        var restored = EncryptedData.FromBytes(bytes);
        var decrypted = service.DecryptToString(restored);

        // Assert
        Assert.AreEqual(plaintext, decrypted);
    }

    #endregion

    #region Key Generation Tests

    [TestMethod]
    public void GenerateKey_ReturnsValidBase64Key()
    {
        // Act
        var key1 = DataEncryptionService.GenerateKey();
        var key2 = DataEncryptionService.GenerateKey();

        // Assert
        Assert.IsFalse(string.IsNullOrEmpty(key1));
        Assert.IsFalse(string.IsNullOrEmpty(key2));

        // Should be valid Base64
        var bytes1 = Convert.FromBase64String(key1);
        var bytes2 = Convert.FromBase64String(key2);

        // Should be 32 bytes (256 bits)
        Assert.AreEqual(32, bytes1.Length);
        Assert.AreEqual(32, bytes2.Length);

        // Should be different (random)
        Assert.AreNotEqual(key1, key2);
    }

    #endregion

    #region Dispose Tests

    [TestMethod]
    [ExpectedException(typeof(ObjectDisposedException))]
    public void Encrypt_AfterDispose_ThrowsObjectDisposedException()
    {
        // Arrange
        var service = new DataEncryptionService(CreateTestMasterKey());
        service.Dispose();

        // Act
        service.Encrypt("Should throw");
    }

    [TestMethod]
    [ExpectedException(typeof(ObjectDisposedException))]
    public void Decrypt_AfterDispose_ThrowsObjectDisposedException()
    {
        // Arrange
        var service = new DataEncryptionService(CreateTestMasterKey());
        var encrypted = service.Encrypt("test");
        service.Dispose();

        // Act
        service.Decrypt(encrypted);
    }

    [TestMethod]
    public void Dispose_CalledMultipleTimes_DoesNotThrow()
    {
        // Arrange
        var service = new DataEncryptionService(CreateTestMasterKey());

        // Act & Assert - should not throw
        service.Dispose();
        service.Dispose();
        service.Dispose();
    }

    #endregion

    #region Integrity Tests

    [TestMethod]
    public void Decrypt_TamperedCiphertext_ThrowsException()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = "Original message";
        var encrypted = service.Encrypt(plaintext);

        // Tamper with ciphertext
        var tamperedCiphertext = (byte[])encrypted.Ciphertext.Clone();
        tamperedCiphertext[0] ^= 0xFF;
        var tampered = new EncryptedData
        {
            Ciphertext = tamperedCiphertext,
            Nonce = encrypted.Nonce,
            Tag = encrypted.Tag,
            Salt = encrypted.Salt
        };

        // Act & Assert - AES-GCM throws AuthenticationTagMismatchException for tampering
        Assert.ThrowsException<System.Security.Cryptography.AuthenticationTagMismatchException>(() =>
            service.Decrypt(tampered));
    }

    [TestMethod]
    public void Decrypt_TamperedTag_ThrowsException()
    {
        // Arrange
        using var service = new DataEncryptionService(CreateTestMasterKey());
        var plaintext = "Original message";
        var encrypted = service.Encrypt(plaintext);

        // Tamper with tag
        var tamperedTag = (byte[])encrypted.Tag.Clone();
        tamperedTag[0] ^= 0xFF;
        var tampered = new EncryptedData
        {
            Ciphertext = encrypted.Ciphertext,
            Nonce = encrypted.Nonce,
            Tag = tamperedTag,
            Salt = encrypted.Salt
        };

        // Act & Assert - AES-GCM throws AuthenticationTagMismatchException for tampering
        Assert.ThrowsException<System.Security.Cryptography.AuthenticationTagMismatchException>(() =>
            service.Decrypt(tampered));
    }

    [TestMethod]
    public void Decrypt_WrongKey_ThrowsException()
    {
        // Arrange
        var key1 = Convert.FromBase64String(DataEncryptionService.GenerateKey());
        var key2 = Convert.FromBase64String(DataEncryptionService.GenerateKey());
        
        using var service1 = new DataEncryptionService(key1);
        using var service2 = new DataEncryptionService(key2);
        
        var plaintext = "Secret message";
        var encrypted = service1.Encrypt(plaintext);

        // Act & Assert - decrypting with wrong key should fail (authentication mismatch)
        Assert.ThrowsException<System.Security.Cryptography.AuthenticationTagMismatchException>(() =>
            service2.Decrypt(encrypted));
    }

    #endregion

    #region Cross-Instance Tests

    [TestMethod]
    public void Decrypt_DifferentServiceInstanceWithSameKey_Succeeds()
    {
        // Arrange - create separate key copies since Dispose clears the array
        var keyBase64 = DataEncryptionService.GenerateKey();
        var masterKey1 = Convert.FromBase64String(keyBase64);
        var masterKey2 = Convert.FromBase64String(keyBase64);
        var plaintext = "Cross-instance message";
        
        EncryptedData encrypted;
        using (var service1 = new DataEncryptionService(masterKey1))
        {
            encrypted = service1.Encrypt(plaintext);
        }

        // Act - decrypt with new instance using same key (different array)
        string decrypted;
        using (var service2 = new DataEncryptionService(masterKey2))
        {
            decrypted = service2.DecryptToString(encrypted);
        }

        // Assert
        Assert.AreEqual(plaintext, decrypted);
    }

    #endregion

    #region Helper Methods

    private static bool AreByteArraysEqual(byte[] a, byte[] b)
    {
        if (a.Length != b.Length) return false;
        for (int i = 0; i < a.Length; i++)
        {
            if (a[i] != b[i]) return false;
        }
        return true;
    }

    #endregion

    #region Test Classes

    private class TestObject
    {
        public int Id { get; set; }
        public string? Name { get; set; }
        public double Value { get; set; }
    }

    private class ComplexTestObject
    {
        public int Id { get; set; }
        public string[]? Items { get; set; }
        public TestObject? Nested { get; set; }
    }

    #endregion
}
