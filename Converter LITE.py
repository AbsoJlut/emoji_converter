try:
    import tkinter as tk
    from tkinter import filedialog, ttk, messagebox, TclError
except ImportError as e:
    raise ImportError("Не удалось импортировать tkinter. Убедитесь, что он установлен. На Windows проверьте, что Python установлен с поддержкой tkinter. На Linux установите его с помощью: `sudo apt-get install python3-tk`. Ошибка: " + str(e))

import subprocess
import os
import sys
import time
from PIL import Image, ImageSequence

# === Утилита для доступа к ресурсам (иконка, gif) ===
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

ICON_PATH = resource_path("icon.ico")

# === Инициализация окна ===
root = tk.Tk()
root.title("TG & DS & Twitch Emoji Converter by AbsoJlut (Lite version)")
root.geometry("700x800")
root.resizable(False, False)

try:
    root.iconbitmap(ICON_PATH)
except:
    pass

# === UI ===
tk.Label(root, text="Выберите режим конвертации:").pack(pady=10)
mode_var = tk.StringVar(value="Telegram")
ttk.Combobox(root, textvariable=mode_var, values=["Telegram", "Discord", "Twitch"], state="readonly").pack()

tk.Label(root, text="Выберите PNG, GIF, WebP, JPG или MP4 файлы:").pack(pady=10)
entry_file = tk.Entry(root, width=50)
entry_file.pack(pady=5)
tk.Button(root, text="Обзор...", command=lambda: select_file()).pack()

# === Параметры конвертации ===
params_frame = tk.LabelFrame(root, text="Настройки качества", padx=10, pady=10)
params_frame.pack(pady=10, fill="x", padx=10)

# Telegram параметры
telegram_params_frame = tk.Frame(params_frame)
tk.Label(telegram_params_frame, text="Параметры для Telegram:", font=("Arial", 10, "bold")).pack(anchor="w")
tk.Label(telegram_params_frame, text="CRF (10-50, меньше — лучше качество, больше — меньше размер):").pack(anchor="w")
telegram_crf_var = tk.IntVar(value=30)
tk.Scale(telegram_params_frame, from_=10, to=50, orient="horizontal", variable=telegram_crf_var).pack(fill="x")
tk.Label(telegram_params_frame, text="Разрешение (48-100, больше — лучше качество, больше размер):").pack(anchor="w")
telegram_res_var = tk.IntVar(value=100)
tk.Scale(telegram_params_frame, from_=48, to=100, orient="horizontal", variable=telegram_res_var, resolution=4).pack(fill="x")
tk.Label(telegram_params_frame, text="FPS (5-30, больше — плавнее, больше размер):").pack(anchor="w")
telegram_fps_var = tk.IntVar(value=10)
tk.Scale(telegram_params_frame, from_=5, to=30, orient="horizontal", variable=telegram_fps_var).pack(fill="x")

# Discord параметры
discord_params_frame = tk.Frame(params_frame)
tk.Label(discord_params_frame, text="Параметры для Discord:", font=("Arial", 10, "bold")).pack(anchor="w")
tk.Label(discord_params_frame, text="Разрешение (64-128, больше — лучше качество, больше размер):").pack(anchor="w")
discord_res_var = tk.IntVar(value=128)
tk.Scale(discord_params_frame, from_=64, to=128, orient="horizontal", variable=discord_res_var, resolution=4).pack(fill="x")
tk.Label(discord_params_frame, text="FPS для GIF/MP4 (5-30, больше — плавнее, больше размер):").pack(anchor="w")
discord_fps_var = tk.IntVar(value=10)
tk.Scale(discord_params_frame, from_=5, to=30, orient="horizontal", variable=discord_fps_var).pack(fill="x")
tk.Label(discord_params_frame, text="Качество PNG (10-100, больше — лучше качество, больше размер):").pack(anchor="w")
discord_quality_var = tk.IntVar(value=85)
tk.Scale(discord_params_frame, from_=10, to=100, orient="horizontal", variable=discord_quality_var, resolution=5).pack(fill="x")

