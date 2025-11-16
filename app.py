import threading
import math
import time
import subprocess
import shlex
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import shutil
import tempfile

from moviepy.editor import VideoFileClip


APP_NAME = "ClipForge"
COMPANY = "CodeX"

# Font configuration for better readability
FONT_FAMILY = "Segoe UI"
FONT_SIZE_TITLE = 18
FONT_SIZE_HEADING = 11
FONT_SIZE_NORMAL = 10
FONT_SIZE_SMALL = 9
FONT_SIZE_TINY = 8


class VideoTrimmerApp:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title(f"{APP_NAME} by {COMPANY}")
		self.root.geometry("850x520")
		self.root.resizable(False, False)
		# Set modern background color
		self.root.configure(bg="#f8f9fa")
		
		# Set window icon
		self._set_window_icon()

		self.video_path_var = tk.StringVar()
		# Set default output to application directory (where the script/exe is located)
		default_output = self._get_app_directory()
		self.output_dir_var = tk.StringVar(value=default_output)
		self.duration_var = tk.IntVar(value=30)
		self.status_var = tk.StringVar(value="Select a video and output folder.")
		self.analysis_var = tk.StringVar(value="")
		self.filename_base_var = tk.StringVar(value="")
		self.progress_var = tk.DoubleVar(value=0.0)
		self.time_var = tk.StringVar(value="")
		# no destructive options; we keep the original file intact

		self._build_ui()
		self.root.after(50, self._show_splash)

	def _set_window_icon(self) -> None:
		"""Set the window icon from icon.ico file."""
		try:
			icon_path = self._resolve_asset("icon.ico")
			if not icon_path.exists():
				icon_path = self._resolve_asset("assets/clipforge.ico")
			if icon_path.exists():
				try:
					self.root.iconbitmap(str(icon_path))
				except Exception:
					# Fallback for systems that don't support iconbitmap
					pass
		except Exception:
			pass
	
	def _build_ui(self) -> None:
		# Import ttk after Tk root is initialized
		global ttk
		import tkinter.ttk as ttk
		
		padx = 14
		pady = 10
		bg_color = "#f8f9fa"

		# Branding row with better styling
		frm_brand = tk.Frame(self.root, bg=bg_color)
		frm_brand.pack(fill="x", padx=padx, pady=(14, 12))
		self.logo_img = None
		logo_path = self._resolve_asset("assets/logo.png")
		if logo_path.exists():
			try:
				self.logo_img = tk.PhotoImage(file=str(logo_path))
				logo_lbl = tk.Label(frm_brand, image=self.logo_img, bg=bg_color)
				logo_lbl.pack(side="left")
			except Exception:
				pass
		lbl_title = tk.Label(frm_brand, text=f"{APP_NAME}", 
		                    font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"), 
		                    bg=bg_color, fg="#1a1a1a")
		lbl_title.pack(side="left", padx=(10, 0))

		# Input video selector with improved styling
		frm_input = tk.Frame(self.root, bg=bg_color)
		frm_input.pack(fill="x", padx=padx, pady=pady)
		tk.Label(frm_input, text="Input video:", 
		        font=(FONT_FAMILY, FONT_SIZE_NORMAL, "normal"), 
		        bg=bg_color, fg="#2c3e50", width=14, anchor="w").pack(side="left")
		ent_in = tk.Entry(frm_input, textvariable=self.video_path_var, width=50, 
		                 font=(FONT_FAMILY, FONT_SIZE_NORMAL), 
		                 relief="solid", bd=1, highlightthickness=1, 
		                 highlightbackground="#dee2e6", highlightcolor="#3498db")
		ent_in.pack(side="left", padx=(10, 10), fill="x", expand=True)
		btn_browse1 = tk.Button(frm_input, text="Browse", command=self._choose_video, 
		                       font=(FONT_FAMILY, FONT_SIZE_NORMAL, "normal"), 
		                       bg="#3498db", fg="white", activebackground="#2980b9", 
		                       relief="flat", padx=16, pady=2, cursor="hand2",
		                       borderwidth=0, highlightthickness=0)
		btn_browse1.pack(side="left")

		# Output dir selector with info note
		frm_out = tk.Frame(self.root, bg=bg_color)
		frm_out.pack(fill="x", padx=padx, pady=pady)
		tk.Label(frm_out, text="Output folder:", 
		        font=(FONT_FAMILY, FONT_SIZE_NORMAL, "normal"), 
		        bg=bg_color, fg="#2c3e50", width=14, anchor="w").pack(side="left")
		ent_out = tk.Entry(frm_out, textvariable=self.output_dir_var, width=50, 
		                  font=(FONT_FAMILY, FONT_SIZE_NORMAL), 
		                  relief="solid", bd=1, highlightthickness=1,
		                  highlightbackground="#dee2e6", highlightcolor="#3498db")
		ent_out.pack(side="left", padx=(10, 10), fill="x", expand=True)
		btn_browse2 = tk.Button(frm_out, text="Browse", command=self._choose_output_dir, 
		                       font=(FONT_FAMILY, FONT_SIZE_NORMAL, "normal"),
		                       bg="#3498db", fg="white", activebackground="#2980b9", 
		                       relief="flat", padx=16, pady=2, cursor="hand2",
		                       borderwidth=0, highlightthickness=0)
		btn_browse2.pack(side="left")
		
		# Info label about Outputs folder
		frm_info = tk.Frame(self.root, bg=bg_color)
		frm_info.pack(fill="x", padx=padx, pady=(0, pady))
		tk.Label(frm_info, text="", 
		        font=(FONT_FAMILY, FONT_SIZE_TINY), bg=bg_color, width=14).pack(side="left")
		tk.Label(frm_info, text="Outputs saved in 'Outputs' folder with subfolder based on filename", 
		         font=(FONT_FAMILY, FONT_SIZE_TINY, "italic"), bg=bg_color, fg="#6c757d", anchor="w").pack(side="left", padx=(10, 0))

		# Filename base
		frm_name = tk.Frame(self.root, bg=bg_color)
		frm_name.pack(fill="x", padx=padx, pady=pady)
		tk.Label(frm_name, text="Filename base:", 
		        font=(FONT_FAMILY, FONT_SIZE_NORMAL, "normal"), 
		        bg=bg_color, fg="#2c3e50", width=14, anchor="w").pack(side="left")
		ent_name = tk.Entry(frm_name, textvariable=self.filename_base_var, width=30, 
		                   font=(FONT_FAMILY, FONT_SIZE_NORMAL), 
		                   relief="solid", bd=1, highlightthickness=1,
		                   highlightbackground="#dee2e6", highlightcolor="#3498db")
		ent_name.pack(side="left", padx=(10, 10))
		tk.Label(frm_name, text="(optional)", 
		        font=(FONT_FAMILY, FONT_SIZE_TINY), bg=bg_color, fg="#6c757d", anchor="w").pack(side="left")

		# Duration selection with better styling
		frm_dur = tk.Frame(self.root, bg=bg_color)
		frm_dur.pack(fill="x", padx=padx, pady=pady)
		tk.Label(frm_dur, text="Trim length:", 
		        font=(FONT_FAMILY, FONT_SIZE_NORMAL, "normal"), 
		        bg=bg_color, fg="#2c3e50", width=14, anchor="w").pack(side="left")
		rb1 = tk.Radiobutton(frm_dur, text="30 seconds", value=30, variable=self.duration_var, 
		                    font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=bg_color, fg="#2c3e50", 
		                    activebackground=bg_color, selectcolor="#e9ecef", cursor="hand2",
		                    activeforeground="#2c3e50")
		rb1.pack(side="left", padx=(10, 12))
		rb2 = tk.Radiobutton(frm_dur, text="60 seconds", value=60, variable=self.duration_var,
		                    font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=bg_color, fg="#2c3e50", 
		                    activebackground=bg_color, selectcolor="#e9ecef", cursor="hand2",
		                    activeforeground="#2c3e50")
		rb2.pack(side="left", padx=12)

		# Action buttons with modern styling
		frm_actions = tk.Frame(self.root, bg=bg_color)
		frm_actions.pack(fill="x", padx=padx, pady=(pady+6, pady))
		btn_analyze = tk.Button(frm_actions, text="Analyze Video", command=self._on_analyze_clicked,
		                       font=(FONT_FAMILY, FONT_SIZE_HEADING, "bold"), 
		                       bg="#6c757d", fg="white", activebackground="#5a6268", 
		                       relief="flat", padx=24, pady=8, cursor="hand2",
		                       borderwidth=0, highlightthickness=0)
		btn_analyze.pack(side="left", padx=(0, 12))
		btn_split = tk.Button(frm_actions, text="Split Video", command=self._on_split_all_clicked,
		                     font=(FONT_FAMILY, FONT_SIZE_HEADING, "bold"), 
		                     bg="#28a745", fg="white", activebackground="#218838", 
		                     relief="flat", padx=24, pady=8, cursor="hand2",
		                     borderwidth=0, highlightthickness=0)
		btn_split.pack(side="left")

		# Status label with better styling
		frm_status = tk.Frame(self.root, bg=bg_color)
		frm_status.pack(fill="x", padx=padx, pady=(pady, 6))
		tk.Label(frm_status, text="Status:", 
		       font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"), 
		       bg=bg_color, fg="#495057").pack(side="left")
		self.status_label = tk.Label(frm_status, textvariable=self.status_var, anchor="w", 
		                            fg="#212529", bg=bg_color, 
		                            font=(FONT_FAMILY, FONT_SIZE_NORMAL))
		self.status_label.pack(side="left", padx=(10, 0), fill="x", expand=True)

		# Analysis label with better styling
		frm_analysis = tk.Frame(self.root, bg=bg_color)
		frm_analysis.pack(fill="x", padx=padx, pady=(0, pady))
		self.analysis_label = tk.Label(frm_analysis, textvariable=self.analysis_var, anchor="w", 
		                              fg="#28a745", bg=bg_color, 
		                              font=(FONT_FAMILY, FONT_SIZE_NORMAL))
		self.analysis_label.pack(fill="x")

		# Progress bar and time info with better styling
		frm_prog = tk.Frame(self.root, bg=bg_color)
		frm_prog.pack(fill="x", padx=padx, pady=(0, pady+6))
		tk.Label(frm_prog, text="Progress:", 
		       font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"), 
		       bg=bg_color, fg="#495057").pack(anchor="w")
		frm_prog_bar = tk.Frame(frm_prog, bg=bg_color)
		frm_prog_bar.pack(fill="x", pady=(6, 0))
		# Configure ttk progress bar style
		style = ttk.Style()
		style.theme_use('default')
		style.configure("TProgressbar", 
		               background="#28a745", 
		               troughcolor="#e9ecef", 
		               borderwidth=0, 
		               lightcolor="#28a745", 
		               darkcolor="#28a745",
		               thickness=20)
		self.progress_bar = ttk.Progressbar(frm_prog_bar, maximum=100, 
		                                    variable=self.progress_var, 
		                                    style="TProgressbar", 
		                                    length=400,
		                                    mode='determinate')
		self.progress_bar.pack(fill="x")
		self.time_label = tk.Label(frm_prog_bar, textvariable=self.time_var, anchor="w", 
		                          fg="#6c757d", bg=bg_color, 
		                          font=(FONT_FAMILY, FONT_SIZE_TINY))
		self.time_label.pack(fill="x", pady=(6, 0))
	def _show_splash(self) -> None:
		# Simple splash that slides the logo text opacity by updating title dots
		splash = tk.Toplevel(self.root)
		splash.overrideredirect(True)
		splash.attributes("-topmost", True)
		splash.geometry("360x160+" + str(self.root.winfo_rootx()+80) + "+" + str(self.root.winfo_rooty()+60))
		frm = tk.Frame(splash, bg="#ffffff")
		frm.pack(fill="both", expand=True)
		lbl = tk.Label(frm, text=f"{APP_NAME}", font=("Segoe UI", 18, "bold"), bg="#ffffff", fg="#2c3e50")
		lbl.pack(pady=16)
		if self.logo_img:
			logo = tk.Label(frm, image=self.logo_img, bg="#ffffff")
			logo.pack()
			try:
				splash.iconphoto(True, self.logo_img)
			except Exception:
				pass
		loading = tk.Label(frm, text="Starting", bg="#ffffff", fg="#7f8c8d", font=("Segoe UI", 9))
		loading.pack(pady=8)

		dots = {"count": 0}
		def animate():
			dots["count"] = (dots["count"] + 1) % 4
			loading.configure(text="Starting" + "." * dots["count"])
			splash.after(180, animate)
		animate()

		def close():
			try:
				splash.destroy()
			except Exception:
				pass
		self.root.after(1200, close)

	def _choose_video(self) -> None:
		filetypes = (
			("Video files", "*.mp4 *.mov *.mkv *.avi *.webm"),
			("All files", "*.*"),
		)
		path = filedialog.askopenfilename(title="Select video", filetypes=filetypes)
		if path:
			self.video_path_var.set(path)

	def _choose_output_dir(self) -> None:
		path = filedialog.askdirectory(title="Select output folder")
		if path:
			self.output_dir_var.set(path)

	def _on_analyze_clicked(self) -> None:
		video_path = self.video_path_var.get().strip()
		duration = int(self.duration_var.get())

		if not video_path:
			messagebox.showwarning("Missing input", "Please choose an input video file.")
			return
		if not Path(video_path).exists():
			messagebox.showerror("File not found", "The selected video file does not exist.")
			return

		self._set_busy(True)
		self.status_var.set("Analyzing video length...")
		threading.Thread(target=self._analyze_worker, args=(Path(video_path), duration), daemon=True).start()

	def _on_split_all_clicked(self) -> None:
		video_path = self.video_path_var.get().strip()
		output_dir = self.output_dir_var.get().strip()
		duration = int(self.duration_var.get())

		if not video_path:
			messagebox.showwarning("Missing input", "Please choose an input video file.")
			return
		if not Path(video_path).exists():
			messagebox.showerror("File not found", "The selected video file does not exist.")
			return
		
		# Determine dynamic output path: Create Outputs folder and subfolder based on filename base
		base_dir = Path(output_dir).expanduser() if output_dir else Path.cwd()
		outputs_dir = base_dir / "Outputs"
		base_name = self._sanitize_basename(self.filename_base_var.get().strip() or Path(video_path).stem)
		# Base name is already truncated to 30 chars in _sanitize_basename
		out_path = outputs_dir / base_name
		
		if not out_path.exists():
			try:
				out_path.mkdir(parents=True, exist_ok=True)
			except Exception as exc:  # pragma: no cover
				messagebox.showerror("Output error", f"Cannot create output folder.\n{exc}")
				return

		# reflect resolved path back to UI for clarity
		self.output_dir_var.set(str(out_path))

		self._set_busy(True)
		self.progress_var.set(0)
		self.time_var.set("")
		self.status_var.set("Preparing... copying to temp and analyzing video")
		threading.Thread(target=self._split_worker, args=(Path(video_path), out_path, duration), daemon=True).start()

	def _analyze_worker(self, input_path: Path, segment_seconds: int) -> None:
		try:
			with VideoFileClip(str(input_path)) as clip:
				total_seconds = float(clip.duration or 0)
				if total_seconds <= 0:
					raise ValueError("Video has unknown duration")
				max_seconds = 2 * 60 * 60
				warning = ""
				if total_seconds > max_seconds:
					warning = " (over 2 hours)"
				parts = int(math.ceil(total_seconds / segment_seconds))
				last_len = total_seconds - (segment_seconds * (parts - 1)) if parts > 0 else 0
				msg = f"Length: {int(total_seconds)}s{warning}. Will produce {parts} part(s). Last part: {int(last_len)}s."
				self._set_status_main_thread("Analysis complete.")
				self.root.after(0, lambda: self.analysis_var.set(msg))
		except Exception as exc:
			self._show_error_main_thread("Analyze failed", str(exc))
		finally:
			self._set_busy(False)

	def _split_worker(self, input_path: Path, output_dir: Path, segment_seconds: int) -> None:
		tmp_input = None
		mp4_source = None
		mp4_source_is_temp = False
		try:
			stem = input_path.stem
			ext = ".mp4"
			# Work on a temp copy to avoid touching original and to ensure readable path
			# Use shorter temp filename to avoid path length issues
			tmp_dir = Path(tempfile.gettempdir())
			# Use timestamp and short hash instead of full filename
			safe_temp_name = f"cf_{int(time.time())}_{hash(input_path.name) % 10000:04d}{input_path.suffix}"
			tmp_input = tmp_dir / safe_temp_name
			shutil.copy2(str(input_path), str(tmp_input))

			# Ensure MP4 source (fast remux first, then re-encode if needed) and get duration
			self._set_status_main_thread("Converting to MP4 (if needed)...")
			mp4_source = self._ensure_mp4_with_progress(tmp_input)
			# Check if mp4_source is a temp file (different from tmp_input)
			if mp4_source != tmp_input:
				mp4_source_is_temp = True
			# Probe duration quickly via ffprobe to avoid opening via MoviePy
			total_seconds = self._ffprobe_duration_seconds(mp4_source)
			if total_seconds is None:
				with VideoFileClip(str(mp4_source)) as clip:
					total_seconds = float(clip.duration or 0)
			if not total_seconds or total_seconds <= 0:
				raise ValueError("Video has unknown duration")
			parts = int(math.ceil(total_seconds / segment_seconds))
			base_raw = self.filename_base_var.get().strip() or stem
			# Sanitize and truncate base name aggressively to avoid path length issues
			base = self._sanitize_basename(base_raw)
			self._set_status_main_thread(f"Splitting into {parts} parts (fast mode)...")

			# Fast single-pass segmentation with live progress
			fast_ok = self._segment_with_progress(mp4_source, output_dir, base, ext, segment_seconds, total_seconds)
			if fast_ok:
				self.progress_var.set(100.0)
				self._set_status_main_thread("All parts saved.")
			else:
				# Fallback to older per-part approach if needed
				# Ensure output directory exists
				output_dir.mkdir(parents=True, exist_ok=True)
				with VideoFileClip(str(mp4_source)) as clip:
					start_time = time.time()
					for idx in range(parts):
						start_t = idx * segment_seconds
						end_t = min((idx + 1) * segment_seconds, total_seconds)
						part_num = idx + 1
						# Use shorter filename to avoid path length issues
						output_filename = f"{base}_part_{part_num:03d}{ext}"
						output_path = output_dir / output_filename
						seg_len = max(0.01, end_t - start_t)
						ffmpeg_cmd = [
							"ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
						"-ss", f"{start_t}", "-i", str(mp4_source), "-t", f"{seg_len}",
							"-c", "copy", "-avoid_negative_ts", "make_zero",
							str(output_path),
						]
						use_fallback = False
						try:
							proc = subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
							if proc.returncode != 0:
								use_fallback = True
						except (subprocess.TimeoutExpired, Exception):
							use_fallback = True
						if use_fallback:
							try:
								# Create short temp directory for MoviePy to avoid long path issues
								moviepy_temp_dir = Path(tempfile.gettempdir()) / f"cf_mpy_{int(time.time())}"
								moviepy_temp_dir.mkdir(exist_ok=True)
								try:
									# Set environment variable for MoviePy temp directory
									original_temp = os.environ.get("TMPDIR") or os.environ.get("TEMP")
									os.environ["TMPDIR"] = str(moviepy_temp_dir)
									os.environ["TEMP"] = str(moviepy_temp_dir)
									
									segment = clip.subclip(start_t, end_t)
									# Use short temp file names to avoid path length issues
									short_output_path = str(output_path)
									# Ensure output path is short enough
									if len(short_output_path) > 200:
										# If path is too long, move output to temp and copy
										short_temp_output = moviepy_temp_dir / f"p{part_num:03d}.mp4"
										segment.write_videofile(
											str(short_temp_output), codec="libx264", audio_codec="aac", 
											threads=2, verbose=False, logger=None, 
											temp_audiofile=str(moviepy_temp_dir / f"a{part_num:03d}.m4a")
										)
										# Copy final file to desired location
										shutil.copy2(str(short_temp_output), str(output_path))
										try:
											short_temp_output.unlink(missing_ok=True)
										except Exception:
											pass
									else:
										segment.write_videofile(
											str(short_output_path), codec="libx264", audio_codec="aac", 
											threads=2, verbose=False, logger=None, 
											temp_audiofile=str(moviepy_temp_dir / f"a{part_num:03d}.m4a")
										)
								finally:
									# Restore original temp directory
									if original_temp:
										os.environ["TMPDIR"] = original_temp
										os.environ["TEMP"] = original_temp
									# Clean up MoviePy temp directory
									try:
										for f in moviepy_temp_dir.glob("*"):
											try:
												f.unlink(missing_ok=True)
											except Exception:
												pass
										moviepy_temp_dir.rmdir()
									except Exception:
										pass
							except Exception as fallback_exc:
								self._show_error_main_thread("Segment write failed", f"Part {part_num}: {str(fallback_exc)}")
								continue
						self._set_status_main_thread(f"Saved part {part_num}/{parts}: {output_path.name}")
						elapsed = time.time() - start_time
						avg_part_time = (elapsed / (idx + 1))
						remaining = max(0.0, avg_part_time * (parts - (idx + 1)))
						pct = ((idx + 1) / parts) * 100.0
						self.root.after(0, lambda e=elapsed, r=remaining, p=pct: self._update_time_progress(e, r, p))
		except Exception as exc:  # pragma: no cover
			self._show_error_main_thread("Failed to split video", str(exc))
		finally:
			# Clean up temp files and release UI
			try:
				if mp4_source_is_temp and mp4_source is not None and mp4_source.exists():
					mp4_source.unlink(missing_ok=True)
			except Exception:
				pass
			try:
				if tmp_input is not None and tmp_input.exists():
					tmp_input.unlink(missing_ok=True)
			except Exception:
				pass
			self._set_busy(False)

	def _update_time_progress(self, elapsed: float, remaining: float, pct: float) -> None:
		self.progress_var.set(pct)
		self.time_var.set(f"Elapsed: {int(elapsed)}s   ETA: {int(remaining)}s")

	def _split_with_ffmpeg_segment(self, input_path: Path, output_dir: Path, base: str, ext: str, segment_seconds: int) -> bool:
		pattern = output_dir / f"{base}_part_%03d{ext}"
		cmd = [
			"ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
			"-i", str(input_path),
			"-c", "copy", "-map", "0",
			"-f", "segment", "-segment_time", str(int(segment_seconds)),
			"-reset_timestamps", "1",
			str(pattern),
		]
		try:
			proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			return proc.returncode == 0
		except Exception:
			return False

	def _get_app_directory(self) -> str:
		"""Get the application directory (where script/exe is located)."""
		try:
			if getattr(sys, 'frozen', False):
				# Running as compiled executable
				return str(Path(sys.executable).parent)
			else:
				# Running as script
				return str(Path(__file__).parent)
		except Exception:
			return str(Path.cwd())
	
	def _default_outputs_root(self) -> Path:
		# Try user Videos folder
		home = Path.home()
		candidates = [
			Path(os.environ.get("USERPROFILE", str(home))) / "Videos",
			home / "Videos",
			home / "Documents",
			home
		]
		for c in candidates:
			try:
				if c.exists():
					return c / "ClipForge" / "Outputs"
			except Exception:
				continue
		return home / "ClipForge" / "Outputs"

	def _sanitize_basename(self, name: str) -> str:
		# Remove characters invalid for filenames on Windows and compress spaces
		# Also truncate aggressively to avoid path length issues (Windows 260 char limit)
		if not name:
			return "output"
		safe = re.sub(r"[\\/\:*?\"<>|]", "_", name)
		safe = re.sub(r"\s+", "_", safe).strip()  # Replace spaces with underscores
		# Truncate to 30 chars to leave room for path, part numbers, and temp files
		if len(safe) > 30:
			safe = safe[:30]
		return safe or "output"

	def _ffprobe_duration_seconds(self, path: Path):
		cmd = [
			"ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)
		]
		try:
			out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
			return float(out.decode().strip())
		except Exception:
			return None

	def _segment_with_progress(self, input_path: Path, output_dir: Path, base: str, ext: str, segment_seconds: int, total_seconds: float) -> bool:
		# Ensure output directory exists
		output_dir.mkdir(parents=True, exist_ok=True)
		pattern = output_dir / f"{base}_part_%03d{ext}"
		cmd = [
			"ffmpeg", "-hide_banner", "-nostdin", "-y",
			"-i", str(input_path),
			"-c", "copy", "-map", "0",
			"-f", "segment", "-segment_time", str(int(segment_seconds)),
			"-reset_timestamps", "1",
			"-progress", "pipe:1",
			str(pattern),
		]
		try:
			proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
			start_time = time.time()
			last_out_ms = 0.0
			while True:
				line = proc.stdout.readline()
				if not line:
					break
				line = line.strip()
				if line.startswith("out_time_ms="):
					ms = float(line.split("=", 1)[1])
					last_out_ms = ms
					pct = min(100.0, (ms / (total_seconds * 1000000.0)) * 100.0)
					elapsed = time.time() - start_time
					remaining = max(0.0, (elapsed / max(pct, 1e-6)) * (100.0 - pct))
					self.root.after(0, lambda e=elapsed, r=remaining, p=pct: self._update_time_progress(e, r, p))
				elif line.startswith("progress=") and line.endswith("end"):
					break
			proc.wait()
			return proc.returncode == 0
		except Exception:
			return False

	def _ensure_mp4_with_progress(self, input_path: Path) -> Path:
		"""Return a path to an MP4 version of input_path.
		Tries fast remux first; on failure, re-encodes to H.264/AAC with progress.
		"""
		# If already mp4, return as-is
		if input_path.suffix.lower() == ".mp4":
			return input_path
		# Use temp directory for converted files to avoid path length issues
		tmp_dir = Path(tempfile.gettempdir())
		remux_out = tmp_dir / f"cf_remux_{int(time.time())}.mp4"
		# Try remux (no re-encode)
		remux_cmd = [
			"ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
			"-i", str(input_path),
			"-c", "copy", "-map", "0",
			"-bsf:a", "aac_adtstoasc",
			"-movflags", "+faststart",
			str(remux_out),
		]
		try:
			proc = subprocess.run(remux_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			if proc.returncode == 0 and remux_out.exists():
				return remux_out
		except Exception:
			pass
		# Re-encode with progress
		# Use temp directory for converted files to avoid path length issues
		tmp_dir = Path(tempfile.gettempdir())
		encode_out = tmp_dir / f"cf_encode_{int(time.time())}.mp4"
		total_seconds = self._ffprobe_duration_seconds(input_path) or 0.0
		cmd = [
			"ffmpeg", "-hide_banner", "-nostdin", "-y",
			"-i", str(input_path),
			"-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
			"-c:a", "aac", "-b:a", "192k",
			"-movflags", "+faststart",
			"-progress", "pipe:1",
			str(encode_out),
		]
		try:
			proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
			start_time = time.time()
			while True:
				line = proc.stdout.readline()
				if not line:
					break
				line = line.strip()
				if line.startswith("out_time_ms=") and total_seconds:
					ms = float(line.split("=", 1)[1])
					pct = min(100.0, (ms / (total_seconds * 1000000.0)) * 100.0)
					elapsed = time.time() - start_time
					remaining = max(0.0, (elapsed / max(pct, 1e-6)) * (100.0 - pct))
					self.root.after(0, lambda e=elapsed, r=remaining, p=pct: self._update_time_progress(e, r, p))
				elif line.startswith("progress=") and line.endswith("end"):
					break
			proc.wait()
			if proc.returncode == 0 and encode_out.exists():
				return encode_out
		except Exception:
			pass
		# Fallback: return original
		return input_path

	def _resolve_asset(self, relative: str) -> Path:
		# Works in both dev and PyInstaller-frozen builds
		base = None
		try:
			if getattr(sys, 'frozen', False):
				# Running as executable - check same directory as exe first
				exe_dir = Path(sys.executable).parent
				# Check if file exists in exe directory
				exe_path = exe_dir / relative
				if exe_path.exists():
					return exe_path
				# Fallback to _MEIPASS (extracted temp folder)
				if hasattr(sys, '_MEIPASS'):
					base = Path(sys._MEIPASS)
				else:
					base = exe_dir
			else:
				# Running as script
				base = Path(__file__).parent
		except Exception:
			base = Path.cwd()
		return (base / relative).resolve()

	def _set_busy(self, busy: bool) -> None:
		def apply_state() -> None:
			for child in self.root.winfo_children():
				for sub in child.winfo_children():
					if isinstance(sub, (tk.Button, tk.Entry, tk.Radiobutton)):
						sub.configure(state=("disabled" if busy else "normal"))
		self.root.after(0, apply_state)

	def _set_status_main_thread(self, text: str) -> None:
		self.root.after(0, lambda: self.status_var.set(text))

	def _show_error_main_thread(self, title: str, message: str) -> None:
		self.root.after(0, lambda: messagebox.showerror(title, message))


def main() -> None:
	root = tk.Tk()
	# Use ttk widgets for consistent styling on Windows
	global ttk
	import tkinter.ttk as ttk  # lazy import after Tk init
	VideoTrimmerApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()


