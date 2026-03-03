use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use anyhow::{anyhow, Result};
use argon2::{
    password_hash::{rand_core::OsRng as ArgonRng, PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Argon2,
};
use base64::{engine::general_purpose::STANDARD as BASE64, Engine};
use rand::RngCore;

/// 加密器
pub struct Encryptor {
    key: [u8; 32],
}

impl Encryptor {
    /// 从密码派生密钥（使用 raw salt 字节）
    pub fn from_password_raw(password: &str, salt_bytes: &[u8]) -> Result<Self> {
        // 使用 Argon2id 派生密钥
        let argon2 = Argon2::default();

        // 从 raw 字节创建 SaltString（用于 password_hash API）
        // SaltString 格式：base64(22 bytes) -> 29 characters without padding
        let salt_b64 = &salt_bytes[..22.min(salt_bytes.len())];
        let salt_str = SaltString::encode_b64(salt_b64)
            .map_err(|e| anyhow!("Failed to create salt string: {}", e))?;

        let password_hash = argon2
            .hash_password(password.as_bytes(), &salt_str)
            .map_err(|e| anyhow!("Failed to derive key: {}", e))?;

        // 从 hash 中提取 32 字节作为 AES 密钥
        let hash_bytes = password_hash.hash.ok_or_else(|| anyhow!("No hash generated"))?;
        let key: [u8; 32] = hash_bytes.as_bytes()[0..32]
            .try_into()
            .map_err(|_| anyhow!("Invalid key length"))?;

        Ok(Self { key })
    }

    /// 生成随机密钥
    pub fn generate_random() -> Self {
        let key = Aes256Gcm::generate_key(&mut OsRng);
        Self { key: key.into() }
    }

    /// 加密数据
    pub fn encrypt(&self, plaintext: &str) -> Result<String> {
        let cipher = Aes256Gcm::new(&self.key.into());
        let nonce = Aes256Gcm::generate_nonce(&mut OsRng);

        let ciphertext = cipher
            .encrypt(&nonce, plaintext.as_bytes())
            .map_err(|e| anyhow!("Encryption failed: {}", e))?;

        // 将 nonce 和 ciphertext 组合后 base64 编码
        let mut combined = nonce.to_vec();
        combined.extend_from_slice(&ciphertext);

        Ok(BASE64.encode(&combined))
    }

    /// 解密数据
    pub fn decrypt(&self, ciphertext: &str) -> Result<String> {
        let combined = BASE64.decode(ciphertext)?;

        if combined.len() < 12 {
            return Err(anyhow!("Invalid ciphertext length"));
        }

        let (nonce_bytes, ciphertext_bytes) = combined.split_at(12);
        let nonce = Nonce::from_slice(nonce_bytes);

        let cipher = Aes256Gcm::new(&self.key.into());
        let plaintext = cipher
            .decrypt(nonce, ciphertext_bytes)
            .map_err(|e| anyhow!("Decryption failed: {}", e))?;

        String::from_utf8(plaintext).map_err(|e| anyhow!("Invalid UTF-8: {}", e))
    }

    /// 获取密钥的 base64 表示
    pub fn get_key_base64(&self) -> String {
        BASE64.encode(&self.key)
    }
}

/// 生成随机 salt
pub fn generate_salt() -> Vec<u8> {
    let mut salt = [0u8; 16];
    rand::rngs::OsRng.fill_bytes(&mut salt);
    salt.to_vec()
}

/// 验证密码（使用 Argon2）
pub fn verify_password_hash(hash: &str, password: &str) -> Result<bool> {
    let parsed_hash =
        PasswordHash::new(hash).map_err(|e| anyhow!("Failed to parse hash: {}", e))?;

    Ok(Argon2::default()
        .verify_password(password.as_bytes(), &parsed_hash)
        .is_ok())
}

/// 生成密码哈希
pub fn generate_password_hash(password: &str) -> Result<String> {
    let salt = SaltString::generate(&mut ArgonRng);
    let argon2 = Argon2::default();

    let hash = argon2
        .hash_password(password.as_bytes(), &salt)
        .map_err(|e| anyhow!("Failed to generate hash: {}", e))?;

    Ok(hash.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encrypt_decrypt() {
        let salt = generate_salt();
        let encryptor = Encryptor::from_password("test-password", &salt).unwrap();

        let plaintext = "Hello, World!";
        let ciphertext = encryptor.encrypt(plaintext).unwrap();
        let decrypted = encryptor.decrypt(&ciphertext).unwrap();

        assert_eq!(plaintext, decrypted);
    }

    #[test]
    fn test_different_passwords() {
        let salt = generate_salt();
        let encryptor1 = Encryptor::from_password("password1", &salt).unwrap();
        let encryptor2 = Encryptor::from_password("password2", &salt).unwrap();

        let plaintext = "Secret Data";
        let ciphertext1 = encryptor1.encrypt(plaintext).unwrap();
        let ciphertext2 = encryptor2.encrypt(plaintext).unwrap();

        assert_ne!(ciphertext1, ciphertext2);
    }

    #[test]
    fn test_password_hash() {
        let password = "secure-password";
        let hash = generate_password_hash(password).unwrap();
        let verified = verify_password_hash(&hash, password).unwrap();

        assert!(verified);

        let wrong_verified = verify_password_hash(&hash, "wrong-password").unwrap();
        assert!(!wrong_verified);
    }
}
