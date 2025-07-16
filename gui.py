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


class ImageDownloaderApp:
    def __init__(self, window):
        self.window = window
        self.window.geometry("702x354")
        self.window.configure(bg="#FFFFFF")
        self.folder_path = tk.StringVar()
        self.image_name = tk.StringVar()  #Saving image custom name
        self.image_format = tk.StringVar(value = 'png')

        self.canvas = Canvas(
            self.window,
            bg="#FFFFFF",
            height=354,
            width=702,
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
            command=self.download_image_from_url,
            relief="flat"
        )
        self.button_2.place(x=158.0, y=230.0, width=156.0, height=25.0)

        self.button_image_3 = PhotoImage(file=self.relative_to_assets("button_3.png"))
        self.button_3 = Button(
            image=self.button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.save_image_from_clipboard,
            relief="flat"
        )
        self.button_3.place(x=160.0, y=270.0, width=151.0, height=25.0)

        self.image_image_1 = PhotoImage(file=self.relative_to_assets("image_1.png"))
        self.image_1 = self.canvas.create_image(567.0, 193.0, image=self.image_image_1)

        self.canvas_displayed_image = None  # Avoid garbage collection

        self.load_clipboard_image_to_canvas()

        self.window.resizable(False, False)

    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def download_image_from_url(self):
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please choose a valid folder to save the image.")
            return

        url = pyperclip.paste()
        if not url.lower().startswith("http"):
            messagebox.showerror("Error", "No valid image URL found in clipboard.")
            return

        try:
            response = requests.get(url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))

            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            # if not filename or "." not in filename:
            #     filename = f"image_{self.get_timestamp()}.jpg"
            custom_name = self.image_name.get().strip()
            if not custom_name:
                custom_name = "image"
            ext = f".{self.image_format.get()}"
            filename = f"{custom_name}_{self.get_timestamp()}{ext}"

            full_path = os.path.join(folder, filename)
            img.save(full_path)
            messagebox.showinfo("Success", f"Image downloaded to:\n{full_path}")
        except Exception as e:
            messagebox.showerror("Download Failed", str(e))

    def save_image_from_clipboard(self):
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please choose a valid folder to save the image.")
            return

        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                # filename = f"clipboard_image_{self.get_timestamp()}.png"
                custom_name = self.image_name.get().strip()
                if not custom_name:
                    custom_name = "image"
                ext = f".{self.image_format.get()}"
                filename = f"{custom_name}_{self.get_timestamp()}{ext}"
                full_path = os.path.join(folder, filename)
                img.save(full_path)
                messagebox.showinfo("Success", f"Clipboard image saved to:\n{full_path}")
            else:
                messagebox.showerror("Error", "No image found in clipboard.")
        except Exception as e:
            messagebox.showerror("Paste Failed", str(e))

    def load_clipboard_image_to_canvas(self):
        image = None

        # Try loading from URL in clipboard
        url = pyperclip.paste()
        if url.lower().startswith("http"):
            try:
                response = requests.get(url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            except Exception as e:
                print(f"Failed to load image from URL: {e}")

        # If not URL or failed, try loading image from clipboard
        if image is None:
            try:
                image = ImageGrab.grabclipboard()
            except Exception as e:
                print(f"Failed to grab image from clipboard: {e}")

        # Display if valid
        if isinstance(image, Image.Image):
            image = image.resize((200, 200))  # Optional: resize to fit canvas
            self.canvas_displayed_image = ImageTk.PhotoImage(image)
            self.canvas.itemconfig(self.image_1, image=self.canvas_displayed_image)
        else:
            print("No valid image found in clipboard.")
            
    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()