# Twitch параметры
twitch_params_frame = tk.Frame(params_frame)
tk.Label(twitch_params_frame, text="Параметры для Twitch:", font=("Arial", 10, "bold")).pack(anchor="w")
tk.Label(twitch_params_frame, text="Качество PNG (10-100, больше — лучше качество, больше размер):").pack(anchor="w")
twitch_quality_var = tk.IntVar(value=100)
tk.Scale(twitch_params_frame, from_=10, to=100, orient="horizontal", variable=twitch_quality_var, resolution=5).pack(fill="x")

def update_params_visibility(*args):
    telegram_params_frame.pack_forget()
    discord_params_frame.pack_forget()
    twitch_params_frame.pack_forget()
    if mode_var.get() == "Telegram":
        telegram_params_frame.pack(fill="x", pady=5)
    elif mode_var.get() == "Discord":
        discord_params_frame.pack(fill="x", pady=5)
    else:
        twitch_params_frame.pack(fill="x", pady=5)

mode_var.trace("w", update_params_visibility)
update_params_visibility()

tk.Label(root, text="Нажмите для конвертации:").pack(pady=10)
tk.Button(root, text="Конвертировать", command=lambda: start_conversion(),
          bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), width=25).pack(pady=10)

error_text = tk.Text(root, height=4, width=40, wrap=tk.WORD, font=("Arial", 10))
copy_button = tk.Button(root, text="Скопировать ошибку", command=lambda: copy_error_to_clipboard(),
                        bg="#FF5555", fg="white", font=("Arial", 10))
error_text.pack_forget()
copy_button.pack_forget()

tk.Label(root, text="Сделано специально для Kotya Lisichkina", fg="#808080", font=("Arial", 8)).pack(pady=5)

# === Вспомогательные функции ===
def show_error(msg):
    error_text.delete(1.0, tk.END)
    error_text.insert(tk.END, msg)
    error_text.pack(pady=5)
    copy_button.pack(pady=5)

def hide_error():
    error_text.pack_forget()
    copy_button.pack_forget()

def copy_error_to_clipboard():
    msg = error_text.get(1.0, tk.END).strip()
    root.clipboard_clear()
    root.clipboard_append(msg)
    messagebox.showinfo("Успех", "Скопировано в буфер обмена")

def select_file():
    paths = filedialog.askopenfilenames(filetypes=[("Image/Video", "*.gif *.png *.webp *.jpg *.mp4")])
    if paths:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, "; ".join(paths))

def start_conversion():
    hide_error()
    paths = entry_file.get().split("; ")
    if not paths or not paths[0]:
        messagebox.showerror("Ошибка", "Выберите файл(ы)")
        return
    mode = mode_var.get()
    if mode == "Telegram":
        convert_to_telegram(paths)
    elif mode == "Discord":
        convert_to_discord(paths)
    else:  # Twitch
        convert_to_twitch(paths)

