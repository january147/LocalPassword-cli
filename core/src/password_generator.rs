use rand::Rng;
use zxcvbn::zxcvbn;

/// 密码强度
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PasswordStrength {
    VeryWeak,
    Weak,
    Fair,
    Strong,
    VeryStrong,
}

impl PasswordStrength {
    pub fn from_score(score: u8) -> Self {
        match score {
            0 => PasswordStrength::VeryWeak,
            1 => PasswordStrength::Weak,
            2 => PasswordStrength::Fair,
            3 => PasswordStrength::Strong,
            4 => PasswordStrength::VeryStrong,
            _ => PasswordStrength::VeryWeak,
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            PasswordStrength::VeryWeak => "非常弱",
            PasswordStrength::Weak => "弱",
            PasswordStrength::Fair => "一般",
            PasswordStrength::Strong => "强",
            PasswordStrength::VeryStrong => "非常强",
        }
    }
}

/// 密码生成器选项
#[derive(Debug, Clone)]
pub struct GeneratorOptions {
    pub length: usize,
    pub include_uppercase: bool,
    pub include_lowercase: bool,
    pub include_numbers: bool,
    pub include_symbols: bool,
    pub exclude_similar: bool,
}

impl Default for GeneratorOptions {
    fn default() -> Self {
        Self {
            length: 16,
            include_uppercase: true,
            include_lowercase: true,
            include_numbers: true,
            include_symbols: true,
            exclude_similar: true,
        }
    }
}

/// 密码生成器
pub struct PasswordGenerator;

impl PasswordGenerator {
    /// 生成密码
    pub fn generate(options: &GeneratorOptions) -> String {
        let mut chars = String::new();

        let uppercase = "ABCDEFGHJKLMNPQRSTUVWXYZ";
        let lowercase = "abcdefghijkmnpqrstuvwxyz";
        let numbers = "23456789";
        let symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?";

        let filtered_uppercase = if options.exclude_similar {
            uppercase.to_string()
        } else {
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ".to_string()
        };

        let filtered_lowercase = if options.exclude_similar {
            lowercase.to_string()
        } else {
            "abcdefghijklmnopqrstuvwxyz".to_string()
        };

        let filtered_numbers = if options.exclude_similar {
            numbers.to_string()
        } else {
            "0123456789".to_string()
        };

        if options.include_uppercase {
            chars.push_str(&filtered_uppercase);
        }
        if options.include_lowercase {
            chars.push_str(&filtered_lowercase);
        }
        if options.include_numbers {
            chars.push_str(&filtered_numbers);
        }
        if options.include_symbols {
            chars.push_str(symbols);
        }

        if chars.is_empty() {
            chars = filtered_lowercase;
        }

        let mut rng = rand::thread_rng();
        (0..options.length)
            .map(|_| {
                let idx = rng.gen_range(0..chars.len());
                chars.chars().nth(idx).unwrap()
            })
            .collect()
    }

    /// 生成快速密码（默认选项）
    pub fn generate_quick(length: usize) -> String {
        Self::generate(&GeneratorOptions {
            length,
            ..Default::default()
        })
    }

    /// 生成强密码
    pub fn generate_strong() -> String {
        Self::generate(&GeneratorOptions {
            length: 20,
            include_symbols: true,
            exclude_similar: true,
            ..Default::default()
        })
    }

    /// 生成短语密码（易于记忆）
    pub fn generate_passphrase(word_count: usize) -> String {
        let words = [
            "correct", "horse", "battery", "staple", "apple", "orange", "banana",
            "purple", "monkey", "dragon", "rocket", "planet", "galaxy", "star",
            "ocean", "mountain", "river", "forest", "desert", "cloud", "storm",
            "light", "dark", "fire", "water", "earth", "wind", "time", "space",
        ];

        let mut rng = rand::thread_rng();
        let passphrase: Vec<String> = (0..word_count)
            .map(|_| words[rng.gen_range(0..words.len())].to_string())
            .collect();

        passphrase.join("-")
    }

    /// 检查密码强度
    pub fn check_strength(password: &str, user_inputs: &[&str]) -> (PasswordStrength, String) {
        let result = zxcvbn(password, user_inputs).unwrap_or_else(|_| {
            // 如果zxcvbn失败，返回默认的Entropy值
            zxcvbn::zxcvbn(password, user_inputs).unwrap()
        });

        let strength = PasswordStrength::from_score(result.score());
        let warning = result
            .feedback()
            .as_ref()
            .and_then(|f| f.warning())
            .map(|w| w.to_string())
            .unwrap_or_else(|| "密码强度良好".to_string());

        (strength, warning)
    }

    /// 计算密码熵（位数）
    pub fn calculate_entropy(password: &str) -> f64 {
        let result = zxcvbn(password, &[]).unwrap_or_else(|_| {
            zxcvbn::zxcvbn(password, &[]).unwrap()
        });
        result.guesses_log10() * 3.321928 // log2(10) ≈ 3.321928
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_password() {
        let options = GeneratorOptions::default();
        let password = PasswordGenerator::generate(&options);

        assert_eq!(password.len(), options.length);
    }

    #[test]
    fn test_generate_quick() {
        let password = PasswordGenerator::generate_quick(12);

        assert_eq!(password.len(), 12);
    }

    #[test]
    fn test_generate_passphrase() {
        let passphrase = PasswordGenerator::generate_passphrase(4);

        let parts: Vec<&str> = passphrase.split('-').collect();
        assert_eq!(parts.len(), 4);
    }

    #[test]
    fn test_check_strength() {
        let (strength, _warning) = PasswordGenerator::check_strength("password", &[]);

        assert_eq!(strength, PasswordStrength::VeryWeak);
    }

    #[test]
    fn test_strong_password() {
        let password = PasswordGenerator::generate_strong();
        let (strength, _warning) = PasswordGenerator::check_strength(&password, &[]);

        assert!(strength == PasswordStrength::Strong || strength == PasswordStrength::VeryStrong);
    }
}
