#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{
    CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu,
    SystemTrayMenuItem, WindowEvent,
};
use once_cell::sync::Lazy;
use parking_lot::Mutex;
use std::sync::Arc;

static PET_SIZE: Lazy<Arc<Mutex<i32>>> = Lazy::new(|| Arc::new(Mutex::new(200)));

fn build_tray_menu() -> SystemTrayMenu {
    let resize = CustomMenuItem::new("resize".to_string(), "设置大小...");
    let quit = CustomMenuItem::new("quit".to_string(), "退出");
    SystemTrayMenu::new()
        .add_item(resize)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit)
}

#[tauri::command]
fn get_pet_size() -> i32 {
    *PET_SIZE.lock()
}

#[tauri::command]
fn set_pet_size(app_handle: tauri::AppHandle, size: i32) {
    let s = size.clamp(100, 500);
    *PET_SIZE.lock() = s;
    if let Some(win) = app_handle.get_window("main") {
        let _ = win.set_size(tauri::LogicalSize::new(s as f64, s as f64));
    }
}

fn main() {
    let tray = SystemTray::new().with_menu(build_tray_menu());

    tauri::Builder::default()
        .system_tray(tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "quit" => {
                    std::process::exit(0);
                }
                "resize" => {
                    if let Some(win) = app.get_window("main") {
                        let _ = win.emit("resize-dialog", ());
                    }
                }
                _ => {}
            },
            SystemTrayEvent::LeftClick { .. } => {
                if let Some(win) = app.get_window("main") {
                    let _ = win.show();
                    let _ = win.set_focus();
                }
            }
            _ => {}
        })
        .on_window_event(|event| {
            if let WindowEvent::CloseRequested { .. } = event.event() {
                // Hide instead of close on window close
                if let Some(win) = event.window().get_window("main") {
                    let _ = win.hide();
                }
                event.prevent_close();
            }
        })
        .invoke_handler(tauri::generate_handler![get_pet_size, set_pet_size])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
