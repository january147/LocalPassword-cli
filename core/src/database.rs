use crate::crypto::{Encryptor, generate_salt};
use crate::models::{PasswordEntry, Category, SearchQuery};
use anyhow::{anyhow, Result, Context};
use rusqlite::{Connection, params};
use std::path::Path;
use std::sync::{Arc, Mutex};

/// 数据库管理器
pub struct Database {
    conn: Arc<Mutex<Connection>>,
    encryptor: Option<Encryptor>,
}

impl Database {
    /// 创建新数据库（带加密）
    pub fn new<P: AsRef<Path>>(
        path: P,
        master_password: &str,
    ) -> Result<Self> {
        let conn = Connection::open(path)
            .context("Failed to open database")?;

        // 初始化表结构
        Self::init_schema(&conn)?;

        // 生成 salt 并保存
        let salt = generate_salt();
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('salt', ?1)",
            params![hex::encode(&salt)],
        )?;

        // 保存密码哈希用于验证
        let hash = crate::crypto::generate_password_hash(master_password)?;
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('master_hash', ?1)",
            params![hash],
        )?;

        // 创建加密器
        let encryptor = Encryptor::from_password_raw(master_password, &salt)?;

        Ok(Self {
            conn: Arc::new(Mutex::new(conn)),
            encryptor: Some(encryptor),
        })
    }

    /// 打开现有数据库
    pub fn open<P: AsRef<Path>>(
        path: P,
        master_password: &str,
    ) -> Result<Self> {
        let conn = Connection::open(path)
            .context("Failed to open database")?;

        // 读取 salt
        let salt_hex: String = conn.query_row(
            "SELECT value FROM settings WHERE key = 'salt'",
            [],
            |row| row.get(0),
        )?;
        let salt = hex::decode(&salt_hex)
            .context("Invalid salt in database")?;

        // 验证密码
        let hash: String = conn.query_row(
            "SELECT value FROM settings WHERE key = 'master_hash'",
            [],
            |row| row.get(0),
        )?;

        let verified = crate::crypto::verify_password_hash(&hash, master_password)?;
        if !verified {
            return Err(anyhow!("Invalid master password"));
        }

        // 创建加密器
        let encryptor = Encryptor::from_password_raw(master_password, &salt)?;

        Ok(Self {
            conn: Arc::new(Mutex::new(conn)),
            encryptor: Some(encryptor),
        })
    }

    /// 初始化数据库表结构
    fn init_schema(conn: &Connection) -> Result<()> {
        // 设置表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )",
            [],
        )?;

        // 密码条目表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                url TEXT,
                notes TEXT,
                category TEXT,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )",
            [],
        )?;

        // 标签表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )",
            [],
        )?;

        // 密码-标签关联表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS password_tags (
                password_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (password_id, tag_id),
                FOREIGN KEY (password_id) REFERENCES passwords(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )",
            [],
        )?;

        // 分类表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                icon TEXT,
                color TEXT
            )",
            [],
        )?;

        // 创建索引
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_passwords_title ON passwords(title)",
            [],
        )?;
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_passwords_category ON passwords(category)",
            [],
        )?;

        Ok(())
    }

    /// 添加密码条目
    pub fn add_password(&self, entry: PasswordEntry) -> Result<i64> {
        let encryptor = self.encryptor.as_ref()
            .ok_or_else(|| anyhow!("Not unlocked"))?;

        let conn = self.conn.lock().unwrap();

        // 加密密码
        let encrypted_password = encryptor.encrypt(&entry.password)?;

        conn.execute(
            "INSERT INTO passwords (title, username, password, url, notes, category, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![
                entry.title,
                entry.username,
                encrypted_password,
                entry.url,
                entry.notes,
                entry.category,
                entry.created_at,
                entry.updated_at,
            ],
        )?;

        let id = conn.last_insert_rowid();

        // 处理标签
        if !entry.tags.is_empty() {
            self.add_tags_internal(&conn, id, &entry.tags)?;
        }

        Ok(id)
    }

    /// 获取密码条目（解密）
    pub fn get_password(&self, id: i64) -> Result<PasswordEntry> {
        let encryptor = self.encryptor.as_ref()
            .ok_or_else(|| anyhow!("Not unlocked"))?;

        let conn = self.conn.lock().unwrap();

        let entry: (String, String, String, Option<String>, Option<String>, Option<String>, i64, i64) =
            conn.query_row(
                "SELECT title, username, password, url, notes, category, created_at, updated_at
                 FROM passwords WHERE id = ?1",
                params![id],
                |row| {
                    Ok((
                        row.get(0)?,
                        row.get(1)?,
                        row.get(2)?,
                        row.get(3)?,
                        row.get(4)?,
                        row.get(5)?,
                        row.get(6)?,
                        row.get(7)?,
                    ))
                },
            )?;

        // 解密密码
        let decrypted_password = encryptor.decrypt(&entry.2)?;

        // 获取标签
        let tags = self.get_tags_internal(&conn, id)?;

        Ok(PasswordEntry {
            id: Some(id),
            title: entry.0,
            username: entry.1,
            password: decrypted_password,
            url: entry.3,
            notes: entry.4,
            category: entry.5,
            created_at: entry.6,
            updated_at: entry.7,
            tags,
        })
    }

    /// 列出所有密码条目（不解密密码）
    pub fn list_passwords(&self) -> Result<Vec<PasswordEntry>> {
        let conn = self.conn.lock().unwrap();

        let mut stmt = conn.prepare(
            "SELECT id, title, username, url, category, created_at, updated_at
             FROM passwords ORDER BY created_at DESC",
        )?;

        let entries = stmt.query_map([], |row| {
            Ok(PasswordEntry {
                id: Some(row.get(0)?),
                title: row.get(1)?,
                username: row.get(2)?,
                password: String::new(), // 不返回密码
                url: row.get(3)?,
                notes: None,
                category: row.get(4)?,
                created_at: row.get(5)?,
                updated_at: row.get(6)?,
                tags: Vec::new(),
            })
        })?;

        let mut result = Vec::new();
        for entry in entries {
            result.push(entry?);
        }

        Ok(result)
    }

    /// 搜索密码条目
    pub fn search_passwords(&self, query: &SearchQuery) -> Result<Vec<PasswordEntry>> {
        let conn = self.conn.lock().unwrap();

        let mut sql = "SELECT id, title, username, url, category, created_at, updated_at
                       FROM passwords WHERE 1=1".to_string();
        let mut params: Vec<Box<dyn rusqlite::ToSql>> = Vec::new();

        if let Some(title) = &query.title {
            sql.push_str(" AND title LIKE ?");
            params.push(Box::new(format!("%{}%", title)));
        }
        if let Some(username) = &query.username {
            sql.push_str(" AND username LIKE ?");
            params.push(Box::new(format!("%{}%", username)));
        }
        if let Some(url) = &query.url {
            sql.push_str(" AND url LIKE ?");
            params.push(Box::new(format!("%{}%", url)));
        }
        if let Some(category) = &query.category {
            sql.push_str(" AND category = ?");
            params.push(Box::new(category.clone()));
        }

        sql.push_str(" ORDER BY created_at DESC");

        let mut stmt = conn.prepare(&sql)?;

        // 手动绑定参数
        let mut entries = Vec::new();
        let mut rows = stmt.query(rusqlite::params_from_iter(params.iter().map(|p| p.as_ref())))?;

        while let Some(row) = rows.next()? {
            entries.push(PasswordEntry {
                id: Some(row.get(0)?),
                title: row.get(1)?,
                username: row.get(2)?,
                password: String::new(),
                url: row.get(3)?,
                notes: None,
                category: row.get(4)?,
                created_at: row.get(5)?,
                updated_at: row.get(6)?,
                tags: Vec::new(),
            });
        }

        Ok(entries)
    }

    /// 更新密码条目
    pub fn update_password(&self, entry: PasswordEntry) -> Result<()> {
        let encryptor = self.encryptor.as_ref()
            .ok_or_else(|| anyhow!("Not unlocked"))?;

        let id = entry.id.ok_or_else(|| anyhow!("Entry must have an ID"))?;

        let conn = self.conn.lock().unwrap();

        // 加密密码
        let encrypted_password = encryptor.encrypt(&entry.password)?;

        conn.execute(
            "UPDATE passwords
             SET title = ?1, username = ?2, password = ?3, url = ?4, notes = ?5,
                 category = ?6, updated_at = ?7
             WHERE id = ?8",
            params![
                entry.title,
                entry.username,
                encrypted_password,
                entry.url,
                entry.notes,
                entry.category,
                entry.updated_at,
                id,
            ],
        )?;

        // 更新标签
        self.delete_tags_internal(&conn, id)?;
        if !entry.tags.is_empty() {
            self.add_tags_internal(&conn, id, &entry.tags)?;
        }

        Ok(())
    }

    /// 删除密码条目
    pub fn delete_password(&self, id: i64) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute("DELETE FROM passwords WHERE id = ?1", params![id])?;
        Ok(())
    }

    /// 添加分类
    pub fn add_category(&self, category: Category) -> Result<i64> {
        let conn = self.conn.lock().unwrap();

        conn.execute(
            "INSERT INTO categories (name, icon, color) VALUES (?1, ?2, ?3)",
            params![category.name, category.icon, category.color],
        )?;

        Ok(conn.last_insert_rowid())
    }

    /// 列出所有分类
    pub fn list_categories(&self) -> Result<Vec<Category>> {
        let conn = self.conn.lock().unwrap();

        let mut stmt = conn.prepare("SELECT id, name, icon, color FROM categories")?;

        let categories = stmt.query_map([], |row| {
            Ok(Category {
                id: Some(row.get(0)?),
                name: row.get(1)?,
                icon: row.get(2)?,
                color: row.get(3)?,
            })
        })?;

        let mut result = Vec::new();
        for category in categories {
            result.push(category?);
        }

        Ok(result)
    }

    /// 内部方法：添加标签
    fn add_tags_internal(&self, conn: &Connection, password_id: i64, tags: &[String]) -> Result<()> {
        for tag_name in tags {
            // 获取或创建标签
            let tag_id: i64 = match conn.query_row(
                "SELECT id FROM tags WHERE name = ?1",
                params![tag_name],
                |row| row.get(0),
            ) {
                Ok(id) => id,
                Err(_) => {
                    conn.execute("INSERT INTO tags (name) VALUES (?1)", params![tag_name])?;
                    conn.last_insert_rowid()
                }
            };

            // 关联密码和标签
            conn.execute(
                "INSERT OR IGNORE INTO password_tags (password_id, tag_id) VALUES (?1, ?2)",
                params![password_id, tag_id],
            )?;
        }
        Ok(())
    }

    /// 内部方法：获取标签
    fn get_tags_internal(&self, conn: &Connection, password_id: i64) -> Result<Vec<String>> {
        let mut stmt = conn.prepare(
            "SELECT t.name FROM tags t
             JOIN password_tags pt ON t.id = pt.tag_id
             WHERE pt.password_id = ?1",
        )?;

        let tags = stmt.query_map(params![password_id], |row| row.get(0))?;

        let mut result = Vec::new();
        for tag in tags {
            result.push(tag?);
        }

        Ok(result)
    }

    /// 内部方法：删除标签关联
    fn delete_tags_internal(&self, conn: &Connection, password_id: i64) -> Result<()> {
        conn.execute(
            "DELETE FROM password_tags WHERE password_id = ?1",
            params![password_id],
        )?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::tempdir;

    #[test]
    fn test_create_database() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("test.db");

        let db = Database::new(&db_path, "master-password").unwrap();

        // 添加一个密码
        let entry = PasswordEntry::new(
            "Test Entry".to_string(),
            "testuser".to_string(),
            "testpass123".to_string(),
        );

        let id = db.add_password(entry).unwrap();
        assert!(id > 0);

        // 获取密码
        let retrieved = db.get_password(id).unwrap();
        assert_eq!(retrieved.title, "Test Entry");
        assert_eq!(retrieved.username, "testuser");
        assert_eq!(retrieved.password, "testpass123");
    }

    #[test]
    fn test_open_database() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("test.db");

        // 创建数据库
        Database::new(&db_path, "master-password").unwrap();

        // 打开数据库（正确密码）
        let db = Database::open(&db_path, "master-password").unwrap();
        assert!(db.list_passwords().unwrap().is_empty());

        // 错误密码
        let result = Database::open(&db_path, "wrong-password");
        assert!(result.is_err());
    }

    #[test]
    fn test_search_passwords() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("test.db");

        let db = Database::new(&db_path, "master-password").unwrap();

        // 添加多个密码
        let entry1 = PasswordEntry::new(
            "Gmail".to_string(),
            "user@gmail.com".to_string(),
            "pass1".to_string(),
        );
        let entry2 = PasswordEntry::new(
            "Facebook".to_string(),
            "user@fb.com".to_string(),
            "pass2".to_string(),
        );
        let entry3 = PasswordEntry::new(
            "GitHub".to_string(),
            "user@github.com".to_string(),
            "pass3".to_string(),
        );

        db.add_password(entry1).unwrap();
        db.add_password(entry2).unwrap();
        db.add_password(entry3).unwrap();

        // 搜索
        let query = SearchQuery::new().with_title("Git".to_string());
        let results = db.search_passwords(&query).unwrap();

        assert_eq!(results.len(), 1);
        assert_eq!(results[0].title, "GitHub");
    }
}
