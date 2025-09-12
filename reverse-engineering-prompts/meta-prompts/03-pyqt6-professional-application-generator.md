# PyQt6 Professional Application Generator Meta-Prompt

## Overview
This meta-prompt generates comprehensive reproduction prompts for creating professional desktop applications using PyQt6. Based on MAP4's sophisticated GUI architecture with tab-based interfaces, real-time progress tracking, professional themes, and responsive layouts.

## Meta-Prompt Template

### PyQt6 Application Configuration Parameters
Configure your professional desktop application:

```yaml
# PyQt6 Professional Application Configuration
APPLICATION_CONFIG:
  app_name: "{APP_NAME}"                         # e.g., "Data Analyzer Pro", "Media Manager"
  app_type: "{APP_TYPE}"                         # "ANALYSIS", "MEDIA", "PRODUCTIVITY", "DEVELOPMENT"
  complexity: "{COMPLEXITY}"                     # "BASIC", "INTERMEDIATE", "ADVANCED", "PROFESSIONAL"
  window_size: [{DEFAULT_WIDTH}, {DEFAULT_HEIGHT}] # [1200, 800]

INTERFACE_FEATURES:
  tab_based_interface: {TAB_INTERFACE}           # true/false
  real_time_updates: {REAL_TIME_UPDATES}         # true/false
  progress_tracking: {PROGRESS_TRACKING}         # true/false
  status_bar: {STATUS_BAR}                       # true/false
  menu_bar: {MENU_BAR}                          # true/false
  toolbar: {TOOLBAR}                            # true/false
  drag_drop: {DRAG_DROP}                        # true/false

THEMING:
  theme_system: {THEME_SYSTEM}                   # true/false
  default_theme: "{DEFAULT_THEME}"               # "DARK", "LIGHT", "AUTO"
  custom_styling: {CUSTOM_STYLING}               # true/false
  responsive_layout: {RESPONSIVE_LAYOUT}         # true/false

DATA_DISPLAY:
  table_widget: {TABLE_WIDGET}                   # true/false
  tree_widget: {TREE_WIDGET}                    # true/false
  list_widget: {LIST_WIDGET}                    # true/false
  graphics_view: {GRAPHICS_VIEW}                 # true/false
  custom_widgets: {CUSTOM_WIDGETS}               # true/false

INTERACTIONS:
  file_dialogs: {FILE_DIALOGS}                   # true/false
  context_menus: {CONTEXT_MENUS}                 # true/false
  keyboard_shortcuts: {KEYBOARD_SHORTCUTS}       # true/false
  notifications: {NOTIFICATIONS}                 # true/false

THREADING:
  background_processing: {BACKGROUND_PROCESSING} # true/false
  progress_dialogs: {PROGRESS_DIALOGS}           # true/false
  worker_threads: {WORKER_THREADS}               # true/false
  async_operations: {ASYNC_OPERATIONS}           # true/false

ARCHITECTURE:
  mvc_pattern: {MVC_PATTERN}                     # true/false
  plugin_system: {PLUGIN_SYSTEM}                # true/false
  settings_management: {SETTINGS_MANAGEMENT}     # true/false
  state_persistence: {STATE_PERSISTENCE}         # true/false
```

## Generated PyQt6 Application Template

Based on the configuration, this meta-prompt generates:

---

# {APP_NAME} - Professional PyQt6 Desktop Application

## Application Overview
Create a {COMPLEXITY}-level desktop application using PyQt6 for {APP_TYPE} purposes with professional interface design, responsive layouts, and modern user experience patterns.

