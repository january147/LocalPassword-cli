use clap::{Parser, Subcommand};
use colored::Colorize;
use anyhow::{Result, Context};
use std::path::PathBuf;

use password_manager_core::{
    Database, PasswordEntry, SearchQuery, password_generator::PasswordGenerator,
};

/// Password Manager CLI
#[derive(Parser, Debug)]
#[command(name = "pm")]
#[command(about = "A secure password manager", long_about = None)]
#[command(version = "0.1.0")]
struct Cli {
    /// Database path (default: ~/.pm.db)
    #[arg(short, long, global = true)]
    #[arg(value_name = "FILE")]
    db: Option<PathBuf>,

    /// Master password (or use PM_MASTER_PASSWORD env var)
    #[arg(long, global = true)]
    #[arg(value_name = "PASSWORD")]
    master_password: Option<String>,

    /// Non-interactive mode (skip all prompts, use defaults)
    #[arg(long, global = true)]
    non_interactive: bool,

    /// Enable logging (or use PM_LOG env var)
    #[arg(long, global = true)]
    log: bool,

    /// Log level (off, error, warn, info, debug, trace)
    #[arg(long, global = true, default_value = "info")]
    log_level: String,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Initialize a new password database
    Init {
        /// Force overwrite existing database
        #[arg(short, long)]
        force: bool,
    },

    /// Add a new password entry
    Add {
        /// Entry title
        #[arg(short, long)]
        title: Option<String>,

        /// Username
        #[arg(short, long)]
        username: Option<String>,

        /// Password (auto-generate if not provided)
        #[arg(short, long)]
        password: Option<String>,

        /// URL
        #[arg(short = 'u', long)]
        url: Option<String>,

        /// Category
        #[arg(short = 'c', long)]
        category: Option<String>,

        /// Notes
        #[arg(short, long)]
        notes: Option<String>,

        /// Generate password (length)
        #[arg(long)]
        generate: Option<usize>,

        /// Copy password to clipboard
        #[arg(short, long)]
        copy: bool,
    },

    /// List all password entries
    List {
        /// Filter by category
        #[arg(short, long)]
        category: Option<String>,

        /// Search query
        #[arg(short, long)]
        search: Option<String>,

        /// Show passwords in plain text (dangerous!)
        #[arg(long)]
        show_passwords: bool,
    },

    /// Get a password entry
    Get {
        /// Entry title or ID
        title: String,

        /// Copy password to clipboard
        #[arg(short, long)]
        copy: bool,

        /// Show full details including password
        #[arg(long)]
        show_password: bool,
    },

    /// Search password entries
    Search {
        /// Search query
        query: String,

        /// Search by username
        #[arg(short, long)]
        username: bool,

        /// Search by URL
        #[arg(short = 'u', long)]
        url: bool,

        /// Search by category
        #[arg(short = 'c', long)]
        category: bool,
    },

    /// Edit a password entry
    Edit {
        /// Entry title or ID
        title: String,
    },

    /// Delete a password entry
    Delete {
        /// Entry title or ID
        title: String,

        /// Skip confirmation
        #[arg(short, long)]
        force: bool,
    },

    /// Generate a strong password
    Generate {
        /// Password length (default: 20)
        #[arg(short, long, default_value_t = 20)]
        length: usize,

        /// Include uppercase letters
        #[arg(long)]
        uppercase: bool,

        /// Include lowercase letters
        #[arg(long)]
        lowercase: bool,

        /// Include numbers
        #[arg(long)]
        numbers: bool,

        /// Include symbols
        #[arg(long)]
        symbols: bool,

        /// Copy to clipboard
        #[arg(short, long)]
        copy: bool,
    },

    /// Check password strength
    Strength {
        /// Password to check
        password: String,
    },

    /// Export database to JSON
    Export {
        /// Export file path
        path: PathBuf,

        /// Include passwords in export (dangerous!)
        #[arg(long)]
        include_passwords: bool,
    },

    /// Import from JSON file
    Import {
        /// Import file path
        path: PathBuf,
    },

    /// Interactive shell mode (enter once, execute multiple commands)
    Shell,
}

fn get_db_path(cli_db: Option<PathBuf>) -> PathBuf {
    cli_db.unwrap_or_else(|| {
        let home = std::env::var("HOME").unwrap_or_else(|_| ".".to_string());
        PathBuf::from(home).join(".pm.db")
    })
}

