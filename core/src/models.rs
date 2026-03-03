use serde::{Deserialize, Serialize};
use std::time::SystemTime;

/// 密码条目
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PasswordEntry {
    pub id: Option<i64>,
    pub title: String,
    pub username: String,
    pub password: String,
    pub url: Option<String>,
    pub notes: Option<String>,
    pub category: Option<String>,
    pub created_at: i64,
    pub updated_at: i64,
    pub tags: Vec<String>,
}

impl PasswordEntry {
    pub fn new(
        title: String,
        username: String,
        password: String,
    ) -> Self {
        let now = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64;

        Self {
            id: None,
            title,
            username,
            password,
            url: None,
            notes: None,
            category: None,
            created_at: now,
            updated_at: now,
            tags: Vec::new(),
        }
    }

    pub fn with_url(mut self, url: String) -> Self {
        self.url = Some(url);
        self
    }

    pub fn with_notes(mut self, notes: String) -> Self {
        self.notes = Some(notes);
        self
    }

    pub fn with_category(mut self, category: String) -> Self {
        self.category = Some(category);
        self
    }

    pub fn with_tags(mut self, tags: Vec<String>) -> Self {
        self.tags = tags;
        self
    }
}

/// 分类
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Category {
    pub id: Option<i64>,
    pub name: String,
    pub icon: Option<String>,
    pub color: Option<String>,
}

/// 搜索条件
#[derive(Debug, Clone)]
pub struct SearchQuery {
    pub title: Option<String>,
    pub username: Option<String>,
    pub url: Option<String>,
    pub category: Option<String>,
    pub tags: Vec<String>,
}

impl SearchQuery {
    pub fn new() -> Self {
        Self {
            title: None,
            username: None,
            url: None,
            category: None,
            tags: Vec::new(),
        }
    }

    pub fn with_title(mut self, title: String) -> Self {
        self.title = Some(title);
        self
    }

    pub fn with_username(mut self, username: String) -> Self {
        self.username = Some(username);
        self
    }

    pub fn with_url(mut self, url: String) -> Self {
        self.url = Some(url);
        self
    }

    pub fn with_category(mut self, category: String) -> Self {
        self.category = Some(category);
        self
    }

    pub fn with_tags(mut self, tags: Vec<String>) -> Self {
        self.tags = tags;
        self
    }
}