### Key Features
{#if TAB_INTERFACE}
- **Tab-Based Interface**: Organized multi-panel interface with intuitive navigation
{/if}
{#if REAL_TIME_UPDATES}
- **Real-Time Updates**: Live data updates with signal/slot architecture
{/if}
{#if PROGRESS_TRACKING}
- **Progress Tracking**: Visual progress indicators for long-running operations
{/if}
{#if THEME_SYSTEM}
- **Professional Theming**: Dark/light themes with consistent styling
{/if}
{#if BACKGROUND_PROCESSING}
- **Background Processing**: Non-blocking operations with worker threads
{/if}

## Core Application Architecture

### 1. Main Application Structure
Create the foundation application framework:

```python
"""
{APP_NAME} - Main Application
Professional PyQt6 Desktop Application
"""

import sys
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    {#if TAB_INTERFACE}QTabWidget, {/if}
    {#if TABLE_WIDGET}QTableWidget, QTableWidgetItem, QHeaderView, {/if}
    {#if TREE_WIDGET}QTreeWidget, QTreeWidgetItem, {/if}
    {#if LIST_WIDGET}QListWidget, QListWidgetItem, {/if}
    {#if PROGRESS_TRACKING}QProgressBar, {/if}
    {#if STATUS_BAR}QStatusBar, {/if}
    {#if MENU_BAR}QMenuBar, QMenu, {/if}
    {#if TOOLBAR}QToolBar, {/if}
    QPushButton, QLabel, QLineEdit, QTextEdit, QSplitter,
    {#if FILE_DIALOGS}QFileDialog, {/if}
    {#if PROGRESS_DIALOGS}QProgressDialog, {/if}
    {#if NOTIFICATIONS}QMessageBox, QSystemTrayIcon, {/if}
    QFrame, QGroupBox, QScrollArea
)

from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSettings, QSize, QPoint,
    {#if ASYNC_OPERATIONS}QRunnable, QThreadPool, {/if}
    {#if DRAG_DROP}QMimeData, {/if}
    QObject, QEvent
)

from PyQt6.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QAction,
    {#if KEYBOARD_SHORTCUTS}QShortcut, QKeySequence, {/if}
    {#if DRAG_DROP}QDragEnterEvent, QDropEvent, {/if}
    QPainter, QBrush, QPen
)

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class {APP_NAME.replace(' ', '').replace('-', '')}MainWindow(QMainWindow):
    """Main application window for {APP_NAME}."""
    
    # Custom signals for inter-component communication
    {#if REAL_TIME_UPDATES}
    data_updated = pyqtSignal(dict)
    status_changed = pyqtSignal(str)
    {/if}
    {#if PROGRESS_TRACKING}
    progress_updated = pyqtSignal(int, str)
    operation_completed = pyqtSignal(bool, str)
    {/if}
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        # Application state
        self.current_data = {}
        self.processing_tasks = []
        {#if SETTINGS_MANAGEMENT}
        self.settings = QSettings("{APP_NAME}", "MainWindow")
        {/if}
        {#if WORKER_THREADS}
        self.worker_threads = []
        {/if}
        {#if ASYNC_OPERATIONS}
        self.thread_pool = QThreadPool()
        {/if}
        
        # Initialize UI components
        self.setup_window()
        {#if THEME_SYSTEM}
        self.setup_theme()
        {/if}
        self.setup_ui()
        {#if KEYBOARD_SHORTCUTS}
        self.setup_shortcuts()
        {/if}
        self.setup_connections()
        
        {#if STATE_PERSISTENCE}
        # Restore previous state
        self.restore_state()
        {/if}
        
        logger.info(f"{APP_NAME} initialized successfully")
    
    def setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("{APP_NAME}")
        self.setMinimumSize({DEFAULT_WIDTH//2}, {DEFAULT_HEIGHT//2})
        self.resize({DEFAULT_WIDTH}, {DEFAULT_HEIGHT})
        
        # Center window on screen
        self.center_window()
        
        # Set application icon
        if os.path.exists("assets/icon.png"):
            self.setWindowIcon(QIcon("assets/icon.png"))
    
    def center_window(self):
        """Center window on screen."""
        screen = QApplication.primaryScreen().availableGeometry()
        window = self.frameGeometry()
        center = screen.center()
        window.moveCenter(center)
        self.move(window.topLeft())
    
    {#if THEME_SYSTEM}
    def setup_theme(self):
        """Apply professional theme styling."""
        if "{DEFAULT_THEME}" == "DARK":
            self.apply_dark_theme()
        elif "{DEFAULT_THEME}" == "LIGHT":
            self.apply_light_theme()
        else:
            # Auto theme based on system
            self.apply_auto_theme()
    
    def apply_dark_theme(self):
        """Apply professional dark theme."""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3c3c3c;
                top: -1px;
            }
            
            QTabBar::tab {
                background-color: #4a4a4a;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #0078d4;
                border-bottom: 2px solid #0078d4;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #5a5a5a;
            }
            
            /* Tables */
            QTableWidget {
                background-color: #3c3c3c;
                alternate-background-color: #454545;
                gridline-color: #555555;
                selection-background-color: #0078d4;
                border: 1px solid #555555;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #4a4a4a;
                color: white;
                padding: 8px;
                border: 1px solid #555555;
                font-weight: bold;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #0078d4;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #106ebe;
            }
            
            QPushButton:pressed {
                background-color: #005a9e;
            }
            
            QPushButton:disabled {
                background-color: #6a6a6a;
                color: #aaaaaa;
            }
            
            /* Secondary Buttons */
            QPushButton.secondary {
                background-color: #6a6a6a;
                color: white;
            }
            
            QPushButton.secondary:hover {
                background-color: #7a7a7a;
            }
            
            /* Input Fields */
            QLineEdit, QTextEdit {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                padding: 8px;
                border-radius: 4px;
                color: white;
                selection-background-color: #0078d4;
            }
            
            QLineEdit:focus, QTextEdit:focus {
                border-color: #0078d4;
                background-color: #3c3c3c;
            }
            
            /* Progress Bars */
            QProgressBar {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #3c3c3c;
                border-top: 1px solid #555555;
                color: white;
            }
            
            /* Menu Bar */
            QMenuBar {
                background-color: #3c3c3c;
                color: white;
                border-bottom: 1px solid #555555;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            
            QMenuBar::item:selected {
                background-color: #0078d4;
            }
            
            /* Menus */
            QMenu {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: white;
            }
            
            QMenu::item {
                padding: 6px 20px;
            }
            
            QMenu::item:selected {
                background-color: #0078d4;
            }
            
            /* Tool Bar */
            QToolBar {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                spacing: 2px;
                padding: 4px;
            }
            
            QToolBar::separator {
                background-color: #666666;
                width: 1px;
                margin: 0 4px;
            }
            
            /* Splitters */
            QSplitter::handle {
                background-color: #555555;
                border: 1px solid #666666;
            }
            
            QSplitter::handle:horizontal {
                width: 6px;
            }
            
            QSplitter::handle:vertical {
                height: 6px;
            }
            
            /* Scroll Areas */
            QScrollArea {
                background-color: #3c3c3c;
                border: 1px solid #555555;
            }
            
            /* Group Boxes */
            QGroupBox {
                font-weight: bold;
                border: 1px solid #666666;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
                color: #0078d4;
            }
        """)
    
    def apply_light_theme(self):
        """Apply professional light theme."""
        self.setStyleSheet("""
            /* Light theme styles - simplified for brevity */
            QMainWindow {
                background-color: #ffffff;
                color: #000000;
            }
            
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #f8f8f8;
            }
            
            QTabBar::tab {
                background-color: #e8e8e8;
                color: #000000;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: white;
            }
            
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
        """)
    
    def apply_auto_theme(self):
        """Apply theme based on system settings."""
        # For simplicity, default to dark theme
        # In practice, would detect system theme
        self.apply_dark_theme()
    {/if}
    
    def setup_ui(self):
        """Setup main user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        {#if TAB_INTERFACE}
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_tabs()
        {/if}
        {#if not TAB_INTERFACE}
        # Single panel interface
        content_widget = self.create_main_content()
        main_layout.addWidget(content_widget)
        {/if}
        
        {#if STATUS_BAR}
        # Setup status bar
        self.setup_status_bar()
        {/if}
        
        {#if MENU_BAR}
        # Setup menu bar
        self.setup_menu_bar()
        {/if}
        
        {#if TOOLBAR}
        # Setup toolbar
        self.setup_toolbar()
        {/if}
    
    {#if TAB_INTERFACE}
    def setup_tabs(self):
        """Setup tab-based interface."""
        {#if APP_TYPE == "ANALYSIS"}
        # Data tab
        data_tab = self.create_data_tab()
        self.tab_widget.addTab(data_tab, "Data")
        
        # Analysis tab
        analysis_tab = self.create_analysis_tab()
        self.tab_widget.addTab(analysis_tab, "Analysis")
        
        # Results tab
        results_tab = self.create_results_tab()
        self.tab_widget.addTab(results_tab, "Results")
        {/if}
        
        {#if APP_TYPE == "MEDIA"}
        # Library tab
        library_tab = self.create_library_tab()
        self.tab_widget.addTab(library_tab, "Library")
        
        # Player tab
        player_tab = self.create_player_tab()
        self.tab_widget.addTab(player_tab, "Player")
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(settings_tab, "Settings")
        {/if}
        
        {#if APP_TYPE == "PRODUCTIVITY"}
        # Workspace tab
        workspace_tab = self.create_workspace_tab()
        self.tab_widget.addTab(workspace_tab, "Workspace")
        
        # Tools tab
        tools_tab = self.create_tools_tab()
        self.tab_widget.addTab(tools_tab, "Tools")
        
        # Reports tab
        reports_tab = self.create_reports_tab()
        self.tab_widget.addTab(reports_tab, "Reports")
        {/if}
        
        {#if APP_TYPE == "DEVELOPMENT"}
        # Editor tab
        editor_tab = self.create_editor_tab()
        self.tab_widget.addTab(editor_tab, "Editor")
        
        # Console tab
        console_tab = self.create_console_tab()
        self.tab_widget.addTab(console_tab, "Console")
        
        # Debug tab
        debug_tab = self.create_debug_tab()
        self.tab_widget.addTab(debug_tab, "Debug")
        {/if}
        
        # Connect tab change events
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    {/if}
    
    {#if TABLE_WIDGET}
    def create_data_table(self) -> QTableWidget:
        """Create professional data table widget."""
        table = QTableWidget()
        
        # Configure table properties
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        table.setSortingEnabled(True)
        table.setShowGrid(True)
        
        # Configure headers
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.verticalHeader().setVisible(False)
        
        # Enable drag and drop if configured
        {#if DRAG_DROP}
        table.setDragDropMode(QTableWidget.DragDropMode.DropOnly)
        table.setAcceptDrops(True)
        {/if}
        
        return table
    {/if}
    
    {#if TREE_WIDGET}
    def create_tree_view(self) -> QTreeWidget:
        """Create tree widget for hierarchical data."""
        tree = QTreeWidget()
        
        # Configure tree properties
        tree.setHeaderHidden(False)
        tree.setRootIsDecorated(True)
        tree.setAlternatingRowColors(True)
        tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        
        return tree
    {/if}
    
    {#if PROGRESS_TRACKING}
    def create_progress_panel(self) -> QWidget:
        """Create progress tracking panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("Ready")
        layout.addWidget(self.progress_label)
        
        return panel
    {/if}
    
    {#if STATUS_BAR}
    def setup_status_bar(self):
        """Setup application status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        {#if PROGRESS_TRACKING}
        # Progress bar in status bar
        self.status_progress = QProgressBar()
        self.status_progress.setMaximumWidth(200)
        self.status_progress.setVisible(False)
        self.status_bar.addPermanentWidget(self.status_progress)
        {/if}
        
        # Connection status
        self.connection_label = QLabel("Disconnected")
        self.status_bar.addPermanentWidget(self.connection_label)
        
        # Show initial status
        self.status_bar.showMessage("Application initialized")
    {/if}
    
    {#if MENU_BAR}
    def setup_menu_bar(self):
        """Setup application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # New action
        new_action = QAction('New', self)
        {#if KEYBOARD_SHORTCUTS}
        new_action.setShortcut('Ctrl+N')
        {/if}
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        # Open action
        open_action = QAction('Open', self)
        {#if KEYBOARD_SHORTCUTS}
        open_action.setShortcut('Ctrl+O')
        {/if}
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Save action
        save_action = QAction('Save', self)
        {#if KEYBOARD_SHORTCUTS}
        save_action.setShortcut('Ctrl+S')
        {/if}
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self)
        {#if KEYBOARD_SHORTCUTS}
        exit_action.setShortcut('Ctrl+Q')
        {/if}
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        {#if THEME_SYSTEM}
        # Theme submenu
        theme_menu = view_menu.addMenu('Theme')
        
        dark_theme_action = QAction('Dark', self)
        dark_theme_action.triggered.connect(lambda: self.apply_dark_theme())
        theme_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction('Light', self)
        light_theme_action.triggered.connect(lambda: self.apply_light_theme())
        theme_menu.addAction(light_theme_action)
        {/if}
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    {/if}
    
    {#if TOOLBAR}
    def setup_toolbar(self):
        """Setup application toolbar."""
        toolbar = self.addToolBar('Main')
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # New action
        new_action = toolbar.addAction('New')
        new_action.triggered.connect(self.new_file)
        
        # Open action
        open_action = toolbar.addAction('Open')
        open_action.triggered.connect(self.open_file)
        
        # Save action
        save_action = toolbar.addAction('Save')
        save_action.triggered.connect(self.save_file)
        
        toolbar.addSeparator()
        
        {#if BACKGROUND_PROCESSING}
        # Process action
        process_action = toolbar.addAction('Process')
        process_action.triggered.connect(self.start_processing)
        {/if}
        
        {#if THEME_SYSTEM}
        toolbar.addSeparator()
        
        # Theme toggle
        theme_action = toolbar.addAction('Toggle Theme')
        theme_action.triggered.connect(self.toggle_theme)
        {/if}
    {/if}
    
    {#if KEYBOARD_SHORTCUTS}
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Application shortcuts
        shortcuts = {
            'Ctrl+N': self.new_file,
            'Ctrl+O': self.open_file,
            'Ctrl+S': self.save_file,
            'Ctrl+Q': self.close,
            'F11': self.toggle_fullscreen,
            'Ctrl+R': self.refresh_data,
            {#if BACKGROUND_PROCESSING}
            'F5': self.start_processing,
            'Esc': self.cancel_processing,
            {/if}
        }
        
        for key, func in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(func)
    {/if}
    
    def setup_connections(self):
        """Setup signal/slot connections."""
        {#if REAL_TIME_UPDATES}
        # Connect real-time update signals
        self.data_updated.connect(self.on_data_updated)
        self.status_changed.connect(self.on_status_changed)
        {/if}
        
        {#if PROGRESS_TRACKING}
        # Connect progress signals
        self.progress_updated.connect(self.on_progress_updated)
        self.operation_completed.connect(self.on_operation_completed)
        {/if}
    
    # Event handlers
    {#if TAB_INTERFACE}
    def on_tab_changed(self, index: int):
        """Handle tab change event."""
        tab_name = self.tab_widget.tabText(index)
        logger.info(f"Switched to tab: {tab_name}")
        {#if STATUS_BAR}
        self.status_bar.showMessage(f"Active tab: {tab_name}")
        {/if}
    {/if}
    
    {#if REAL_TIME_UPDATES}
    def on_data_updated(self, data: dict):
        """Handle data update event."""
        self.current_data.update(data)
        self.refresh_displays()
        logger.debug(f"Data updated: {len(data)} items")
    
    def on_status_changed(self, status: str):
        """Handle status change event."""
        {#if STATUS_BAR}
        self.status_bar.showMessage(status)
        {/if}
        logger.info(f"Status: {status}")
    {/if}
    
    {#if PROGRESS_TRACKING}
    def on_progress_updated(self, percentage: int, message: str):
        """Handle progress update event."""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(percentage)
        
        {#if STATUS_BAR}
        if hasattr(self, 'status_progress'):
            self.status_progress.setVisible(True)
            self.status_progress.setValue(percentage)
        
        self.status_bar.showMessage(message)
        {/if}
        
        if hasattr(self, 'progress_label'):
            self.progress_label.setText(message)
    
    def on_operation_completed(self, success: bool, message: str):
        """Handle operation completion event."""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
        
        {#if STATUS_BAR}
        if hasattr(self, 'status_progress'):
            self.status_progress.setVisible(False)
        
        status_message = "✓ " + message if success else "✗ " + message
        self.status_bar.showMessage(status_message)
        {/if}
        
        {#if NOTIFICATIONS}
        # Show notification
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)
        {/if}
        
        logger.info(f"Operation completed - Success: {success}, Message: {message}")
    {/if}
    
    {#if DRAG_DROP}
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        files = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        if files:
            self.handle_dropped_files(files)
            event.acceptProposedAction()
    
    def handle_dropped_files(self, files: List[str]):
        """Process dropped files."""
        logger.info(f"Files dropped: {files}")
        # Implementation specific to application type
        pass
    {/if}
    
    # Action handlers
    def new_file(self):
        """Create new file/project."""
        logger.info("New file action triggered")
        # Implementation specific to application
        pass
    
    {#if FILE_DIALOGS}
    def open_file(self):
        """Open file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def save_file(self):
        """Save file dialog."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "All Files (*)"
        )
        
        if file_path:
            self.save_to_file(file_path)
    {/if}
    {#if not FILE_DIALOGS}
    def open_file(self):
        """Open file placeholder."""
        logger.info("Open file action triggered")
        pass
    
    def save_file(self):
        """Save file placeholder."""
        logger.info("Save file action triggered")
        pass
    {/if}
    
    {#if BACKGROUND_PROCESSING}
    def start_processing(self):
        """Start background processing."""
        if self.processing_tasks:
            logger.warning("Processing already in progress")
            return
        
        # Create and start worker thread
        worker = ProcessingWorker(self.current_data)
        {#if PROGRESS_TRACKING}
        worker.progress_updated.connect(self.progress_updated)
        {/if}
        worker.finished.connect(self.on_processing_finished)
        worker.error.connect(self.on_processing_error)
        
        {#if WORKER_THREADS}
        self.worker_threads.append(worker)
        {/if}
        worker.start()
        
        logger.info("Background processing started")
    
    def cancel_processing(self):
        """Cancel background processing."""
        {#if WORKER_THREADS}
        for worker in self.worker_threads:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        self.worker_threads.clear()
        {/if}
        
        self.operation_completed.emit(False, "Processing cancelled")
        logger.info("Background processing cancelled")
    
    def on_processing_finished(self, results: dict):
        """Handle processing completion."""
        self.operation_completed.emit(True, f"Processing completed: {len(results)} items")
        self.current_data.update(results)
        self.refresh_displays()
    
    def on_processing_error(self, error: str):
        """Handle processing error."""
        self.operation_completed.emit(False, f"Processing error: {error}")
        logger.error(f"Processing error: {error}")
    {/if}
    
    {#if THEME_SYSTEM}
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        # Simple theme toggle - in practice, would track current theme
        self.apply_dark_theme()  # or light based on current state
    {/if}
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def refresh_data(self):
        """Refresh application data."""
        logger.info("Refreshing data")
        self.refresh_displays()
    
    def refresh_displays(self):
        """Refresh all display components."""
        # Implementation specific to application
        logger.debug("Displays refreshed")
    
    def show_about(self):
        """Show about dialog."""
        {#if NOTIFICATIONS}
        QMessageBox.about(
            self,
            "About {APP_NAME}",
            f"""
            <h3>{APP_NAME}</h3>
            <p>Professional desktop application built with PyQt6</p>
            <p>Version 1.0</p>
            <p>Built with Python and PyQt6</p>
            """
        )
        {/if}
    
    def load_file(self, file_path: str):
        """Load file into application."""
        logger.info(f"Loading file: {file_path}")
        # Implementation specific to application
        pass
    
    def save_to_file(self, file_path: str):
        """Save data to file."""
        logger.info(f"Saving to file: {file_path}")
        # Implementation specific to application
        pass
    
    {#if STATE_PERSISTENCE}
    def restore_state(self):
        """Restore application state from settings."""
        if hasattr(self, 'settings'):
            # Restore window geometry
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
            
            # Restore window state
            state = self.settings.value("windowState")
            if state:
                self.restoreState(state)
            
            {#if TAB_INTERFACE}
            # Restore last active tab
            last_tab = self.settings.value("lastTab", 0, type=int)
            if hasattr(self, 'tab_widget'):
                self.tab_widget.setCurrentIndex(last_tab)
            {/if}
    
    def save_state(self):
        """Save application state to settings."""
        if hasattr(self, 'settings'):
            # Save window geometry
            self.settings.setValue("geometry", self.saveGeometry())
            
            # Save window state
            self.settings.setValue("windowState", self.saveState())
            
            {#if TAB_INTERFACE}
            # Save current tab
            if hasattr(self, 'tab_widget'):
                self.settings.setValue("lastTab", self.tab_widget.currentIndex())
            {/if}
    {/if}
    
    # Window event handlers
    def closeEvent(self, event):
        """Handle window close event."""
        {#if STATE_PERSISTENCE}
        # Save state before closing
        self.save_state()
        {/if}
        
        {#if BACKGROUND_PROCESSING}
        # Cancel any running tasks
        self.cancel_processing()
        {/if}
        
        logger.info("Application closing")
        event.accept()

{#if BACKGROUND_PROCESSING}
class ProcessingWorker(QThread):
    """Worker thread for background processing."""
    
    {#if PROGRESS_TRACKING}
    progress_updated = pyqtSignal(int, str)
    {/if}
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, data: dict):
        super().__init__()
        self.data = data
    
    def run(self):
        """Run background processing."""
        try:
            results = {}
            total_items = len(self.data)
            
            for i, (key, value) in enumerate(self.data.items()):
                # Simulate processing
                self.msleep(100)  # Simulate work
                
                # Process item
                processed_value = self.process_item(key, value)
                results[key] = processed_value
                
                {#if PROGRESS_TRACKING}
                # Update progress
                progress = int((i + 1) / total_items * 100)
                self.progress_updated.emit(progress, f"Processing {key}...")
                {/if}
            
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def process_item(self, key: str, value: Any) -> Any:
        """Process individual item - override in subclasses."""
        return value  # Placeholder processing
{/if}

def main():
    """Main application entry point."""
    # Create application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("{APP_NAME}")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Your Company")
    
    # Create and show main window
    window = {APP_NAME.replace(' ', '').replace('-', '')}MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
```

## Project Structure

```
{APP_NAME.lower().replace(' ', '_').replace('-', '_')}/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main application
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main window class
│   │   ├── widgets/            # Custom widgets
│   │   │   ├── __init__.py
│   │   │   ├── custom_table.py
│   │   │   ├── progress_panel.py
│   │   │   └── data_display.py
│   │   {#if THEME_SYSTEM}
│   │   └── themes.py           # Theme management
│   │   {/if}
│   ├── core/
│   │   ├── __init__.py
│   │   ├── application.py      # Application logic
│   │   ├── data_manager.py     # Data management
│   │   {#if BACKGROUND_PROCESSING}
│   │   └── workers.py          # Background workers
│   │   {/if}
│   {#if SETTINGS_MANAGEMENT}
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Settings management
│   {/if}
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py          # Utility functions
│       └── constants.py        # Application constants
├── assets/
│   ├── icons/                  # Application icons
│   ├── images/                 # Images and graphics
│   {#if THEME_SYSTEM}
│   └── themes/                 # Theme resources
│   {/if}
├── tests/
│   ├── __init__.py
│   ├── test_main_window.py
│   └── test_workers.py
├── requirements.txt
├── setup.py
└── README.md
```

## Dependencies

```txt
# Core PyQt6
PyQt6>=6.4.0

{#if SETTINGS_MANAGEMENT}
# Configuration
PyQt6.QtCore
{/if}

{#if BACKGROUND_PROCESSING}
# Threading
PyQt6.QtCore
{/if}

# Additional utilities (based on application type)
{#if APP_TYPE == "ANALYSIS"}
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
{/if}

{#if APP_TYPE == "MEDIA"}
mutagen>=1.45.0
{/if}

{#if APP_TYPE == "DEVELOPMENT"}
pygments>=2.10.0
{/if}
```

## Configuration Template

```yaml
# {APP_NAME} Configuration

application:
  name: "{APP_NAME}"
  version: "1.0.0"
  window_size: [{DEFAULT_WIDTH}, {DEFAULT_HEIGHT}]
  {#if THEME_SYSTEM}
  default_theme: "{DEFAULT_THEME}"
  {/if}

{#if SETTINGS_MANAGEMENT}
ui:
  {#if TAB_INTERFACE}
  default_tab: 0
  {/if}
  {#if PROGRESS_TRACKING}
  show_progress_in_statusbar: true
  {/if}
  {#if KEYBOARD_SHORTCUTS}
  enable_shortcuts: true
  {/if}

{#if STATE_PERSISTENCE}
persistence:
  save_window_state: true
  save_user_preferences: true
{/if}
{/if}

{#if BACKGROUND_PROCESSING}
processing:
  max_workers: 4
  timeout: 30  # seconds
{/if}

{#if NOTIFICATIONS}
notifications:
  show_system_tray: false
  show_message_boxes: true
{/fi}
```

## Usage Examples

### Basic Application
```python
# Create simple analysis application
app = QApplication(sys.argv)
window = DataAnalyzerMainWindow()
window.show()
sys.exit(app.exec())
```

### With Custom Theme
```python
# Apply custom theme
window = MediaManagerMainWindow()
window.apply_dark_theme()
window.show()
```

### Background Processing
```python
# Start background task
worker = ProcessingWorker(data)
worker.progress_updated.connect(window.on_progress_updated)
worker.finished.connect(window.on_processing_finished)
worker.start()
```

## Validation Criteria

A successful implementation should demonstrate:

1. **Professional Interface**: Modern, responsive PyQt6 interface
2. **Theme System**: Consistent dark/light theme support
3. **Real-time Updates**: Non-blocking UI with progress indicators
4. **Robust Architecture**: Clean separation of UI and business logic
5. **User Experience**: Intuitive navigation and feedback
6. **Performance**: Smooth operation with background processing

---

*Generated by PyQt6 Professional Application Generator Meta-Prompt*
*Version 1.0 - Based on MAP4 GUI Architecture*