from pathlib import Path
import tkinter as tk
from tkinter import Canvas, Entry, Button, PhotoImage, filedialog, messagebox
import requests
import pyperclip
import os
from urllib.parse import urlparse
from PIL import Image, ImageTk, ImageGrab
from io import BytesIO
import datetime

from tkinterdnd2 import DND_FILES, TkinterDnD

class ImageDownloaderApp:
    def __init__(self, window):
        self.window = window
        self.window.geometry("702x354")
        self.window.configure(bg="#FFFFFF")
        self.folder_path = tk.StringVar()
        self.image_name = tk.StringVar()  #Saving image custom name
        self.image_format = tk.StringVar(value = 'png')

        self.auto_update = True

        

        self.canvas = Canvas(
            self.window,
            bg="#FFFFFF",
            height=354,
            width=900,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        self.canvas.create_rectangle(0.0, 0.0, 702.0, 354.0, fill="#F4F4F4", outline="")

        self.canvas.create_text(240.0, 0.0, anchor="nw", text="Image Downloader", fill="#4871EC", font=("InknutAntiqua Regular", 30 * -1))
        self.canvas.create_text(34.0, 50.0, anchor="nw", text="Name", fill="#000000", font=("Inter", 12 * -1))

        self.canvas.create_text(34.0, 109.0, anchor="nw", text="Save Location", fill="#000000", font=("Inter", 12 * -1))
        self.canvas.create_text(34.0, 195.0, anchor="nw", text="Paste Image", fill="#000000", font=("Inter", 12 * -1))

        formats= ['png','jpg','jpeg', 'bmp' , 'gif' ]
        self.format_dropdown = tk.OptionMenu(self.window, self.image_format,*formats)
        self.format_dropdown.place(x=130.0, y=190.0, width = 80, height = 25.0)

        self.ASSETS_PATH = Path(r"assets\frame0")
        
        
        self.entry_image_1 = PhotoImage(file=self.relative_to_assets("entry_1.png"))
        self.entry_bg_1 = self.canvas.create_image(188.0, 150.5, image=self.entry_image_1)

        self.entry = Entry(
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0,
            textvariable=self.image_name
        )
        self.entry.place(x=34.0, y=70, width=308.0, height=31.0)

        self.entry2 = Entry(
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0,
            textvariable=self.folder_path
        )
        self.entry2.place(x=34.0, y=140.0, width=308.0, height=15.0)

        self.button_image_1 = PhotoImage(file=self.relative_to_assets("button_1.png"))
        self.button_1 = Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.choose_folder,
            relief="flat"
        )
        self.button_1.place(x=353.0, y=140.0, width=79.0, height=25.0)

        self.button_image_2 = PhotoImage(file=self.relative_to_assets("button_2.png"))
        self.button_2 = Button(
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.download_image_auto,
            relief="flat"
        )
        self.button_2.place(x=158.0, y=230.0, width=156.0, height=25.0)

        # Pause Auto-Update button
        self.toggle_button = Button(
            self.window,
            text="Pause Auto-Update",
            command=self.toggle_auto_update,
            bg="#28a745",  # xanh lá
            fg="white",
            activebackground="#218838"
        )
        self.toggle_button.place(x=160, y=270.0, width=151, height=25)

        

        self.image_image_1 = PhotoImage(file=self.relative_to_assets("image_1.png"))
        self.image_1 = self.canvas.create_image(570.0, 160.0, image=self.image_image_1)

        

        self.canvas_displayed_image = None  # Avoid garbage collection

        self.load_clipboard_image_to_canvas()
        self.last_clipboard_url = ""
        self.last_clipboard_image = None
        self.poll_clipboard()  # Check clipboard continuously

        #Notify Download success or fail
        self.status_label = tk.Label(
            self.window,
            text="Ready",
            bg="#F4F4F4",
            fg="black",
            anchor="w",
            font=("Inter", 10)
        )
        self.status_label.place(x=20, y=330, width=660, height=20)

        self.window.resizable(False, False)

    #Update status Download
    def update_status(self, message, success=True):
        self.status_label.config(
            text=message,
            fg="green" if success else "red"
        )
    def toggle_auto_update(self):
        self.auto_update = not self.auto_update
        if self.auto_update:
            self.toggle_button.config(
                text="Pause Auto-Update",
                bg="#28a745",  # xanh lá
                activebackground="#218838"
            )
        else:
            self.toggle_button.config(
                text="Resume Auto-Update",
                bg="#dc3545",  # đỏ
                activebackground="#c82333"
            )
    
    def poll_clipboard(self):
        if self.auto_update:
            current_url = pyperclip.paste()
            if current_url.lower().startswith("http") and current_url != self.last_clipboard_url:
                try:
                    response = requests.get(current_url, timeout=5)
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content))
                    self.update_canvas_image(img)
                    self.last_clipboard_url = current_url
                except Exception as e:
                    print(f"[URL Check] Invalid or unreachable URL: {e}")

            try:
                img = ImageGrab.grabclipboard()
                if isinstance(img, Image.Image) and not self.images_equal(img, self.last_clipboard_image):
                    self.update_canvas_image(img)
                    self.last_clipboard_image = img.copy()
            except Exception as e:
                print(f"[Clipboard Image Check] Error: {e}")

        self.window.after(2000, self.poll_clipboard)


    def images_equal(self, img1, img2):
        if img1 is None or img2 is None:
            return False
        return list(img1.getdata()) == list(img2.getdata())
    
    def update_canvas_image(self, img):
        img = img.copy()
        img.thumbnail((200, 200))  # giữ tỉ lệ, tránh méo ảnh
        self.canvas_displayed_image = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.image_1, image=self.canvas_displayed_image)


    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def download_image_auto(self):
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            self.update_status("Please choose a valid folder to save the image.", success=False)
            return

        # Get image name
        custom_name = self.image_name.get().strip() or "image"
        ext = f".{self.image_format.get()}"
        filename = f"{custom_name}_{self.get_timestamp()}{ext}"
        full_path = os.path.join(folder, filename)

        try:
            # Try clipboard first
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                img.save(full_path)
                self.update_status(f"Clipboard image saved to: {full_path}")
                return
        except Exception as e:
            print(f"Clipboard error: {e}")

        # Try URL
        url = pyperclip.paste()
        if url.lower().startswith("http"):
            try:
                response = requests.get(url)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                img.save(full_path)
                self.update_status(f"Image downloaded from URL to: {full_path}")
                return
            except Exception as e:
                self.update_status(f"Failed to download from URL: {e}", success=False)
                return

        self.update_status("No image in clipboard or valid image URL.", success=False)


    def load_clipboard_image_to_canvas(self):
        image = None
        url = pyperclip.paste()
        if url.lower().startswith("http"):
            try:
                response = requests.get(url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            except Exception as e:
                print(f"Failed to load image from URL: {e}")

        if image is None:
            try:
                image = ImageGrab.grabclipboard()
            except Exception as e:
                print(f"Failed to grab image from clipboard: {e}")

        if isinstance(image, Image.Image):
            image.thumbnail((200, 200), Image.Resampling.LANCZOS)
            self.canvas_displayed_image = ImageTk.PhotoImage(image)
            self.canvas.itemconfig(self.image_1, image=self.canvas_displayed_image)
        else:
            print("No valid image found in clipboard.")
            
    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Instead of tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()
