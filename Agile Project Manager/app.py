import wx
import wx.dataview
import time
import threading
import json
import os
from datetime import datetime, timedelta

# -------------------------------------------------------------------------
# OFFLINE TEMPLATE LOGIC
# -------------------------------------------------------------------------

TEMPLATES = {
    "scrum": {
        "name": "Scrum Software Project",
        "description": "Agile development with sprints, backlog, and reviews.",
        "management_type": "scrum",
        "phases": [
            ("Product Backlog", "List of all desired features", [
                ("User Story Creation", 3, "Product Owner",
                 [("Interview Users", 1), ("Define Acceptance Criteria", 1), ("Prioritize", 1)]),
                ("Backlog Refinement", 2, "Scrum Master", [])
            ]),
            ("Sprint Planning", "Plan for next sprint", [
                ("Sprint Goal Definition", 1, "Product Owner", []),
                ("Task Breakdown", 2, "Development Team", [("Estimate Effort", 1), ("Assign Points", 1)])
            ]),
            ("Sprint 1 (2 weeks)", "First development sprint", [
                ("Sprint Backlog Setup", 1, "Scrum Master", []),
                ("Daily Standups", 10, "Team", []),
                ("Feature Development", 8, "Dev Team", [("Frontend", 4), ("Backend", 4)]),
                ("Unit Testing", 4, "QA", [])
            ]),
            ("Sprint Review", "Demo to stakeholders", [
                ("Demo Preparation", 1, "Team", []),
                ("Stakeholder Demo", 1, "Product Owner", []),
                ("Feedback Collection", 1, "Scrum Master", [])
            ]),
            ("Sprint Retrospective", "Process improvement", [
                ("What Went Well", 1, "Team", []),
                ("Improvement Actions", 1, "Scrum Master", [])
            ]),
            ("Sprint 2 (2 weeks)", "Second development sprint", [
                ("Sprint Planning", 1, "Team", []),
                ("Feature Development", 8, "Dev Team", []),
                ("Integration Testing", 4, "QA", []),
                ("Bug Fixing", 3, "Team", [])
            ]),
            ("Release Preparation", "Final release activities", [
                ("Final Testing", 3, "QA", []),
                ("Documentation", 2, "Tech Writer", []),
                ("Deployment", 1, "DevOps", [])
            ])
        ]
    },
    "kanban": {
        "name": "Kanban Workflow Project",
        "description": "Continuous flow with WIP limits and cycle time focus.",
        "management_type": "kanban",
        "phases": [
            ("Backlog", "Pool of requested work", [
                ("Request Intake", 2, "Product Manager", [("Triage Requests", 1), ("Initial Assessment", 1)]),
                ("Value Analysis", 3, "Business Analyst", []),
                ("Ready for Dev", 1, "Team Lead", [])
            ]),
            ("Analysis & Design", "Detailed requirements", [
                ("Detailed Analysis", 3, "Business Analyst", []),
                ("Technical Design", 2, "Senior Dev", []),
                ("Design Review", 1, "Architect", [])
            ]),
            ("Development", "Implementation", [
                ("Coding", 5, "Developer", []),
                ("Code Review", 2, "Peer", []),
                ("Unit Tests", 2, "Developer", [])
            ]),
            ("Testing", "Quality assurance", [
                ("Integration Testing", 3, "QA Engineer", []),
                ("User Acceptance", 2, "Business User", []),
                ("Bug Fixing", 2, "Developer", [])
            ]),
            ("Deployment", "Release to production", [
                ("Deployment Prep", 1, "DevOps", []),
                ("Production Deploy", 1, "DevOps", []),
                ("Post-Deploy Check", 1, "Support", [])
            ]),
            ("Done", "Completed work", [
                ("Documentation", 1, "Tech Writer", []),
                ("Lessons Learned", 1, "Team", [])
            ])
        ]
    },
    "waterfall": {
        "name": "Traditional Waterfall Project",
        "description": "Sequential phases with formal handoffs.",
        "management_type": "waterfall",
        "phases": [
            ("Requirements", "Gathering needs", [
                ("Stakeholder Interviews", 5, "PM", [("Prep", 1), ("Interview", 3), ("Review", 1)]),
                ("Spec Document", 7, "PM", [])
            ]),
            ("Design", "System architecture", [
                ("UI Mockups", 5, "Designer", [("Wireframes", 2), ("Hi-Fi", 3)]),
                ("DB Schema", 3, "DBA", [])
            ]),
            ("Implementation", "Coding", [
                ("Backend Setup", 5, "Backend Team", []),
                ("API Development", 10, "Backend Team", []),
                ("Frontend", 10, "Frontend Team", [])
            ]),
            ("Testing", "Quality assurance", [
                ("Code Reviews", 3, "Tech Lead", []),
                ("Unit Testing", 5, "Dev Team", []),
                ("Integration Testing", 5, "QA", [])
            ]),
            ("Deployment", "Go live", [
                ("UAT", 5, "Stakeholders", []),
                ("Production Deploy", 1, "DevOps", []),
                ("User Training", 2, "PM", [])
            ]),
            ("Maintenance", "Support", [
                ("Monitoring", 1, "DevOps", []),
                ("Bug Fixes", 3, "Support Team", [])
            ])
        ]
    }
}