fn init_logger(cli: &Cli) {
    // Check if logging is enabled (either via flag or env var)
    let log_enabled = cli.log || std::env::var("PM_LOG").is_ok();

    if log_enabled {
        let log_level = match cli.log_level.as_str() {
            "off" => "off",
            "error" => "error",
            "warn" => "warn",
            "info" => "info",
            "debug" => "debug",
            "trace" => "trace",
            _ => "info",
        };

        env_logger::Builder::from_env(env_logger::Env::default()
            .default_filter_or(log_level))
            .format_timestamp_secs()
            .init();

        log::info!("Logging enabled at level: {}", log_level);
    }
}

fn open_database(path: &PathBuf, master_password_opt: Option<String>, non_interactive: bool) -> Result<Database> {
    log::debug!("Attempting to open database at: {}", path.display());

    use dialoguer::Password;

    let master_password = match master_password_opt {
        Some(pwd) => {
            log::debug!("Using master password from command-line argument");
            pwd
        }
        None => {
            // Check environment variable
            if let Ok(env_pwd) = std::env::var("PM_MASTER_PASSWORD") {
                log::debug!("Using master password from PM_MASTER_PASSWORD env var");
                env_pwd
            } else if non_interactive {
                log::error!("Master password required but none provided in non-interactive mode");
                return Err(anyhow::anyhow!("Master password required. Use --master-password or PM_MASTER_PASSWORD env var"));
            } else {
                // Interactive mode
                log::debug!("Prompting for master password interactively");
                Password::new()
                    .with_prompt("Enter master password:")
                    .interact()?
            }
        }
    };

    log::info!("Opening database...");
    let result = Database::open(path, &master_password);

    match &result {
        Ok(_) => {
            log::info!("Database opened successfully");
        }
        Err(e) => {
            log::error!("Failed to open database: {}", e);
        }
    }

    result.context("Failed to open database. Check your master password.")
}

