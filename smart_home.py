
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from collections import deque


# ==================== COLORS ====================

BG = "#101827"
PANEL = "#192438"
PANEL_LIGHT = "#223149"
ACCENT = "#38BDF8"
TEXT = "#F1F5F9"
MUTED = "#9CAFC4"
GREEN = "#34D399"
RED = "#FB7185"
YELLOW = "#FBBF24"


# ==================== TREE NODE ====================

class Node:
    def __init__(self, name, node_type, status=None):
        self.name = name
        self.node_type = node_type
        self.status = status
        self.children = []


# ==================== SMART HOME MANAGER ====================

class SmartHomeManager:
    def __init__(self):
        self.root = Node("Smart Home Hub", "Hub")
        self.create_sample_home()

    def create_sample_home(self):
        living = Node("Living Room", "Room")
        bedroom = Node("Bedroom", "Room")
        kitchen = Node("Kitchen", "Room")

        self.root.children = [living, bedroom, kitchen]

        living.children = [
            Node("Smart Light", "Device", "ON"),
            Node("Smart TV", "Device", "OFF"),
            Node("Smart Fan", "Device", "OFF"),
        ]

        bedroom.children = [
            Node("Bedroom Light", "Device", "ON"),
            Node("Smart AC", "Device", "OFF"),
        ]

        kitchen.children = [
            Node("Smart Fridge", "Device", "ON"),
            Node("Smart Oven", "Device", "OFF"),
        ]

    def find_node(self, name, node=None):
        if node is None:
            node = self.root

        if node.name.casefold() == name.strip().casefold():
            return node

        for child in node.children:
            result = self.find_node(name, child)
            if result is not None:
                return result

        return None

    def add_room(self, name):
        name = name.strip()

        if not name:
            return False, "Room name cannot be empty."

        if self.find_node(name):
            return False, "A room or device with that name already exists."

        self.root.children.append(Node(name, "Room"))
        return True, f"Room '{name}' added successfully."

    def add_device(self, room_name, device_name):
        room_name = room_name.strip()
        device_name = device_name.strip()

        if not room_name or not device_name:
            return False, "Room and device names cannot be empty."

        room = self.find_node(room_name)

        if room is None or room.node_type != "Room":
            return False, "Select a valid existing room."

        if self.find_node(device_name):
            return False, "A room or device with that name already exists."

        room.children.append(Node(device_name, "Device", "OFF"))
        return True, f"Device '{device_name}' added successfully."

    def delete_node(self, node):
        """Delete a room or device from the tree; the central hub is protected."""
        if node is None:
            return False, "Select a room or device to delete."

        if node is self.root or node.node_type == "Hub":
            return False, "The Smart Home Hub is the root and cannot be deleted."

        # Find the parent and remove this node from its children list.
        def remove_from_parent(parent):
            for child in list(parent.children):
                if child is node:
                    parent.children.remove(child)
                    return True
                if remove_from_parent(child):
                    return True
            return False

        if remove_from_parent(self.root):
            if node.node_type == "Room":
                return True, (
                    f"Room '{node.name}' and its {len(node.children)} direct "
                    "device(s) were removed from the hierarchy."
                )
            return True, f"Device '{node.name}' deleted successfully."

        return False, "The selected node could not be found in the hierarchy."

    def toggle_device(self, node):
        if node is None or node.node_type != "Device":
            return False

        node.status = "OFF" if node.status == "ON" else "ON"
        return True

    def preorder(self, node, result):
        result.append(node)
        for child in node.children:
            self.preorder(child, result)

    def postorder(self, node, result):
        for child in node.children:
            self.postorder(child, result)
        result.append(node)

    def level_order(self, node):
        result = []
        queue = deque([node])

        while queue:
            current = queue.popleft()
            result.append(current)
            queue.extend(current.children)

        return result

    def get_statistics(self):
        rooms = 0
        devices = 0
        on_count = 0
        off_count = 0

        def count(node):
            nonlocal rooms, devices, on_count, off_count

            if node.node_type == "Room":
                rooms += 1
            elif node.node_type == "Device":
                devices += 1

                if node.status == "ON":
                    on_count += 1
                else:
                    off_count += 1

            for child in node.children:
                count(child)

        count(self.root)

        return {
            "rooms": rooms,
            "devices": devices,
            "on": on_count,
            "off": off_count,
        }