PROJECT_TYPES = ["Software Development", "Marketing Campaign", "Construction", "Event Planning", "Research Project",
                 "Product Launch"]


def generate_offline_plan(prompt, project_type="scrum", custom_type="Software Development"):
    prompt = prompt.lower()

    # Determine methodology based on prompt or use selected
    if any(x in prompt for x in ['scrum', 'sprint', 'agile', 'backlog']):
        key = 'scrum'
    elif any(x in prompt for x in ['kanban', 'flow', 'wip', 'continuous']):
        key = 'kanban'
    elif any(x in prompt for x in ['waterfall', 'sequential', 'traditional']):
        key = 'waterfall'
    else:
        key = project_type.lower() if isinstance(project_type, str) else 'scrum'

    # Use the selected template
    if key not in TEMPLATES:
        key = 'scrum'

    data = TEMPLATES[key]

    # Customize name based on project type
    project_name = f"{custom_type} Project" if custom_type else data["name"]

    project_data = {
        "name": project_name,
        "description": f"{data['description']} - {prompt}",
        "management_type": data["management_type"],
        "project_type": custom_type,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "phases": []
    }

    for p_name, p_desc, tasks in data["phases"]:
        phase_tasks = []
        for t in tasks:
            title, duration, assignee, sub_raw = t
            subtasks_list = []
            sub_duration_sum = 0
            for st in sub_raw:
                subtasks_list.append({"title": st[0], "durationDays": st[1]})
                sub_duration_sum += st[1]

            final_duration = sub_duration_sum if subtasks_list else duration
            phase_tasks.append({
                "title": title,
                "durationDays": final_duration,
                "assignee": assignee,
                "subtasks": subtasks_list
            })

        phase_obj = {
            "name": p_name,
            "description": p_desc,
            "tasks": phase_tasks
        }
        project_data["phases"].append(phase_obj)

    return project_data


# -------------------------------------------------------------------------
# DATA MODELS
# -------------------------------------------------------------------------
class Subtask:
    def __init__(self, title, duration, completed=False):
        self.title = title
        self.duration = duration
        self.completed = completed

    def to_dict(self):
        return {
            "title": self.title,
            "durationDays": self.duration,
            "completed": self.completed
        }


class Task:
    def __init__(self, title, duration, assignee="Unassigned", completed=False):
        self.title = title
        self.duration = duration
        self.assignee = assignee
        self.completed = completed
        self.subtasks = []
        self.priority = "Medium"  # Added for Kanban/Scrum
        self.status = "Todo"  # Added for Kanban/Scrum

    def to_dict(self):
        return {
            "title": self.title,
            "durationDays": self.duration,
            "assignee": self.assignee,
            "completed": self.completed,
            "priority": self.priority,
            "status": self.status,
            "subtasks": [s.to_dict() for s in self.subtasks]
        }


class Phase:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.tasks = []
        self.wip_limit = None  # For Kanban phases

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "wip_limit": self.wip_limit,
            "tasks": [t.to_dict() for t in self.tasks]
        }


class Project:
    def __init__(self, name="New Project", description=""):
        self.name = name
        self.description = description
        self.phases = []
        self.management_type = "scrum"  # scrum, kanban, or waterfall
        self.project_type = "Software Development"
        self.created_date = datetime.now().strftime("%Y-%m-%d")
        self.sprint_length = 14  # For Scrum
        self.wip_limits = {}  # For Kanban

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "management_type": self.management_type,
            "project_type": self.project_type,
            "created_date": self.created_date,
            "sprint_length": self.sprint_length,
            "wip_limits": self.wip_limits,
            "phases": [p.to_dict() for p in self.phases]
        }


# -------------------------------------------------------------------------
# WORKER
# -------------------------------------------------------------------------
class OfflineWorker(threading.Thread):
    def __init__(self, prompt, project_type, custom_type, callback):
        threading.Thread.__init__(self)
        self.prompt = prompt
        self.project_type = project_type
        self.custom_type = custom_type
        self.callback = callback

    def run(self):
        time.sleep(0.5)
        try:
            data = generate_offline_plan(self.prompt, self.project_type, self.custom_type)
            self.callback(data, None)
        except Exception as e:
            self.callback(None, str(e))