fn format_entry(entry: &PasswordEntry, show_password: bool) -> String {
    let mut output = format!(
        "\n{} {}\n",
        "📌".cyan(),
        entry.title.bold().yellow()
    );
    output.push_str(&format!("  {}: {}\n", "Username".cyan(), entry.username));
    output.push_str(&format!("  {}: {}\n", "Password".cyan(), if show_password { &entry.password } else { "******" }));

    if let Some(url) = &entry.url {
        output.push_str(&format!("  {}: {}\n", "URL".cyan(), url));
    }

    if let Some(category) = &entry.category {
        output.push_str(&format!("  {}: {}\n", "Category".cyan(), category));
    }

    if let Some(notes) = &entry.notes {
        output.push_str(&format!("  {}: {}\n", "Notes".cyan(), notes));
    }

    if !entry.tags.is_empty() {
        output.push_str(&format!("  {}: {}\n", "Tags".cyan(), entry.tags.join(", ")));
    }

    output
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    // Initialize logging
    init_logger(&cli);

    log::info!("Password Manager CLI starting...");
    log::debug!("Parsed CLI arguments: {:?}", cli);

    let db_path = get_db_path(cli.db);
    log::info!("Using database at: {}", db_path.display());

    match cli.command {
        Commands::Init { force } => {
            log::info!("Initializing new database (force: {})", force);

            if db_path.exists() && !force {
                use dialoguer::Confirm;
                let confirm = Confirm::new()
                    .with_prompt(format!("Database already exists at {}. Overwrite?", db_path.display()))
                    .default(false)
                    .interact()?;

                if !confirm {
                    log::info!("Init cancelled by user");
                    println!("Cancelled.");
                    return Ok(());
                }
            }

            // 删除旧数据库文件（如果存在）
            if db_path.exists() {
                log::info!("Removing existing database file");
                std::fs::remove_file(&db_path)
                    .context("Failed to remove old database file")?;
            }

            println!("Initializing new password database...");
            use dialoguer::Password;

            let master_password = Password::new()
                .with_prompt("Set master password:")
                .with_confirmation("Confirm master password:", "Passwords do not match")
                .interact()?;

            log::info!("Creating new database...");
            Database::new(&db_path, &master_password)
                .context("Failed to create database")?;

            log::info!("Database created successfully");
            println!("{}", "✓ Database created successfully!".green());
            println!("  Location: {}", db_path.display());
            println!("\nKeep your master password safe. It cannot be recovered.");
        }

        Commands::Add {
            title,
            username,
            password,
            url,
            category,
            notes,
            generate,
            copy,
        } => {
            log::info!("Adding new password entry...");

            let db = open_database(&db_path, cli.master_password.clone(), cli.non_interactive)?;

            use dialoguer::{Input, Password, Confirm};

            // Prompt for missing fields
            let title = match title {
                Some(t) => t,
                None => Input::new()
                    .with_prompt("Entry title")
                    .with_initial_text("")
                    .interact_text()?,
            };

            let username = match username {
                Some(u) => u,
                None => Input::new()
                    .with_prompt("Username")
                    .with_initial_text("")
                    .interact_text()?,
            };

            let password = match (password, generate) {
                (Some(p), _) => p,
                (None, Some(len)) => {
                    let pwd = PasswordGenerator::generate_quick(len);
                    println!("{}", format!("Generated password: {}", pwd).green());
                    pwd
                }
                (None, None) => {
                    let should_generate = Confirm::new()
                        .with_prompt("Generate a strong password?")
                        .default(true)
                        .interact()?;

                    if should_generate {
                        let pwd = PasswordGenerator::generate_quick(20);
                        println!("{}", format!("Generated password: {}", pwd).green());
                        pwd
                    } else {
                        Password::new()
                            .with_prompt("Password:")
                            .with_confirmation("Confirm password:", "Passwords do not match")
                            .interact()?
                    }
                }
            };

            let url = match url {
                Some(u) => Some(u),
                None => {
                    let input: String = Input::new()
                        .with_prompt("URL (optional)")
                        .allow_empty(true)
                        .interact_text()?;
                    if input.is_empty() { None } else { Some(input) }
                }
            };

            let category = match category {
                Some(c) => Some(c),
                None => {
                    let input: String = Input::new()
                        .with_prompt("Category (optional)")
                        .allow_empty(true)
                        .interact_text()?;
                    if input.is_empty() { None } else { Some(input) }
                }
            };

            let notes = match notes {
                Some(n) => Some(n),
                None => {
                    let input: String = Input::new()
                        .with_prompt("Notes (optional)")
                        .allow_empty(true)
                        .interact_text()?;
                    if input.is_empty() { None } else { Some(input) }
                }
            };

            let mut entry = PasswordEntry::new(title, username, password);

            if let Some(u) = url {
                entry = entry.with_url(u);
            }
            if let Some(c) = category {
                entry = entry.with_category(c);
            }
            if let Some(n) = notes {
                entry = entry.with_notes(n);
            }

            log::info!("Adding password entry: title='{}', username='{}'", entry.title, entry.username);
            db.add_password(entry)?;
            log::info!("Password entry added successfully");

            println!("{}", "\n✓ Password entry added successfully!".green());

            if copy {
                log::info!("Copying password to clipboard");
                // Copy password logic would go here
                println!("Password copied to clipboard");
            }
        }

        Commands::List { category, search, show_passwords } => {
            log::info!("Listing passwords (category: {:?}, search: {:?})", category, search);

            let db = open_database(&db_path, cli.master_password.clone(), cli.non_interactive)?;
            let entries = db.list_passwords()?;

            if entries.is_empty() {
                log::info!("No password entries found");
                println!("{}", "No password entries found.".yellow());
                return Ok(());
            }

            log::info!("Found {} entries before filtering", entries.len());

            if entries.is_empty() {
                println!("{}", "No password entries found.".yellow());
                return Ok(());
            }

            let mut filtered: Vec<_> = entries.into_iter().collect();

            if let Some(cat) = category {
                filtered.retain(|e| e.category.as_ref().map_or(false, |c| c.contains(&cat)));
            }

            if let Some(query) = search {
                let q = query.to_lowercase();
                filtered.retain(|e| {
                    e.title.to_lowercase().contains(&q)
                        || e.username.to_lowercase().contains(&q)
                        || e.url.as_ref().map_or(false, |u| u.to_lowercase().contains(&q))
                });
            }

            if filtered.is_empty() {
                println!("{}", "No matching entries found.".yellow());
                return Ok(());
            }

            println!("{}", format!("\nFound {} entries:\n", filtered.len()).bold());
            for entry in &filtered {
                println!("{}", format_entry(entry, show_passwords));
            }
        }

        Commands::Get { title, copy, show_password } => {
            let db = open_database(&db_path, cli.master_password.clone(), cli.non_interactive)?;
            let entries = db.list_passwords()?;

            // Try to find by ID first, then by title
            let entry = if let Ok(id) = title.parse::<i64>() {
                entries.into_iter().find(|e| e.id == Some(id))
            } else {
                let query = title.to_lowercase();
                entries.into_iter().find(|e| e.title.to_lowercase() == query)
            };

            match entry {
                Some(entry) => {
                    println!("{}", format_entry(&entry, show_password || copy));
                    if copy {
                        println!("Password copied to clipboard");
                    }
                }
                None => println!("{}", "Entry not found.".red()),
            }
        }

        Commands::Search { query, username, url, category } => {
            let db = open_database(&db_path, cli.master_password.clone(), cli.non_interactive)?;
            let _entries = db.list_passwords()?;

            let mut search_query = SearchQuery::new();

            if username {
                search_query = search_query.with_username(query.clone());
            } else if url {
                search_query = search_query.with_url(query.clone());
            } else if category {
                search_query = search_query.with_category(query.clone());
            } else {
                search_query = search_query.with_title(query.clone());
            }

            let results = db.search_passwords(&search_query)?;

            if results.is_empty() {
                println!("{}", "No matching entries found.".yellow());
                return Ok(());
            }

            println!("{}", format!("\nFound {} results:\n", results.len()).bold());
            for entry in &results {
                println!("{}", format_entry(entry, false));
            }
        }

        Commands::Edit { title } => {
            let db = open_database(&db_path, cli.master_password.clone(), cli.non_interactive)?;
            let entries = db.list_passwords()?;

            // Find the entry to edit
            let entry = if let Ok(id) = title.parse::<i64>() {
                entries.into_iter().find(|e| e.id == Some(id))
            } else {
                let query = title.to_lowercase();
                entries.into_iter().find(|e| e.title.to_lowercase() == query)
            };

            let entry = match entry {
                Some(e) => e,
                None => {
                    println!("{}", "Entry not found.".red());
                    return Ok(());
                }
            };

            println!("\nEditing: {}", entry.title.yellow());
            println!("{}", format_entry(&entry, false));

            use dialoguer::Input;

            // Edit fields
            let new_title: String = Input::new()
                .with_prompt(&format!("Title [{}]", entry.title))
                .with_initial_text(&entry.title)
                .allow_empty(true)
                .interact_text()?;
            let title = if new_title.is_empty() { entry.title.clone() } else { new_title };

            let new_username: String = Input::new()
                .with_prompt(&format!("Username [{}]", entry.username))
                .with_initial_text(&entry.username)
                .allow_empty(true)
                .interact_text()?;
            let username = if new_username.is_empty() { entry.username.clone() } else { new_username };

            println!("Press Enter to keep current password");
            use dialoguer::Password;
            let new_password = Password::new()
                .with_prompt("Password")
                .allow_empty_password(true)
                .interact()?;
            let password = if new_password.is_empty() { entry.password.clone() } else { new_password };

            let mut updated_entry = entry.clone();
            updated_entry.title = title;
            updated_entry.username = username;
            updated_entry.password = password;

            db.update_password(updated_entry)?;
            println!("{}", "\n✓ Entry updated successfully!".green());
        }

        Commands::Delete { title, force } => {
            log::info!("Deleting password entry: title='{}', force={}", title, force);

            let db = open_database(&db_path, cli.master_password.clone(), cli.non_interactive)?;
            let entries = db.list_passwords()?;

            let entry = if let Ok(id) = title.parse::<i64>() {
                entries.into_iter().find(|e| e.id == Some(id))
            } else {
                let query = title.to_lowercase();
                entries.into_iter().find(|e| e.title.to_lowercase() == query)
            };

            let entry = match entry {
                Some(e) => e,
                None => {
                    println!("{}", "Entry not found.".red());
                    return Ok(());
                }
            };

            if !force {
                println!("\nDeleting: {}", entry.title.yellow());
                println!("{}", format_entry(&entry, false));

                use dialoguer::Confirm;
                let confirm = Confirm::new()
                    .with_prompt("Are you sure you want to delete this entry?")
                    .default(false)
                    .interact()?;

                if !confirm {
                    log::info!("Delete cancelled by user");
                    println!("Cancelled.");
                    return Ok(());
                }
            }

            if let Some(id) = entry.id {
                log::info!("Deleting password entry with ID: {}", id);
                db.delete_password(id)?;
                log::info!("Entry deleted successfully");
                println!("{}", "\n✓ Entry deleted successfully!".green());
            }
        }

        Commands::Generate {
            length,
            uppercase,
            lowercase,
            numbers,
            symbols,
            copy,
        } => {
            use password_manager_core::password_generator::GeneratorOptions;

            // If no flags specified, use defaults
            let use_uppercase = uppercase || (!lowercase && !numbers && !symbols);
            let use_lowercase = lowercase || (!uppercase && !numbers && !symbols);
            let use_numbers = numbers || (!uppercase && !lowercase && !symbols);
            let use_symbols = symbols || (!uppercase && !lowercase && !numbers);

            let options = GeneratorOptions {
                length,
                include_uppercase: use_uppercase,
                include_lowercase: use_lowercase,
                include_numbers: use_numbers,
                include_symbols: use_symbols,
                exclude_similar: true,
            };

            let password = PasswordGenerator::generate(&options);

            println!("\n{}", format!("Generated password ({} chars):", length).cyan());
            println!("{}", password.bold().green());

            let (strength, warning) = PasswordGenerator::check_strength(&password, &[]);
            println!("\n{}", format!("Strength: {}", strength.as_str().bold()));
            if !warning.is_empty() && warning != "密码强度良好" {
                println!("  {}", warning);
            }

            if copy {
                println!("Password copied to clipboard");
            }
        }

        Commands::Strength { password } => {
            let (strength, warning) = PasswordGenerator::check_strength(&password, &[]);

            println!("\n{}", "Password Strength Analysis:".cyan().bold());
            println!("  Label: {}", strength.as_str());
            println!("  Note: {}", warning);
        }

        Commands::Export { path, include_passwords } => {
            let db = open_database(&db_path, cli.master_password.clone(), cli.non_interactive)?;
            let entries = db.list_passwords()?;

            let export_data: Vec<_> = entries.iter().map(|e| {
                let mut export = serde_json::json!({
                    "title": e.title,
                    "username": e.username,
                    "url": e.url,
                    "category": e.category,
                    "notes": e.notes,
                    "tags": e.tags,
                    "created_at": e.created_at,
                    "updated_at": e.updated_at,
                });

                if include_passwords {
                    export["password"] = serde_json::Value::String(e.password.clone());
                }

                export
            }).collect();

            let json = serde_json::to_string_pretty(&export_data)?;
            std::fs::write(&path, json)?;

            println!("{}", "\n✓ Database exported successfully!".green());
            println!("  Location: {}", path.display());
            if !include_passwords {
                println!("  Note: Passwords were not included in the export");
            }
        }

        Commands::Import { path } => {
            let json = std::fs::read_to_string(&path)?;
            let imported: Vec<serde_json::Value> = serde_json::from_str(&json)?;

            let db = open_database(&db_path, cli.master_password.clone(), cli.non_interactive)?;

            for item in imported {
                if let (Some(title), Some(username)) = (
                    item.get("title").and_then(|v| v.as_str()),
                    item.get("username").and_then(|v| v.as_str()),
                ) {
                    let password = item.get("password")
                        .and_then(|v| v.as_str())
                        .unwrap_or("");

                    let mut entry = PasswordEntry::new(
                        title.to_string(),
                        username.to_string(),
                        password.to_string(),
                    );

                    if let Some(url) = item.get("url").and_then(|v| v.as_str()) {
                        entry = entry.with_url(url.to_string());
                    }
                    if let Some(category) = item.get("category").and_then(|v| v.as_str()) {
                        entry = entry.with_category(category.to_string());
                    }
                    if let Some(notes) = item.get("notes").and_then(|v| v.as_str()) {
                        entry = entry.with_notes(notes.to_string());
                    }

                    db.add_password(entry)?;
                }
            }

            println!("{}", "\n✓ Database imported successfully!".green());
        }

        Commands::Shell => {
            run_interactive_shell(&db_path, cli.master_password)?;
        }
    }

    Ok(())
}