# ==================== GUI APPLICATION ====================

class SmartHomeApp:
    def __init__(self, root):
        self.root = root
        self.manager = SmartHomeManager()
        self.tree_nodes = {}

        self.root.title("Smart Home Device Hierarchy Manager")
        self.root.geometry("1120x740")
        self.root.minsize(900, 620)
        self.root.configure(bg=BG)

        self.setup_styles()
        self.build_ui()
        self.refresh_tree()
        self.update_statistics()

        self.log("Welcome! Smart Home Manager is ready.")
        self.log("Select a node to view its details.")

    def setup_styles(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background=PANEL,
            foreground=TEXT,
            fieldbackground=PANEL,
            rowheight=29,
            borderwidth=0,
            font=("Segoe UI", 10),
        )

        style.configure(
            "Treeview.Heading",
            background=PANEL_LIGHT,
            foreground=TEXT,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )

        style.map(
            "Treeview",
            background=[("selected", "#075985")],
            foreground=[("selected", "#FFFFFF")],
        )

        style.configure(
            "TCombobox",
            fieldbackground=PANEL_LIGHT,
            background=PANEL_LIGHT,
            foreground=TEXT,
        )

    def make_button(self, parent, label, command,
                    color=ACCENT, fg=BG):
        return tk.Button(
            parent,
            text=label,
            command=command,
            bg=color,
            fg=fg,
            activebackground=color,
            activeforeground=fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=9,
        )

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(18, 12))

        title_area = tk.Frame(header, bg=BG)
        title_area.pack(side="left", fill="x", expand=True)

        tk.Label(
            title_area,
            text="SMART HOME",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="Device Hierarchy Manager",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 23, "bold"),
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="IoT Simulation  •  General Tree  •  DFS & BFS",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(3, 0))

        self.make_button(
            header, "+ Add Room", self.add_room, GREEN
        ).pack(side="right", padx=(8, 0))

        # Statistics cards
        stats_frame = tk.Frame(self.root, bg=BG)
        stats_frame.pack(fill="x", padx=24, pady=(0, 14))

        self.stat_values = {}

        cards = [
            ("ROOMS", "rooms", ACCENT),
            ("TOTAL DEVICES", "devices", TEXT),
            ("DEVICES ON", "on", GREEN),
            ("DEVICES OFF", "off", RED),
        ]

        for title, key, color in cards:
            card = tk.Frame(stats_frame, bg=PANEL, padx=15, pady=12)
            card.pack(side="left", fill="x", expand=True, padx=(0, 8))

            tk.Label(
                card,
                text=title,
                bg=PANEL,
                fg=MUTED,
                font=("Segoe UI", 9, "bold"),
            ).pack(anchor="w")

            value = tk.Label(
                card,
                text="0",
                bg=PANEL,
                fg=color,
                font=("Segoe UI", 22, "bold"),
            )
            value.pack(anchor="w", pady=(4, 0))

            self.stat_values[key] = value

        # Main content
        content = tk.Frame(self.root, bg=BG)
        content.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        content.columnconfigure(0, weight=5)
        content.columnconfigure(1, weight=4)
        content.rowconfigure(0, weight=1)

        # Left panel: hierarchy
        left = tk.Frame(content, bg=PANEL, padx=14, pady=14)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        tk.Label(
            left,
            text="DEVICE HIERARCHY",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        tree_frame = tk.Frame(left, bg=PANEL)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("type", "status"),
            show="tree headings",
            selectmode="browse",
        )

        self.tree.heading("#0", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("status", text="Status")

        self.tree.column("#0", width=200, minwidth=130)
        self.tree.column("type", width=75, anchor="center")
        self.tree.column("status", width=70, anchor="center")

        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.tag_configure("hub", foreground=ACCENT)
        self.tree.tag_configure("room", foreground=YELLOW)
        self.tree.tag_configure("on", foreground=GREEN)
        self.tree.tag_configure("off", foreground=RED)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        left_buttons = tk.Frame(left, bg=PANEL)
        left_buttons.grid(row=2, column=0, sticky="ew", pady=(12, 0))

        self.make_button(
            left_buttons, "↻ Refresh", self.refresh_all, PANEL_LIGHT, TEXT
        ).pack(side="left", padx=(0, 6))

        self.make_button(
            left_buttons, "⌕ Search", self.search_node
        ).pack(side="left", padx=6)

        # Right panel
        right = tk.Frame(content, bg=PANEL, padx=16, pady=14)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(5, weight=1)

        tk.Label(
            right,
            text="DEVICE CONTROL",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.detail_name = tk.Label(
            right,
            text="Select a node",
            bg=PANEL,
            fg=ACCENT,
            font=("Segoe UI", 17, "bold"),
            wraplength=340,
        )
        self.detail_name.grid(
            row=1, column=0, sticky="w", pady=(12, 3)
        )

        self.detail_info = tk.Label(
            right,
            text="Choose a room or device from the tree.",
            bg=PANEL,
            fg=MUTED,
            justify="left",
            anchor="w",
            wraplength=340,
            font=("Segoe UI", 10),
        )
        self.detail_info.grid(
            row=2, column=0, sticky="ew", pady=(0, 12)
        )

        self.status_button = self.make_button(
            right, "Power ON / OFF",
            self.toggle_selected, GREEN
        )
        self.status_button.grid(
            row=3, column=0, sticky="ew", pady=(0, 12)
        )

        actions = tk.Frame(right, bg=PANEL)
        actions.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)

        self.make_button(
            actions, "+ Add Device", self.add_device
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=3)

        self.make_button(
            actions, "Statistics", self.show_statistics,
            PANEL_LIGHT, TEXT
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=3)

        self.delete_button = self.make_button(
            actions, "Delete Selected", self.delete_selected,
            RED, "#FFFFFF"
        )
        self.delete_button.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(6, 3)
        )
        self.delete_button.config(state="disabled")

        # Traversal and activity panel
        output_panel = tk.Frame(right, bg=PANEL_LIGHT, padx=10, pady=10)
        output_panel.grid(row=5, column=0, sticky="nsew")
        output_panel.columnconfigure(0, weight=1)
        output_panel.rowconfigure(2, weight=1)

        tk.Label(
            output_panel,
            text="TREE TRAVERSAL & ACTIVITY",
            bg=PANEL_LIGHT,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        traversal_frame = tk.Frame(output_panel, bg=PANEL_LIGHT)
        traversal_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.make_button(
            traversal_frame, "Preorder", 
            lambda: self.run_traversal("preorder"),
            PANEL, TEXT
        ).pack(side="left", expand=True, fill="x", padx=(0, 3))

        self.make_button(
            traversal_frame, "Postorder",
            lambda: self.run_traversal("postorder"),
            PANEL, TEXT
        ).pack(side="left", expand=True, fill="x", padx=3)

        self.make_button(
            traversal_frame, "Level-order",
            lambda: self.run_traversal("level"),
            PANEL, TEXT
        ).pack(side="left", expand=True, fill="x", padx=(3, 0))

        log_frame = tk.Frame(output_panel, bg=PANEL_LIGHT)
        log_frame.grid(row=2, column=0, sticky="nsew")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.output = tk.Text(
            log_frame,
            height=8,
            bg="#0D1523",
            fg="#D6E3F0",
            insertbackground=TEXT,
            relief="flat",
            wrap="word",
            font=("Consolas", 9),
            padx=10,
            pady=8,
            state="disabled",
        )

        output_scroll = ttk.Scrollbar(
            log_frame, orient="vertical",
            command=self.output.yview
        )
        self.output.configure(yscrollcommand=output_scroll.set)

        self.output.grid(row=0, column=0, sticky="nsew")
        output_scroll.grid(row=0, column=1, sticky="ns")

        # Footer
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=24, pady=(0, 12))

        tk.Label(
            footer,
            text="● SIMULATION MODE",
            bg=BG,
            fg=GREEN,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

        tk.Label(
            footer,
            text="Python  •  Tkinter  •  General Tree",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="right")

    # ==================== TREE DISPLAY ====================

    def refresh_tree(self):
        selected_node = self.get_selected_node()
        selected_name = selected_node.name if selected_node else None

        self.tree.delete(*self.tree.get_children())
        self.tree_nodes.clear()

        self.insert_node("", self.manager.root)

        self.tree.item(str(id(self.manager.root)), open=True)

        for child in self.manager.root.children:
            self.tree.item(str(id(child)), open=True)

        if selected_name:
            found = self.manager.find_node(selected_name)
            if found:
                iid = str(id(found))
                self.tree.selection_set(iid)
                self.tree.see(iid)

        self.update_statistics()
        self.on_select()

    def insert_node(self, parent_iid, node):
        iid = str(id(node))
        self.tree_nodes[iid] = node

        if node.node_type == "Device":
            icon = "💡" if node.status == "ON" else "○"
            tag = "on" if node.status == "ON" else "off"
            status = node.status
            label = f"{icon} {node.name}"
        elif node.node_type == "Hub":
            tag = "hub"
            status = "ONLINE*"
            label = "⌂ " + node.name
        else:
            tag = "room"
            status = "—"
            label = "▸ " + node.name

        self.tree.insert(
            parent_iid,
            "end",
            iid=iid,
            text=label,
            values=(node.node_type, status),
            tags=(tag,),
            open=True,
        )

        for child in node.children:
            self.insert_node(iid, child)

    def get_selected_node(self):
        selection = self.tree.selection()

        if not selection:
            return None

        return self.tree_nodes.get(selection[0])

    def on_select(self, event=None):
        node = self.get_selected_node()

        if node is None:
            self.detail_name.config(text="Select a node")
            self.detail_info.config(
                text="Choose a room or device from the tree."
            )
            self.status_button.config(
                state="disabled", text="Select a device first"
            )
            self.delete_button.config(state="disabled")
            return

        self.detail_name.config(text=node.name)
        # The root hub must never be deleted.
        self.delete_button.config(
            state="disabled" if node.node_type == "Hub" else "normal"
        )

        if node.node_type == "Device":
            info = (
                "Type: IoT Device\n"
                f"Status: {node.status}\n"
                "Control: Simulated locally"
            )
            self.status_button.config(
                state="normal",
                text=f"Turn {'OFF' if node.status == 'ON' else 'ON'}",
                bg=RED if node.status == "ON" else GREEN,
            )
        elif node.node_type == "Room":
            info = (
                "Type: Room\n"
                f"Devices and subnodes: {len(node.children)}"
            )
            self.status_button.config(
                state="disabled", text="Select a device first"
            )
        else:
            info = (
                "Type: Central Hub\n"
                f"Connected rooms: {len(node.children)}\n"
                "Root of the general tree"
            )
            self.status_button.config(
                state="disabled", text="Select a device first"
            )

        self.detail_info.config(text=info)

    # ==================== STATISTICS ====================

    def update_statistics(self):
        stats = self.manager.get_statistics()

        for key, value in stats.items():
            self.stat_values[key].config(text=str(value))

    def show_statistics(self):
        stats = self.manager.get_statistics()

        report = [
            "SMART HOME STATISTICS",
            "=====================",
            f"Total rooms: {stats['rooms']}",
            f"Total IoT devices: {stats['devices']}",
            f"Devices ON: {stats['on']}",
            f"Devices OFF: {stats['off']}",
        ]

        self.log("\n".join(report))

    # ==================== DEVICE ACTIONS ====================

    def add_room(self):
        name = simpledialog.askstring(
            "Add Room",
            "Enter the new room name:",
            parent=self.root,
        )

        if name is None:
            return

        success, message = self.manager.add_room(name)

        if success:
            self.refresh_tree()
            self.log(message)
            messagebox.showinfo("Success", message, parent=self.root)
        else:
            messagebox.showwarning(
                "Invalid Input", message, parent=self.root
            )

    def add_device(self):
        selected = self.get_selected_node()

        if selected and selected.node_type == "Room":
            default_room = selected.name
        else:
            default_room = None

        rooms = [
            node.name for node in self.manager.root.children
            if node.node_type == "Room"
        ]

        if not rooms:
            messagebox.showwarning(
                "No Rooms", "Add a room before adding a device.",
                parent=self.root
            )
            return

        room_name = simpledialog.askstring(
            "Add Device",
            "Enter the existing room name:\n" + ", ".join(rooms),
            initialvalue=default_room or "",
            parent=self.root,
        )

        if room_name is None:
            return

        device_name = simpledialog.askstring(
            "Add Device",
            "Enter the device name:",
            parent=self.root,
        )

        if device_name is None:
            return

        success, message = self.manager.add_device(
            room_name, device_name
        )

        if success:
            self.refresh_tree()
            self.log(message)
            messagebox.showinfo("Success", message, parent=self.root)
        else:
            messagebox.showwarning(
                "Invalid Input", message, parent=self.root
            )

    def delete_selected(self):
        node = self.get_selected_node()

        if node is None:
            messagebox.showwarning(
                "Select Room or Device",
                "Please select a room or device from the hierarchy first.",
                parent=self.root,
            )
            return

        if node is self.manager.root or node.node_type == "Hub":
            messagebox.showwarning(
                "Cannot Delete Hub",
                "The Smart Home Hub is the root node and cannot be deleted.",
                parent=self.root,
            )
            return

        if node.node_type == "Room":
            device_count = len(node.children)
            description = (
                f"Delete room '{node.name}' and all {device_count} "
                f"device(s) currently inside it?"
            )
        else:
            description = f"Delete device '{node.name}'?"

        confirmed = messagebox.askyesno(
            "Confirm Deletion",
            description + "\n\nThis action cannot be undone.",
            icon="warning",
            parent=self.root,
        )
        if not confirmed:
            return

        success, message = self.manager.delete_node(node)
        if success:
            self.refresh_tree()
            self.log(message)
            messagebox.showinfo("Deleted", message, parent=self.root)
        else:
            messagebox.showwarning(
                "Unable to Delete", message, parent=self.root
            )

    def toggle_selected(self):
        node = self.get_selected_node()

        if node is None or node.node_type != "Device":
            messagebox.showwarning(
                "Select Device",
                "Please select an IoT device first.",
                parent=self.root,
            )
            return

        self.manager.toggle_device(node)
        self.refresh_tree()

        self.tree.selection_set(str(id(node)))
        self.tree.see(str(id(node)))

        self.log(f"{node.name} status changed to {node.status}.")
        self.on_select()

    # ==================== SEARCH ====================

    def search_node(self):
        name = simpledialog.askstring(
            "Search",
            "Enter the room or device name:",
            parent=self.root,
        )

        if name is None:
            return

        if not name.strip():
            messagebox.showwarning(
                "Invalid Input", "Search name cannot be empty.",
                parent=self.root
            )
            return

        node = self.manager.find_node(name)

        if node is None:
            self.log(f"Search failed: '{name}' not found.")
            messagebox.showinfo(
                "Not Found", f"'{name}' was not found.",
                parent=self.root
            )
            return

        iid = str(id(node))
        self.tree.selection_set(iid)
        self.tree.see(iid)
        self.on_select()

        self.log(f"Found: {node.name} [{node.node_type}]")

    # ==================== TRAVERSAL ====================

    def run_traversal(self, method):
        result = []

        if method == "preorder":
            self.manager.preorder(self.manager.root, result)
            title = "PREORDER TRAVERSAL (DFS)"
        elif method == "postorder":
            self.manager.postorder(self.manager.root, result)
            title = "POSTORDER TRAVERSAL (DFS)"
        else:
            result = self.manager.level_order(self.manager.root)
            title = "LEVEL-ORDER TRAVERSAL (BFS)"

        lines = [title, "=" * len(title)]

        for index, node in enumerate(result, start=1):
            lines.append(
                f"{index:02d}. {node.name} [{node.node_type}]"
            )

        lines.append(f"\nTotal nodes visited: {len(result)}")

        self.log("\n".join(lines))

    # ==================== GENERAL ====================

    def refresh_all(self):
        self.refresh_tree()
        self.log("Hierarchy and statistics refreshed.")

    def log(self, message):
        self.output.config(state="normal")
        self.output.insert("end", message + "\n\n")
        self.output.see("end")
        self.output.config(state="disabled")


# ==================== START APPLICATION ====================

if __name__ == "__main__":
    window = tk.Tk()
    app = SmartHomeApp(window)
    window.mainloop()
