import customtkinter as ctk
import os
import shutil
import re
from tkinter import filedialog

# Appearance settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BulkSerialFileRenamerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bulk Serial File Renamer")
        self.geometry("750x700")

        self.source_folder = ""

        # Title
        self.label = ctk.CTkLabel(
            self,
            text="BULK SERIAL FILE RENAMER",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.label.pack(pady=20)

        # Manual Selection Panel
        self.select_frame = ctk.CTkFrame(self, border_width=2, border_color="#1f6aa5")
        self.select_frame.pack(pady=10, padx=40, fill="both", expand=True)

        self.select_label = ctk.CTkLabel(
            self.select_frame,
            text="SELECT A FOLDER TO BEGIN",
            font=ctk.CTkFont(size=16, slant="italic"),
        )
        self.select_label.pack(expand=True, fill="both", pady=20)

        # Folder Selection Frame
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.pack(pady=10, padx=40, fill="x")

        self.folder_btn = ctk.CTkButton(
            self.folder_frame,
            text="Select Folder",
            command=self.select_folder,
        )
        self.folder_btn.pack(pady=10, padx=20, side="left")

        self.folder_path_label = ctk.CTkLabel(
            self.folder_frame,
            text="No folder selected",
            text_color="gray",
        )
        self.folder_path_label.pack(pady=10, padx=20, side="left")

        # Naming Frame
        self.name_frame = ctk.CTkFrame(self)
        self.name_frame.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(
            self.name_frame,
            text="Base Name:",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=(10, 0), padx=20, anchor="w")

        self.name_entry = ctk.CTkEntry(
            self.name_frame,
            width=500,
            placeholder_text="e.g. project-file",
        )
        self.name_entry.pack(pady=10, padx=20)
        self.name_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        # Options Frame
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=10, padx=40, fill="x")
        self.copy_mode = ctk.BooleanVar(value=True)
        self.copy_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Safety First: Copy to new folder",
            variable=self.copy_mode,
        )
        self.copy_check.pack(pady=10, padx=20, side="left")

        # Preview Area
        ctk.CTkLabel(
            self,
            text="Rename Preview:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(10, 5))

        self.preview_text = ctk.CTkTextbox(self, width=600, height=120, state="disabled")
        self.preview_text.pack(pady=10)

        # Action Button
        self.boost_btn = ctk.CTkButton(
            self,
            text="RENAME FILES",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2da44e",
            hover_color="#22863a",
            height=50,
            command=self.execute_boost,
        )
        self.boost_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=5)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder = folder
            folder_name = os.path.basename(self.source_folder)
            self.folder_path_label.configure(text=folder_name, text_color="white")
            self.select_label.configure(text=f"Folder Loaded:\n{folder_name}", text_color="#2da44e")
            self.status_label.configure(text="✅ Folder loaded.", text_color="#2da44e")
            self.update_preview()

    def clean_name(self, name):
        name = name.lower()
        name = re.sub(r"[^a-z0-9]+", "-", name)
        return name.strip("-")

    def get_renamable_files(self):
        files = []
        for f in os.listdir(self.source_folder):
            full_path = os.path.join(self.source_folder, f)
            if os.path.isfile(full_path):
                files.append(f)
        files.sort()
        return files

    def update_preview(self):
        if not self.source_folder:
            return
        base_name = self.clean_name(self.name_entry.get()) or "product-name"
        files = self.get_renamable_files()
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        if not files:
            self.preview_text.insert("end", "No files found.")
        else:
            for i, filename in enumerate(files[:5], 1):
                ext = os.path.splitext(filename)[1].lower()
                new_name = f"{base_name}-{i:02d}{ext}"
                self.preview_text.insert("end", f"{filename}  -->  {new_name}\n")
        self.preview_text.configure(state="disabled")

    def execute_boost(self):
        if not self.source_folder:
            self.status_label.configure(text="❌ No folder loaded.", text_color="red")
            return
        base_name = self.clean_name(self.name_entry.get())
        if not base_name:
            self.status_label.configure(text="❌ Enter a keyword.", text_color="red")
            return
        files = self.get_renamable_files()
        if not files:
            self.status_label.configure(text="❌ No files found in selected folder.", text_color="red")
            return
        try:
            target_dir = os.path.join(self.source_folder, "renamed_files")
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            files.sort()
            for i, filename in enumerate(files, 1):
                ext = os.path.splitext(filename)[1].lower()
                new_name = f"{base_name}-{i:02d}{ext}"
                src = os.path.join(self.source_folder, filename)
                dst = os.path.join(target_dir, new_name)
                if self.copy_mode.get():
                    shutil.copy2(src, dst)
                else:
                    os.rename(src, dst)
            self.status_label.configure(text="✅ Success! Folder created.", text_color="green")
            try:
                if os.name == "nt":
                    os.startfile(target_dir)
                else:
                    os.system(f'xdg-open "{target_dir}" &')
            except Exception as explorer_err:
                print(f"Could not open folder automatically: {explorer_err}")
        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {str(e)}", text_color="red")


if __name__ == "__main__":
    app = BulkSerialFileRenamerApp()
    app.mainloop()