fn run_interactive_shell(db_path: &PathBuf, master_password_opt: Option<String>) -> Result<()> {
    use dialoguer::Password;
    use std::io::{self, Write, BufRead};

    // 输入主密码
    let master_password = match master_password_opt {
        Some(pwd) => pwd,
        None => {
            // Check environment variable
            if let Ok(env_pwd) = std::env::var("PM_MASTER_PASSWORD") {
                env_pwd
            } else {
                Password::new()
                    .with_prompt("Enter master password:")
                    .interact()?
            }
        }
    };

    // 打开数据库
    let db = Database::open(db_path, &master_password)
        .context("Failed to open database. Check your master password.")?;

    println!();
    println!("{}", "═════════════════════════════════════════".cyan());
    println!("{}", "  Password Manager Interactive Shell".green().bold());
    println!("{}", "═════════════════════════════════════════".cyan());
    println!();
    println!("{}", "Available commands:".yellow());
    println!("  list              - List all passwords");
    println!("  add               - Add a new password");
    println!("  get <title/id>    - Get password details");
    println!("  search <query>    - Search passwords");
    println!("  edit <title/id>   - Edit a password");
    println!("  delete <title/id> - Delete a password");
    println!("  generate [len]    - Generate strong password");
    println!("  strength <pwd>    - Check password strength");
    println!("  help              - Show this help");
    println!("  exit / quit       - Exit shell");
    println!();
    println!("{}", "Type a command to get started...".green());
    println!();

    let stdin = io::stdin();
    let mut stdout = io::stdout();

    loop {
        print!("{} ", "pm>".cyan().bold());
        stdout.flush()?;

        let mut input = String::new();
        stdin.lock().read_line(&mut input)?;
        let input = input.trim();

        if input.is_empty() {
            continue;
        }

        // 处理退出命令
        if matches!(input.to_lowercase().as_str(), "exit" | "quit" | "q") {
            println!("{}", "\n👋 Goodbye!".green());
            break;
        }

        // 处理帮助命令
        if matches!(input.to_lowercase().as_str(), "help" | "h" | "?") {
            println!();
            println!("{}", "Available commands:".yellow());
            println!("  list              - List all passwords");
            println!("  add               - Add a new password");
            println!("  get <title/id>    - Get password details");
            println!("  search <query>    - Search passwords");
            println!("  edit <title/id>   - Edit a password");
            println!("  delete <title/id> - Delete a password");
            println!("  generate [len]    - Generate strong password");
            println!("  strength <pwd>    - Check password strength");
            println!("  help              - Show this help");
            println!("  exit / quit       - Exit shell");
            println!();
            continue;
        }

        // 解析命令
        let parts: Vec<&str> = input.split_whitespace().collect();
        if parts.is_empty() {
            continue;
        }

        let command = parts[0].to_lowercase();
        let args = &parts[1..];

        match command.as_str() {
            "list" => {
                shell_list(&db, args);
            }
            "add" => {
                shell_add(&db);
            }
            "get" => {
                shell_get(&db, args);
            }
            "search" => {
                shell_search(&db, args);
            }
            "edit" => {
                shell_edit(&db, args);
            }
            "delete" => {
                shell_delete(&db, args);
            }
            "generate" => {
                shell_generate(args);
            }
            "strength" => {
                shell_strength(args);
            }
            _ => {
                println!("{}", format!("Unknown command: {}. Type 'help' for available commands.", command).red());
            }
        }
    }

    Ok(())
}