# -------------------------------------------------------------------------
# WIZARD DIALOG - SIMPLIFIED VERSION
# -------------------------------------------------------------------------
class ProjectWizardDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title='Project Wizard', size=(500, 450))

        self.parent = parent

        self.init_ui()
        self.Center()

    def init_ui(self):
        # Main panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(45, 45, 48))

        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(panel, label="PROJECT WIZARD")
        title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(wx.Colour(64, 169, 255))
        main_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        # Description
        desc = wx.StaticText(panel, label="Describe your project idea:")
        desc.SetForegroundColour(wx.Colour(200, 200, 200))
        main_sizer.Add(desc, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Text input for project description
        self.txt_prompt = wx.TextCtrl(panel, value="", style=wx.TE_MULTILINE, size=(-1, 100))
        self.txt_prompt.SetBackgroundColour(wx.Colour(60, 60, 60))
        self.txt_prompt.SetForegroundColour(wx.WHITE)
        main_sizer.Add(self.txt_prompt, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Project type
        type_label = wx.StaticText(panel, label="Project Type:")
        type_label.SetForegroundColour(wx.Colour(200, 200, 200))
        main_sizer.Add(type_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.cbo_project_type = wx.ComboBox(panel, choices=PROJECT_TYPES, value="Software Development",
                                            style=wx.CB_READONLY)
        self.cbo_project_type.SetBackgroundColour(wx.Colour(60, 60, 60))
        self.cbo_project_type.SetForegroundColour(wx.WHITE)
        main_sizer.Add(self.cbo_project_type, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Methodology
        method_label = wx.StaticText(panel, label="Project Methodology:")
        method_label.SetForegroundColour(wx.Colour(200, 200, 200))
        main_sizer.Add(method_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Radio buttons in a horizontal sizer
        method_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rb_scrum = wx.RadioButton(panel, label="Scrum", style=wx.RB_GROUP)
        self.rb_kanban = wx.RadioButton(panel, label="Kanban")
        self.rb_waterfall = wx.RadioButton(panel, label="Waterfall")

        for rb in [self.rb_scrum, self.rb_kanban, self.rb_waterfall]:
            rb.SetForegroundColour(wx.WHITE)
            method_sizer.Add(rb, 1, wx.EXPAND | wx.RIGHT, 5)

        main_sizer.Add(method_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Methodology description
        self.lbl_method_desc = wx.StaticText(panel, label="Scrum: Iterative sprints with reviews and retrospectives")
        self.lbl_method_desc.SetForegroundColour(wx.Colour(150, 150, 150))
        self.lbl_method_desc.Wrap(450)
        main_sizer.Add(self.lbl_method_desc, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Button sizer at the bottom
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer(1)

        self.btn_cancel = wx.Button(panel, wx.ID_CANCEL, "Cancel", size=(100, 30))
        self.btn_generate = wx.Button(panel, wx.ID_OK, "Generate Project", size=(120, 30))
        self.btn_generate.SetBackgroundColour(wx.Colour(64, 169, 255))
        self.btn_generate.SetForegroundColour(wx.WHITE)

        button_sizer.Add(self.btn_cancel, 0, wx.RIGHT, 10)
        button_sizer.Add(self.btn_generate, 0)

        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 15)

        # Set sizer
        panel.SetSizer(main_sizer)

        # Bind events
        self.Bind(wx.EVT_RADIOBUTTON, self.on_methodology_changed, self.rb_scrum)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_methodology_changed, self.rb_kanban)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_methodology_changed, self.rb_waterfall)

        # Set default
        self.rb_scrum.SetValue(True)

    def on_methodology_changed(self, event):
        if self.rb_scrum.GetValue():
            self.lbl_method_desc.SetLabel(
                "Scrum: Iterative sprints with reviews and retrospectives. Best for projects with changing requirements.")
        elif self.rb_kanban.GetValue():
            self.lbl_method_desc.SetLabel(
                "Kanban: Continuous flow with visual workflow. Best for maintenance and support projects.")
        else:
            self.lbl_method_desc.SetLabel(
                "Waterfall: Sequential phases with formal handoffs. Best for projects with fixed requirements.")

    def get_values(self):
        """Get the values from the dialog"""
        return {
            "prompt": self.txt_prompt.GetValue().strip(),
            "project_type": "scrum" if self.rb_scrum.GetValue() else "kanban" if self.rb_kanban.GetValue() else "waterfall",
            "custom_type": self.cbo_project_type.GetValue()
        }


# -------------------------------------------------------------------------
# MAIN FRAME - DARK THEME
# -------------------------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='AgileFlow Project Manager', size=(1000, 800))

        # -- Theme Colors (Dracula/Dark Inspired) --
        self.col_bg_main = wx.Colour(30, 30, 30)
        self.col_bg_panel = wx.Colour(45, 45, 48)
        self.col_fg_text = wx.Colour(220, 220, 220)
        self.col_accent = wx.Colour(64, 169, 255)
        self.col_scrum = wx.Colour(86, 179, 103)  # Green for Scrum
        self.col_kanban = wx.Colour(255, 149, 0)  # Orange for Kanban
        self.col_waterfall = wx.Colour(175, 82, 222)  # Purple for Waterfall
        self.col_danger = wx.Colour(255, 85, 85)
        self.col_input_bg = wx.Colour(60, 60, 60)

        self.project = None
        self.current_phase = None
        self.row_map = {}

        # Create menu FIRST, before init_ui
        self.create_menu()

        self.init_ui()
        self.Center()

    def create_menu(self):
        # -- Menus --
        menubar = wx.MenuBar()

        # File Menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, '&New Project\tCtrl+N', 'Start fresh')
        file_menu.Append(wx.ID_OPEN, '&Open Project...\tCtrl+O', 'Open JSON file')
        file_menu.Append(wx.ID_SAVE, '&Save Project...\tCtrl+S', 'Save to JSON')
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, 'E&xit', 'Quit')
        menubar.Append(file_menu, '&File')

        # Tools Menu
        tools_menu = wx.Menu()
        self.wizard_id = wx.NewId()
        tools_menu.Append(self.wizard_id, '&Project Wizard...\tCtrl+W', 'Generate plan from description')

        # Add methodology switching
        self.method_menu = wx.Menu()
        self.scrum_id = wx.NewId()
        self.kanban_id = wx.NewId()
        self.waterfall_id = wx.NewId()
        self.method_menu.AppendRadioItem(self.scrum_id, 'Switch to &Scrum')
        self.method_menu.AppendRadioItem(self.kanban_id, 'Switch to &Kanban')
        self.method_menu.AppendRadioItem(self.waterfall_id, 'Switch to &Waterfall')
        tools_menu.AppendSubMenu(self.method_menu, 'Switch &Methodology')

        menubar.Append(tools_menu, '&Tools')

        # Set the menu bar
        self.SetMenuBar(menubar)

        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_new_project, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.on_save_project, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_open_project, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_generate, id=self.wizard_id)
        self.Bind(wx.EVT_MENU, self.on_switch_scrum, id=self.scrum_id)
        self.Bind(wx.EVT_MENU, self.on_switch_kanban, id=self.kanban_id)
        self.Bind(wx.EVT_MENU, self.on_switch_waterfall, id=self.waterfall_id)

    def init_ui(self):
        self.SetBackgroundColour(self.col_bg_main)

        # -- Main Sizer --
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # -- Header Panel --
        self.header_panel = wx.Panel(self)
        self.header_panel.SetBackgroundColour(self.col_bg_panel)
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Project Info
        self.lbl_project_name = wx.StaticText(self.header_panel, label="No Project Loaded")
        self.lbl_project_name.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.lbl_project_name.SetForegroundColour(self.col_accent)

        self.lbl_methodology = wx.StaticText(self.header_panel, label="")
        self.lbl_methodology.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        self.lbl_project_type = wx.StaticText(self.header_panel, label="")
        self.lbl_project_type.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.lbl_project_type.SetForegroundColour(wx.Colour(150, 150, 150))

        info_sizer = wx.BoxSizer(wx.VERTICAL)
        info_sizer.Add(self.lbl_project_name, 0, wx.BOTTOM, 2)
        info_sizer.Add(self.lbl_methodology, 0, wx.BOTTOM, 2)
        info_sizer.Add(self.lbl_project_type, 0)

        header_sizer.Add(info_sizer, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)

        # Stats
        stats_sizer = wx.BoxSizer(wx.VERTICAL)
        self.lbl_stats = wx.StaticText(self.header_panel, label="Tasks: 0 | Completed: 0 | Progress: 0%")
        self.lbl_stats.SetForegroundColour(wx.Colour(180, 180, 180))
        stats_sizer.Add(self.lbl_stats, 0, wx.ALIGN_RIGHT)

        header_sizer.Add(stats_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)
        self.header_panel.SetSizer(header_sizer)

        main_sizer.Add(self.header_panel, 0, wx.EXPAND)

        # -- Splitter --
        self.splitter = wx.SplitterWindow(self, style=wx.SP_3D | wx.SP_LIVE_UPDATE | wx.SP_NOBORDER)
        self.splitter.SetBackgroundColour(self.col_bg_main)

        # --- LEFT PANEL: Tree ---
        self.tree_panel = wx.Panel(self.splitter)
        self.tree_panel.SetBackgroundColour(self.col_bg_panel)

        tree_sizer = wx.BoxSizer(wx.VERTICAL)
        lbl_tree = wx.StaticText(self.tree_panel, label=" PROJECT BOARD")
        lbl_tree.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        lbl_tree.SetForegroundColour(wx.Colour(150, 150, 150))

        self.tree = wx.TreeCtrl(self.tree_panel,
                                style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_ROW_LINES | wx.BORDER_NONE)
        self.tree.SetBackgroundColour(self.col_bg_panel)
        self.tree.SetForegroundColour(self.col_fg_text)

        self.root = self.tree.AddRoot("Root")
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_phase_selected, self.tree)

        tree_sizer.Add(lbl_tree, 0, wx.ALL, 15)
        tree_sizer.Add(self.tree, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.tree_panel.SetSizer(tree_sizer)

        # --- RIGHT PANEL: Content ---
        self.right_panel = wx.Panel(self.splitter)
        self.right_panel.SetBackgroundColour(self.col_bg_main)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Phase Header Area
        self.phase_header_panel = wx.Panel(self.right_panel)
        self.phase_header_panel.SetBackgroundColour(self.col_bg_main)
        phase_header_sizer = wx.BoxSizer(wx.VERTICAL)

        self.lbl_phase_name = wx.StaticText(self.phase_header_panel, label="Select a phase from the left")
        self.lbl_phase_name.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.lbl_phase_name.SetForegroundColour(self.col_accent)

        self.lbl_phase_desc = wx.StaticText(self.phase_header_panel, label="...")
        self.lbl_phase_desc.SetForegroundColour(wx.Colour(180, 180, 180))

        phase_header_sizer.Add(self.lbl_phase_name, 0, wx.BOTTOM, 5)
        phase_header_sizer.Add(self.lbl_phase_desc, 0, wx.EXPAND)
        self.phase_header_panel.SetSizer(phase_header_sizer)

        # Task List (DataViewListCtrl) - Enhanced for Scrum/Kanban
        self.task_list = wx.dataview.DataViewListCtrl(self.right_panel, style=wx.BORDER_NONE)
        self.task_list.SetBackgroundColour(wx.Colour(40, 40, 40))
        self.task_list.SetForegroundColour(self.col_fg_text)

        # Enhanced Columns for Agile
        self.task_list.AppendToggleColumn("✔", width=40, mode=wx.dataview.DATAVIEW_CELL_ACTIVATABLE)
        self.task_list.AppendTextColumn("Task / Subtask", width=350)
        self.task_list.AppendTextColumn("Status", width=100)
        self.task_list.AppendTextColumn("Priority", width=80)
        self.task_list.AppendTextColumn("Duration", width=80)
        self.task_list.AppendTextColumn("Assignee", width=150)

        self.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self.on_list_selection, self.task_list)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_list_double_click, self.task_list)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_VALUE_CHANGED, self.on_item_value_changed, self.task_list)

        # -- Controls Panel (Bottom) --
        self.controls_panel = wx.Panel(self.right_panel)
        self.controls_panel.SetBackgroundColour(wx.Colour(50, 50, 50))
        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)

        def make_lbl(label):
            t = wx.StaticText(self.controls_panel, label=label)
            t.SetForegroundColour(self.col_fg_text)
            return t

        self.txt_title = wx.TextCtrl(self.controls_panel, value="", size=(200, -1), style=wx.BORDER_SIMPLE)
        self.txt_title.SetBackgroundColour(self.col_input_bg)
        self.txt_title.SetForegroundColour(self.col_fg_text)
        self.txt_title.SetHint("Task Title")

        # Priority dropdown
        self.cbo_priority = wx.ComboBox(self.controls_panel, value="Medium", choices=["High", "Medium", "Low"],
                                        size=(80, -1), style=wx.CB_READONLY)
        self.cbo_priority.SetBackgroundColour(self.col_input_bg)
        self.cbo_priority.SetForegroundColour(self.col_fg_text)

        self.spin_dur = wx.SpinCtrl(self.controls_panel, value="1", min=1, max=365, size=(60, -1),
                                    style=wx.BORDER_SIMPLE)
        self.spin_dur.SetBackgroundColour(self.col_input_bg)
        self.spin_dur.SetForegroundColour(self.col_fg_text)

        self.txt_assignee = wx.TextCtrl(self.controls_panel, value="", size=(120, -1), style=wx.BORDER_SIMPLE)
        self.txt_assignee.SetBackgroundColour(self.col_input_bg)
        self.txt_assignee.SetForegroundColour(self.col_fg_text)
        self.txt_assignee.SetHint("Assignee")

        self.btn_add_task = wx.Button(self.controls_panel, label="+ Task")
        self.btn_add_task.SetBackgroundColour(self.col_accent)
        self.btn_add_task.SetForegroundColour(wx.WHITE)

        self.btn_add_sub = wx.Button(self.controls_panel, label="+ Subtask")
        self.btn_add_sub.Disable()

        self.btn_delete = wx.Button(self.controls_panel, label="Delete")
        self.btn_delete.SetBackgroundColour(self.col_danger)
        self.btn_delete.SetForegroundColour(wx.WHITE)
        self.btn_delete.Disable()

        self.Bind(wx.EVT_BUTTON, self.on_add_task, self.btn_add_task)
        self.Bind(wx.EVT_BUTTON, self.on_add_subtask, self.btn_add_sub)
        self.Bind(wx.EVT_BUTTON, self.on_delete_item, self.btn_delete)

        controls_sizer.Add(make_lbl("Title:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        controls_sizer.Add(self.txt_title, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        controls_sizer.Add(make_lbl("Priority:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        controls_sizer.Add(self.cbo_priority, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        controls_sizer.Add(make_lbl("Days:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        controls_sizer.Add(self.spin_dur, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        controls_sizer.Add(make_lbl("Who:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        controls_sizer.Add(self.txt_assignee, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        controls_sizer.Add(self.btn_add_task, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        controls_sizer.Add(self.btn_add_sub, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        controls_sizer.AddStretchSpacer(1)
        controls_sizer.Add(self.btn_delete, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        self.controls_panel.SetSizer(controls_sizer)

        self.right_sizer.Add(self.phase_header_panel, 0, wx.EXPAND | wx.ALL, 25)
        line = wx.StaticLine(self.right_panel)
        line.SetBackgroundColour(wx.Colour(60, 60, 60))
        self.right_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 25)
        self.right_sizer.Add(self.task_list, 1, wx.EXPAND | wx.ALL, 25)
        self.right_sizer.Add(self.controls_panel, 0, wx.EXPAND | wx.ALL, 0)
        self.right_panel.SetSizer(self.right_sizer)

        self.splitter.SplitVertically(self.tree_panel, self.right_panel, 300)
        self.splitter.SetMinimumPaneSize(200)

        main_sizer.Add(self.splitter, 1, wx.EXPAND)

        self.SetSizer(main_sizer)

        self.CreateStatusBar()
        self.SetStatusText("Ready - AgileFlow Project Manager")

        # Load default project
        self.create_default_project()

    def create_default_project(self):
        data = generate_offline_plan("Software Development using Scrum", "scrum", "Software Development")
        self.load_project_data(data, None)

    def update_header(self):
        if self.project:
            self.lbl_project_name.SetLabel(self.project.name)

            # Set methodology color
            if self.project.management_type == "scrum":
                color = self.col_scrum
                methodology_text = "Scrum Methodology"
            elif self.project.management_type == "kanban":
                color = self.col_kanban
                methodology_text = "Kanban Methodology"
            else:
                color = self.col_waterfall
                methodology_text = "Waterfall Methodology"

            self.lbl_methodology.SetLabel(methodology_text)
            self.lbl_methodology.SetForegroundColour(color)

            self.lbl_project_type.SetLabel(f"Type: {self.project.project_type}")

            # Update stats
            total_tasks = 0
            completed_tasks = 0
            for phase in self.project.phases:
                for task in phase.tasks:
                    total_tasks += 1
                    if task.completed:
                        completed_tasks += 1
                    total_tasks += len(task.subtasks)
                    completed_tasks += sum(1 for st in task.subtasks if st.completed)

            progress = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
            self.lbl_stats.SetLabel(f"Tasks: {total_tasks} | Completed: {completed_tasks} | Progress: {progress}%")

            # Update title
            self.SetTitle(f"{self.project.name} - AgileFlow ({self.project.management_type.capitalize()})")

    def on_exit(self, event):
        self.Close()

    def on_new_project(self, event):
        self.project = Project("Untitled Project", "Start by adding phases or using the Wizard.")
        self.project.management_type = "scrum"
        self.refresh_tree()
        self.update_header()
        self.lbl_phase_name.SetLabel("New Project")
        self.lbl_phase_desc.SetLabel("Empty project created.")
        self.task_list.DeleteAllItems()
        self.row_map = {}
        self.SetStatusText("New project created.")

    def on_save_project(self, event):
        if not self.project:
            wx.MessageBox("No active project to save.", "Nothing to Save", wx.OK | wx.ICON_WARNING)
            return

        # Create a proper file save dialog
        dlg = wx.FileDialog(
            self,
            message="Save project file",
            defaultDir=os.getcwd(),
            defaultFile=f"{self.project.name.replace(' ', '_')}.json",
            wildcard="JSON files (*.json)|*.json|All files (*.*)|*.*",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )

        if dlg.ShowModal() == wx.ID_OK:
            # Get the file path
            pathname = dlg.GetPath()

            # Ensure .json extension
            if not pathname.lower().endswith('.json'):
                pathname += '.json'

            try:
                # Save the project as JSON
                with open(pathname, 'w', encoding='utf-8') as f:
                    json.dump(self.project.to_dict(), f, indent=2, ensure_ascii=False)

                wx.MessageBox(f"Project saved successfully to:\n{pathname}",
                              "Save Successful", wx.OK | wx.ICON_INFORMATION)
                self.SetStatusText(f"Saved: {os.path.basename(pathname)}")

            except Exception as e:
                wx.MessageBox(f"Error saving file:\n{str(e)}",
                              "Save Error", wx.OK | wx.ICON_ERROR)

        dlg.Destroy()

    def on_open_project(self, event):
        # Create a proper file open dialog
        dlg = wx.FileDialog(
            self,
            message="Open project file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="JSON files (*.json)|*.json|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )

        if dlg.ShowModal() == wx.ID_OK:
            # Get the file path
            pathname = dlg.GetPath()

            try:
                # Load the JSON file
                with open(pathname, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Load the project data
                self.load_project_data(data, None)

                wx.MessageBox(f"Project loaded successfully:\n{os.path.basename(pathname)}",
                              "Load Successful", wx.OK | wx.ICON_INFORMATION)
                self.SetStatusText(f"Loaded: {os.path.basename(pathname)}")

            except Exception as e:
                wx.MessageBox(f"Error loading file:\n{str(e)}",
                              "Load Error", wx.OK | wx.ICON_ERROR)

        dlg.Destroy()

    def on_generate(self, event):
        dlg = ProjectWizardDialog(self)

        # Show the dialog
        result = dlg.ShowModal()

        if result == wx.ID_OK:
            # Get values from the dialog
            values = dlg.get_values()
            prompt = values["prompt"]
            project_type = values["project_type"]
            custom_type = values["custom_type"]

            if prompt:
                self.SetStatusText(f"Generating {project_type} plan...")
                worker = OfflineWorker(prompt.strip(), project_type, custom_type, self.on_wizard_complete)
                worker.start()
            else:
                wx.MessageBox("Please enter a project description.", "Empty Input", wx.OK | wx.ICON_INFORMATION)

        dlg.Destroy()

    def on_switch_scrum(self, event):
        if self.project:
            self.project.management_type = "scrum"
            self.update_header()
            self.SetStatusText("Switched to Scrum methodology")

    def on_switch_kanban(self, event):
        if self.project:
            self.project.management_type = "kanban"
            self.update_header()
            self.SetStatusText("Switched to Kanban methodology")

    def on_switch_waterfall(self, event):
        if self.project:
            self.project.management_type = "waterfall"
            self.update_header()
            self.SetStatusText("Switched to Waterfall methodology")

    def on_wizard_complete(self, data, error):
        wx.CallAfter(self.load_project_data, data, error)

    def load_project_data(self, data, error):
        if error:
            wx.MessageBox(f"Generation error: {error}", "Error", wx.ICON_ERROR)
            return
        if not data:
            wx.MessageBox("No data received.", "Error", wx.ICON_ERROR)
            return

        self.project = Project(data.get('name', 'Untitled'), data.get('description', ''))
        self.project.management_type = data.get('management_type', 'scrum')
        self.project.project_type = data.get('project_type', 'Software Development')
        self.project.created_date = data.get('created_date', datetime.now().strftime("%Y-%m-%d"))
        self.project.sprint_length = data.get('sprint_length', 14)
        self.project.wip_limits = data.get('wip_limits', {})

        for p_data in data.get('phases', []):
            phase = Phase(p_data.get('name'), p_data.get('description'))
            phase.wip_limit = p_data.get('wip_limit')
            for t_data in p_data.get('tasks', []):
                dur = t_data.get('durationDays', t_data.get('duration', 1))
                t = Task(
                    title=t_data.get('title', 'Untitled Task'),
                    duration=dur,
                    assignee=t_data.get('assignee', 'Unassigned'),
                    completed=t_data.get('completed', False)
                )
                t.priority = t_data.get('priority', 'Medium')
                t.status = t_data.get('status', 'Todo')
                for st_data in t_data.get('subtasks', []):
                    sdur = st_data.get('durationDays', st_data.get('duration', 1))
                    st = Subtask(
                        title=st_data.get('title', 'Untitled Subtask'),
                        duration=sdur,
                        completed=st_data.get('completed', False)
                    )
                    t.subtasks.append(st)
                phase.tasks.append(t)
            self.project.phases.append(phase)

        self.refresh_tree()
        self.update_header()

        if self.project.phases:
            first_item = self.tree.GetFirstChild(self.root)[0]
            if first_item.IsOk():
                self.tree.SelectItem(first_item)
        else:
            self.lbl_phase_name.SetLabel(self.project.name)
            self.lbl_phase_desc.SetLabel(self.project.description)
            self.task_list.DeleteAllItems()
            self.row_map = {}
        self.SetStatusText(f"Project loaded ({self.project.management_type.capitalize()})")

    def refresh_tree(self):
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot("Project")
        for phase in self.project.phases:
            # Add WIP limit to phase name if it exists (for Kanban)
            phase_name = phase.name
            if phase.wip_limit and self.project.management_type == "kanban":
                phase_name = f"{phase.name} (WIP: {phase.wip_limit})"
            self.tree.AppendItem(self.root, phase_name, data=phase)
        self.tree.ExpandAll()

    def on_phase_selected(self, event):
        item = event.GetItem()
        if not item.IsOk():
            return
        data = self.tree.GetItemData(item)
        if isinstance(data, Phase):
            self.current_phase = data
            self.lbl_phase_name.SetLabel(data.name)

            # Add methodology-specific description
            if self.project.management_type == "scrum" and "Sprint" in data.name:
                desc = f"{data.description} | Sprint Length: {self.project.sprint_length} days"
            elif self.project.management_type == "kanban" and data.wip_limit:
                desc = f"{data.description} | WIP Limit: {data.wip_limit}"
            else:
                desc = data.description

            self.lbl_phase_desc.SetLabel(desc)
            self.refresh_task_list()
        else:
            self.current_phase = None
            if self.project:
                self.lbl_phase_name.SetLabel(self.project.name)
                self.lbl_phase_desc.SetLabel(self.project.description)
            else:
                self.lbl_phase_name.SetLabel("No Project")
                self.lbl_phase_desc.SetLabel("")
            self.task_list.DeleteAllItems()
            self.row_map = {}

    def refresh_task_list(self):
        self.task_list.DeleteAllItems()
        self.row_map = {}
        idx = 0
        if not self.current_phase:
            return

        # Color coding based on priority
        for task in self.current_phase.tasks:
            self.task_list.AppendItem([
                task.completed,
                task.title,
                task.status,
                task.priority,
                str(task.duration),
                task.assignee
            ])
            self.row_map[idx] = {'type': 'task', 'obj': task}
            idx += 1

            for st in task.subtasks:
                self.task_list.AppendItem([
                    st.completed,
                    f"    ↳ {st.title}",
                    "",  # Subtasks don't have separate status
                    "",  # Subtasks inherit parent priority
                    str(st.duration),
                    ""
                ])
                self.row_map[idx] = {'type': 'subtask', 'obj': st, 'parent': task}
                idx += 1

        # Update stats after refresh
        self.update_header()

    def on_item_value_changed(self, event):
        item = event.GetItem()
        if not item.IsOk():
            return
        row = self.task_list.ItemToRow(item)
        if row == wx.NOT_FOUND or row not in self.row_map:
            return

        col = event.GetColumn()
        obj = self.row_map[row]['obj']

        if col == 0:  # Completed checkbox
            is_checked = self.task_list.GetValue(row, 0)
            obj.completed = bool(is_checked)
        elif col == 2:  # Status column
            new_status = self.task_list.GetValue(row, 2)
            if hasattr(obj, 'status'):
                obj.status = new_status
        elif col == 3:  # Priority column
            new_priority = self.task_list.GetValue(row, 3)
            if hasattr(obj, 'priority'):
                obj.priority = new_priority

        self.update_header()

    def on_list_selection(self, event):
        row = self.task_list.GetSelectedRow()
        has_sel = (row != wx.NOT_FOUND and row in self.row_map)
        self.btn_delete.Enable(has_sel)
        if has_sel:
            item_data = self.row_map[row]
            if item_data['type'] == 'task':
                self.btn_add_sub.Enable()
                self.btn_add_sub.SetLabel("+ Sub")
            else:
                self.btn_add_sub.Disable()
        else:
            self.btn_add_sub.Disable()
            self.btn_add_sub.SetLabel("+ Subtask")

    def on_list_double_click(self, event):
        row = self.task_list.GetSelectedRow()
        if row == wx.NOT_FOUND or row not in self.row_map:
            return
        item = self.row_map[row]
        obj = item['obj']

        if self.task_list.GetSelectedColumn() in [2, 3]:  # Status or Priority column
            # Create a dialog for editing status or priority
            col = self.task_list.GetSelectedColumn()
            if col == 2:  # Status
                choices = ["Todo", "In Progress", "Review", "Testing", "Done", "Blocked"]
                current = obj.status if hasattr(obj, 'status') else "Todo"
                label = "Status:"
            else:  # Priority
                choices = ["High", "Medium", "Low"]
                current = obj.priority if hasattr(obj, 'priority') else "Medium"
                label = "Priority:"

            dlg = wx.SingleChoiceDialog(self, label, "Edit", choices)
            dlg.SetSelection(choices.index(current) if current in choices else 0)

            if dlg.ShowModal() == wx.ID_OK:
                new_value = dlg.GetStringSelection()
                if col == 2:
                    if hasattr(obj, 'status'):
                        obj.status = new_value
                    self.task_list.SetValue(new_value, row, 2)
                else:
                    if hasattr(obj, 'priority'):
                        obj.priority = new_value
                    self.task_list.SetValue(new_value, row, 3)
            dlg.Destroy()
        else:  # Title column
            dlg = wx.TextEntryDialog(self, 'Rename:', 'Edit Item', obj.title)
            if dlg.ShowModal() == wx.ID_OK:
                new_title = dlg.GetValue().strip()
                if new_title:
                    obj.title = new_title
                    if item['type'] == 'task':
                        self.task_list.SetValue(new_title, row, 1)
                    else:
                        self.task_list.SetValue(f"    ↳ {new_title}", row, 1)
            dlg.Destroy()

    def on_add_task(self, event):
        if not self.current_phase:
            wx.MessageBox("Please select a phase from the left panel.", "No Phase Selected", wx.OK | wx.ICON_WARNING)
            return
        title = self.txt_title.GetValue().strip()
        if not title:
            wx.MessageBox("Task title cannot be empty.", "Invalid Input", wx.OK | wx.ICON_WARNING)
            return

        # Determine default status based on methodology
        if self.project.management_type == "kanban":
            default_status = "Backlog" if self.current_phase.name == "Backlog" else "Todo"
        elif self.project.management_type == "scrum":
            default_status = "Todo"
        else:
            default_status = "Todo"

        t = Task(
            title=title,
            duration=self.spin_dur.GetValue(),
            assignee=self.txt_assignee.GetValue().strip() or "Unassigned"
        )
        t.priority = self.cbo_priority.GetValue()
        t.status = default_status

        self.current_phase.tasks.append(t)
        self.txt_title.SetValue("")
        self.spin_dur.SetValue(1)
        self.txt_assignee.SetValue("")
        self.refresh_task_list()

    def on_add_subtask(self, event):
        row = self.task_list.GetSelectedRow()
        if row == wx.NOT_FOUND or row not in self.row_map:
            return
        item = self.row_map[row]
        if item['type'] != 'task':
            wx.MessageBox("Please select a main task to add a subtask.", "Invalid Selection", wx.OK | wx.ICON_WARNING)
            return
        title = self.txt_title.GetValue().strip()
        if not title:
            wx.MessageBox("Subtask title cannot be empty.", "Invalid Input", wx.OK | wx.ICON_WARNING)
            return
        parent_task = item['obj']
        st = Subtask(title, self.spin_dur.GetValue())
        parent_task.subtasks.append(st)
        self.txt_title.SetValue("")
        self.spin_dur.SetValue(1)
        self.refresh_task_list()

    def on_delete_item(self, event):
        row = self.task_list.GetSelectedRow()
        if row == wx.NOT_FOUND or row not in self.row_map:
            return
        if wx.MessageBox("Are you sure you want to delete this item?", "Confirm Delete",
                         wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) != wx.YES:
            return
        item = self.row_map[row]
        if item['type'] == 'task':
            if item['obj'] in self.current_phase.tasks:
                self.current_phase.tasks.remove(item['obj'])
        elif item['type'] == 'subtask':
            parent = item['parent']
            if item['obj'] in parent.subtasks:
                parent.subtasks.remove(item['obj'])
        self.refresh_task_list()


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()