# === Конвертация для Telegram ===
def convert_to_telegram(input_paths):
    if len(input_paths) != 1:
        messagebox.showerror("Ошибка", "Выберите только один файл!")
        return

    input_path = input_paths[0]
    if not input_path.lower().endswith(('.png', '.jpg', '.mp4', '.gif')):
        messagebox.showerror("Ошибка", "Телеграм режим поддерживает только PNG, JPG, GIF или MP4 файлы!")
        return

    temp_gif_path = os.path.splitext(input_path)[0] + "_temp.gif"
    output_path = os.path.splitext(input_path)[0] + "_telegram_emoji.webm"
    max_size_kb = 64
    max_duration = 3.0
    resolution = telegram_res_var.get()
    crf = telegram_crf_var.get()
    fps = telegram_fps_var.get()

    try:
        durations = []
        frame_count = 0
        if input_path.lower().endswith(('.png', '.jpg')):
            with Image.open(input_path) as img:
                img = img.convert("RGBA")
                frames = [img.resize((resolution, resolution), Image.Resampling.LANCZOS)] * 30
                durations = [100] * 30
                frame_count = 30
                frames[0].save(temp_gif_path, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
                print(f"Создан GIF из {input_path}: {frame_count} кадров, длительности: {durations}")
        elif input_path.lower().endswith('.gif'):
            cmd_probe = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames", "-of", "default=noprint_wrappers=1:nokey=1", input_path]
            try:
                frame_count = int(subprocess.check_output(cmd_probe, text=True).strip())
                print(f"Исходный GIF: {frame_count} кадров")
            except:
                frame_count = 0
                print("Не удалось определить количество кадров в GIF")
            temp_gif_path = input_path
        elif input_path.lower().endswith('.mp4'):
            cmd = [
                "ffmpeg", "-i", os.path.normpath(input_path), "-vf", f"scale={resolution}:{resolution}:force_original_aspect_ratio=decrease",
                "-pix_fmt", "rgba", "-f", "gif", "-r", str(fps), "-y", os.path.normpath(temp_gif_path)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            with Image.open(temp_gif_path) as temp_gif:
                for frame in ImageSequence.Iterator(temp_gif):
                    durations.append(frame.info.get("duration", 50))
                    frame_count += 1
                print(f"Промежуточный GIF из MP4: {frame_count} кадров, длительности: {durations}")

        total_duration = min(sum(durations) / 1000, max_duration) if durations else max_duration
        if total_duration <= 0 or frame_count <= 1:
            total_duration = max_duration
            durations = [100] * int(fps * total_duration)
            frame_count = len(durations)
            print(f"Запасная длительность: {total_duration} сек, {frame_count} кадров")

        for attempt in range(3):
            cmd = [
                "ffmpeg", "-i", os.path.normpath(temp_gif_path), "-vf",
                f"scale={resolution}:{resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2,format=yuva420p",
                "-c:v", "libvpx-vp9", "-crf", str(crf), "-b:v", "0", "-t", str(total_duration),
                "-r", str(fps), "-an", "-loop", "0", "-y", os.path.normpath(output_path)
            ]
            try:
                result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print(f"FFmpeg команда: {' '.join(cmd)}")
                print(f"FFmpeg вывод: {result.stderr}")
            except subprocess.CalledProcessError as e:
                raise Exception(f"FFmpeg error: {e.stderr}")

            final_size_kb = os.path.getsize(output_path) / 1024
            if final_size_kb <= max_size_kb or attempt == 2:
                break
            if attempt == 0:
                crf = min(crf + 10, 50)
                print(f"Попытка {attempt + 1}: CRF={crf}, разрешение={resolution}, FPS={fps}")
            elif attempt == 1:
                resolution = max(resolution - 16, 48)
                crf = telegram_crf_var.get()
                print(f"Попытка {attempt + 1}: CRF={crf}, разрешение={resolution}, FPS={fps}")

        if final_size_kb > max_size_kb:
            messagebox.showwarning("Превышен размер", f"Размер {final_size_kb:.1f} КБ превышает 64 КБ.")
            os.remove(output_path)
            return

        cmd_probe_webm = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames", "-of", "default=noprint_wrappers=1:nokey=1", output_path]
        try:
            webm_frame_count = int(subprocess.check_output(cmd_probe_webm, text=True).strip())
            print(f"Выходной WebM: {webm_frame_count} кадров")
        except:
            webm_frame_count = 0
            print("Не удалось определить количество кадров в WebM")

        messagebox.showinfo("Готово", f"Сохранено как {output_path} (размер: {final_size_kb:.1f} КБ, разрешение: {resolution}x{resolution}, длительность: {total_duration:.1f} сек, кадров: {webm_frame_count})")

    except subprocess.CalledProcessError as e:
        show_error(f"FFmpeg error: {e.stderr}")
    except Exception as e:
        show_error(str(e))
    finally:
        if input_path.lower().endswith(('.png', '.jpg', '.mp4')):
            for f in [temp_gif_path, "ffmpeg2pass-0.log", "ffmpeg2pass-0.log.mbtree"]:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except PermissionError:
                        time.sleep(0.5)
                        os.remove(f)

# === Конвертация для Discord ===
def convert_to_discord(input_paths):
    input_path = input_paths[0]
    if not input_path.lower().endswith(('.png', '.jpg', '.mp4', '.gif')):
        messagebox.showerror("Ошибка", "Дискорд режим поддерживает только PNG, JPG, GIF или MP4 файлы!")
        return
    suffix = "_discord_emoji"
    output_ext = ".png" if input_path.lower().endswith(".png") else ".gif"
    temp_path = os.path.splitext(input_path)[0] + "_temp" + output_ext
    max_size_kb = 256
    resolution = discord_res_var.get()
    fps = discord_fps_var.get()
    quality = discord_quality_var.get()

    try:
        if input_path.lower().endswith(".png"):
            with Image.open(input_path) as img:
                img = img.convert("RGBA")
                resized = img.resize((resolution, resolution), Image.Resampling.LANCZOS)
                resized.save(temp_path, format="PNG", optimize=True, quality=quality)
                size_kb = os.path.getsize(temp_path) / 1024
                if size_kb > max_size_kb:
                    messagebox.showwarning("Превышен размер", f"Размер {size_kb:.1f} КБ превышает 256 КБ.")
                    os.remove(temp_path)
                    return

        elif input_path.lower().endswith((".gif", ".mp4")):
            cmd = [
                "ffmpeg", "-i", os.path.normpath(input_path), "-vf", f"scale={resolution}:{resolution}",
                "-pix_fmt", "rgb8", "-f", "gif", "-r", str(fps), "-qmin", "1", "-qmax", "20", "-y", os.path.normpath(temp_path)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            size_kb = os.path.getsize(temp_path) / 1024
            if size_kb > max_size_kb:
                messagebox.showwarning("Превышен размер", f"Размер {size_kb:.1f} КБ превышает 256 КБ.")
                os.remove(temp_path)
                return

        output_path = os.path.splitext(input_path)[0] + suffix + output_ext
        for _ in range(3):
            try:
                os.rename(temp_path, output_path)
                break
            except PermissionError as e:
                if "[WinError 32]" in str(e):
                    time.sleep(0.5)
                else:
                    raise e
        else:
            raise Exception("Не удалось переименовать файл: он занят другим процессом")

        messagebox.showinfo("Готово", f"Сохранено как {output_path} (размер: {size_kb:.1f} КБ, разрешение: {resolution}x{resolution})")

    except Exception as e:
        show_error(str(e))
        if os.path.exists(temp_path):
            os.remove(temp_path)

# === Конвертация для Twitch ===
def convert_to_twitch(input_paths):
    if len(input_paths) != 1:
        messagebox.showerror("Ошибка", "Выберите только один файл!")
        return

    input_path = input_paths[0]
    if not input_path.lower().endswith(('.png', '.jpg', '.webp')):
        messagebox.showerror("Ошибка", "Twitch режим поддерживает только PNG, JPG или WebP файлы!")
        return

    output_sizes = [28, 56, 112]
    max_size_kb = 25
    suffix = "_twitch_emoji"
    output_paths = []
    quality = twitch_quality_var.get()

    try:
        with Image.open(input_path) as img:
            img = img.convert("RGBA")
            base_name = os.path.splitext(input_path)[0]

            for size in output_sizes:
                output_path = f"{base_name}_{size}x{size}{suffix}.png"
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                
                temp_path = f"{base_name}_temp_{size}.png"
                resized.save(temp_path, format="PNG", optimize=True, quality=quality)
                size_kb = os.path.getsize(temp_path) / 1024
                if size_kb > max_size_kb:
                    messagebox.showwarning("Превышен размер", f"Размер {size_kb:.1f} КБ для {size}x{size} превышает 25 КБ.")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return

                for _ in range(3):
                    try:
                        os.rename(temp_path, output_path)
                        break
                    except PermissionError as e:
                        if "[WinError 32]" in str(e):
                            time.sleep(0.5)
                        else:
                            raise e
                else:
                    raise Exception(f"Не удалось переименовать файл {temp_path}: он занят другим процессом")

                output_paths.append((output_path, size_kb, size))

        message = "\n".join([f"Сохранено как {path} (размер: {size:.1f} КБ, разрешение: {res}x{res})" for path, size, res in output_paths])
        messagebox.showinfo("Готово", message)

    except Exception as e:
        show_error(str(e))
        for path, _, _ in output_paths:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(temp_path):
            os.remove(temp_path)

root.mainloop()