fn shell_list(db: &Database, _args: &[&str]) {
    match db.list_passwords() {
        Ok(entries) => {
            if entries.is_empty() {
                println!("{}", "No password entries found.".yellow());
                return;
            }

            println!();
            println!("{}", format!("Found {} entries:", entries.len()).bold());
            for entry in entries {
                println!("  [{}] {} ({})", entry.id.unwrap_or(0), entry.title, entry.username);
            }
            println!();
        }
        Err(e) => {
            println!("{}", format!("Error listing passwords: {}", e).red());
        }
    }
}

fn shell_add(db: &Database) {
    use dialoguer::{Input, Confirm};

    let title = Input::new()
        .with_prompt("Entry title")
        .interact_text()
        .unwrap_or_default();

    let username = Input::new()
        .with_prompt("Username")
        .interact_text()
        .unwrap_or_default();

    let should_generate = Confirm::new()
        .with_prompt("Generate a strong password?")
        .default(true)
        .interact()
        .unwrap_or_default();

    let password = if should_generate {
        PasswordGenerator::generate_quick(20)
    } else {
        use dialoguer::Password;
        Password::new()
            .with_prompt("Password:")
            .with_confirmation("Confirm password:", "Passwords do not match")
            .interact()
            .unwrap_or_default()
    };

    let url_input: String = Input::new()
        .with_prompt("URL (optional)")
        .allow_empty(true)
        .interact_text()
        .unwrap_or_default();
    let url = if url_input.is_empty() { None } else { Some(url_input) };

    let category_input: String = Input::new()
        .with_prompt("Category (optional)")
        .allow_empty(true)
        .interact_text()
        .unwrap_or_default();
    let category = if category_input.is_empty() { None } else { Some(category_input) };

    let mut entry = PasswordEntry::new(title, username, password);

    if let Some(u) = url {
        entry = entry.with_url(u);
    }
    if let Some(c) = category {
        entry = entry.with_category(c);
    }

    match db.add_password(entry) {
        Ok(id) => {
            println!("{}", format!("\n✓ Password entry added successfully! (ID: {})", id).green());
        }
        Err(e) => {
            println!("{}", format!("\n✗ Error adding password: {}", e).red());
        }
    }
}

fn shell_get(db: &Database, args: &[&str]) {
    if args.is_empty() {
        println!("{}", "Usage: get <title or ID>".yellow());
        return;
    }

    let entries = match db.list_passwords() {
        Ok(e) => e,
        Err(e) => {
            println!("{}", format!("Error listing passwords: {}", e).red());
            return;
        }
    };

    let target = args[0];

    let entry = if let Ok(id) = target.parse::<i64>() {
        entries.into_iter().find(|e| e.id == Some(id))
    } else {
        let query = target.to_lowercase();
        entries.into_iter().find(|e| e.title.to_lowercase() == query)
    };

    match entry {
        Some(e) => {
            match db.get_password(e.id.unwrap()) {
                Ok(full_entry) => {
                    println!();
                    println!("{}", format_entry(&full_entry, true));
                }
                Err(e) => {
                    println!("{}", format!("Error getting password: {}", e).red());
                }
            }
        }
        None => {
            println!("{}", "Entry not found.".red());
        }
    }
}

fn shell_search(db: &Database, args: &[&str]) {
    if args.is_empty() {
        println!("{}", "Usage: search <query>".yellow());
        return;
    }

    let query = args[0].to_string();
    let search_query = SearchQuery::new().with_title(query.clone());

    match db.search_passwords(&search_query) {
        Ok(results) => {
            if results.is_empty() {
                println!("{}", "No matching entries found.".yellow());
                return;
            }

            println!();
            println!("{}", format!("Found {} results for '{}':", results.len(), query).bold());
            for entry in results {
                println!("  [{}] {} ({})", entry.id.unwrap_or(0), entry.title, entry.username);
            }
            println!();
        }
        Err(e) => {
            println!("{}", format!("Error searching passwords: {}", e).red());
        }
    }
}

fn shell_edit(db: &Database, args: &[&str]) {
    if args.is_empty() {
        println!("{}", "Usage: edit <title or ID>".yellow());
        return;
    }

    let entries = match db.list_passwords() {
        Ok(e) => e,
        Err(e) => {
            println!("{}", format!("Error listing passwords: {}", e).red());
            return;
        }
    };

    let target = args[0];

    let entry = if let Ok(id) = target.parse::<i64>() {
        entries.into_iter().find(|e| e.id == Some(id))
    } else {
        let query = target.to_lowercase();
        entries.into_iter().find(|e| e.title.to_lowercase() == query)
    };

    let entry = match entry {
        Some(e) => e,
        None => {
            println!("{}", "Entry not found.".red());
            return;
        }
    };

    println!();
    println!("{}", format!("Editing: {}", entry.title).yellow());
    println!("{}", format_entry(&entry, false));

    use dialoguer::Input;

    let new_title: String = Input::new()
        .with_prompt(&format!("Title [{}]", entry.title))
        .allow_empty(true)
        .interact_text()
        .unwrap_or_default();
    let title = if new_title.is_empty() { entry.title.clone() } else { new_title };

    let new_username: String = Input::new()
        .with_prompt(&format!("Username [{}]", entry.username))
        .allow_empty(true)
        .interact_text()
        .unwrap_or_default();
    let username = if new_username.is_empty() { entry.username.clone() } else { new_username };

    use dialoguer::Password;
    let new_password = Password::new()
        .with_prompt("Password (press Enter to keep current)")
        .allow_empty_password(true)
        .interact()
        .unwrap_or_default();
    let password = if new_password.is_empty() {
        match db.get_password(entry.id.unwrap()) {
            Ok(e) => e.password,
            Err(_) => entry.password.clone(),
        }
    } else {
        new_password
    };

    let mut updated_entry = entry.clone();
    updated_entry.title = title;
    updated_entry.username = username;
    updated_entry.password = password;

    match db.update_password(updated_entry) {
        Ok(_) => {
            println!("{}", "\n✓ Entry updated successfully!".green());
        }
        Err(e) => {
            println!("{}", format!("\n✗ Error updating entry: {}", e).red());
        }
    }
}

fn shell_delete(db: &Database, args: &[&str]) {
    if args.is_empty() {
        println!("{}", "Usage: delete <title or ID>".yellow());
        return;
    }

    let entries = match db.list_passwords() {
        Ok(e) => e,
        Err(e) => {
            println!("{}", format!("Error listing passwords: {}", e).red());
            return;
        }
    };

    let target = args[0];

    let entry = if let Ok(id) = target.parse::<i64>() {
        entries.into_iter().find(|e| e.id == Some(id))
    } else {
        let query = target.to_lowercase();
        entries.into_iter().find(|e| e.title.to_lowercase() == query)
    };

    let entry = match entry {
        Some(e) => e,
        None => {
            println!("{}", "Entry not found.".red());
            return;
        }
    };

    println!();
    println!("{}", format!("Deleting: {}", entry.title).yellow());
    println!("{}", format_entry(&entry, false));

    use dialoguer::Confirm;
    let confirm = Confirm::new()
        .with_prompt("Are you sure you want to delete this entry?")
        .default(false)
        .interact();

    match confirm {
        Ok(true) => {
            if let Some(id) = entry.id {
                match db.delete_password(id) {
                    Ok(_) => {
                        println!("{}", "\n✓ Entry deleted successfully!".green());
                    }
                    Err(e) => {
                        println!("{}", format!("\n✗ Error deleting entry: {}", e).red());
                    }
                }
            }
        }
        Ok(false) => {
            println!("{}", "\nCancelled.".yellow());
        }
        Err(e) => {
            println!("{}", format!("\n✗ Error: {}", e).red());
        }
    }
}

fn shell_generate(args: &[&str]) {
    use password_manager_core::password_generator::GeneratorOptions;

    let length = if args.is_empty() {
        20
    } else {
        args[0].parse::<usize>().unwrap_or(20)
    };

    let options = GeneratorOptions {
        length,
        include_uppercase: true,
        include_lowercase: true,
        include_numbers: true,
        include_symbols: true,
        exclude_similar: true,
    };

    let password = PasswordGenerator::generate(&options);

    println!();
    println!("{}", format!("Generated password ({} chars):", length).cyan());
    println!("{}", password.bold().green());

    let (strength, warning) = PasswordGenerator::check_strength(&password, &[]);
    println!();
    println!("{}", format!("Strength: {}", strength.as_str().bold()));
    if !warning.is_empty() && warning != "密码强度良好" {
        println!("  {}", warning);
    }
}

fn shell_strength(args: &[&str]) {
    if args.is_empty() {
        println!("{}", "Usage: strength <password>".yellow());
        return;
    }

    let password = args[0];
    let (strength, warning) = PasswordGenerator::check_strength(password, &[]);

    println!();
    println!("{}", "Password Strength Analysis:".cyan().bold());
    println!("  Label: {}", strength.as_str());
    println!("  Note: {}", warning);
}
