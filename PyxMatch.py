import sys
from keyauth import api
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QRect
import hashlib
from datetime import datetime
import os
import shutil
import tkinter as tk
from tkinter import ttk
import cv2
import io
from PIL import Image, ImageTk, ImageSequence
import mss
import platform
import base64
import uuid
import requests
import socket
import subprocess
import threading
import queue
import logging
import webbrowser
from screeninfo import get_monitors
import json

TOKEN = "INSERT_YOUR_BOT_TOKEN"
CHAT_ID = "INSERT_YOUR_CHAT_ID"
STATS_FOLDER = "stats"
LOGS_FOLDER = "logs"
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)

def get_external_ip():
    """Obtenir l'adresse IP externe de la connexion Internet."""
    try:
        response = requests.get('https://httpbin.org/ip')
        return response.json()['origin'].split(',')[0]
    except:
        return "Inconnu"

def get_username():
    """Obtenir le nom d'utilisateur du PC."""
    return os.getlogin()

def send_telegram_message(ip, username):
    """Envoyer un message via Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"{username} a ouvert le logiciel à {timestamp} depuis l'IP externe: {ip}"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    
    response = requests.post(url, data=payload)
    return response.json()

def send_error_message(message):
    """Envoyer un message via Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    
    response = requests.post(url, data=payload)
    return response.json()

def getchecksum():
    md5_hash = hashlib.md5()
    file = open(''.join(sys.argv), "rb")
    md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest

keyauthapp = api(
    name="INSERT_YOUR_APP_NAME",
    ownerid="INSERT_YOUR_OWNER_ID",
    secret="INSERT_YOUR_SECRET",
    version="1.0",
    hash_to_check=getchecksum()
)

class ScreenCaptureApp:
    def __init__(self, root):
        try:
            self.root = root
            root.iconbitmap('cpt.ico')
            self.root.title("PyxMatch")
            self.load_config()
            
            self.output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
            os.makedirs(self.output_folder, exist_ok=True)

            images_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
            num_files = len([f for f in os.listdir(images_folder) if os.path.isfile(os.path.join(images_folder, f))])

            if not os.path.exists(STATS_FOLDER):
                os.makedirs(STATS_FOLDER)

            logs_folder = os.path.join(os.getcwd(), "logs")
            if not os.path.exists(logs_folder):
                os.makedirs(logs_folder)
            self.log_file_path = os.path.join(logs_folder, "match_percentages.txt")

            # Définissez la taille de la fenêtre en fonction du nombre de fichiers
            self.root.geometry(f"380x280")
            self.root.resizable(False, False)
            self.root.configure(bg="#f4f4f4")  # Couleur d'arrière-plan foncée

            # Configuration du style
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TButton", background="#f4f4f4", foreground="#333", padding=(10, 5), relief="solid", font=("Arial", 9))
            style.configure("TLabel", background="#f4f4f4", foreground="#555", font=("Arial", 12))
            style.configure("TCombobox", padding=5, font=("Arial", 10))

            self.files_created = []  # Liste pour stocker les fichiers créés
            self.displaying_image_window = None  # Fenêtre pour afficher les images ou les GIFs
            self.image_index = 0  # Index pour suivre les images à afficher
            self.base_image = None  # Ajoutez cette ligne pour initialiser base_image à None

            shutil.rmtree("temporaire", ignore_errors=True)
            self.output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temporaire")
            os.makedirs(self.output_folder, exist_ok=True)

            self.file_values = {}  # Dictionnaire pour stocker les valeurs

            # Étiquette pour choisir l'écran
            self.screen_label = ttk.Label(self.root, text="Choisissez l'écran:")
            self.screen_label.pack(pady=7)

            # Liste déroulante pour choisir l'écran
            self.screen_combobox = ttk.Combobox(self.root)
            self.screen_combobox.pack(pady=(0))

            self.season_combobox = ttk.Combobox(self.root, values=["saison 2", "saison 3"], state="readonly")
            self.season_combobox.pack(pady=10)  # Positionnement (à ajuster selon votre interface)
            self.season_combobox.current(0)  # Sélection par défaut de "saison 2"

            #self.match_threshold_label = ttk.Label(self.root, text="Pourcentage % (Se référer au tuto ou discord):")
            #self.match_threshold_label.pack(pady=1)

            #self.match_threshold = ttk.Entry(self.root)
            #self.match_threshold.pack(pady=(1))
            #self.match_threshold.insert(0, "15")  # Valeur par défaut de 5%

            # Remplissage de la liste déroulante des écrans
            self.populate_screen_combobox()

            self.media_queue = queue.Queue()
            self.image_paths = self.load_image_paths()

            button_frame = tk.Frame(self.root, background="#f4f4f4")
            button_frame.pack(pady=10)

            self.media_folder_path = os.path.join(os.getcwd(), "media")
            self.open_media_button = ttk.Button(self.root, text="Ouvrir le dossier média", command=self.open_media_folder)
            self.open_media_button.pack()  # Vous pouvez ajouter des options pour positionner le bouton comme vous le souhaitez

            # Bouton pour démarrer la capture
            self.capture_button = ttk.Button(button_frame, text="Start", command=self.capture_specific_screen)
            self.capture_button.grid(row=0, column=0, padx=5)

            # Bouton pour fermer le programme
            #self.close_button = ttk.Button(button_frame, text="Fermer", command=self.close_program)
            #self.close_button.grid(row=0, column=1, padx=5)

            # Étiquette pour afficher le pourcentage de correspondance
            self.match_label = ttk.Label(self.root, text="")
            self.match_label.pack(pady=(5))

            def start_screen_exe():
                subprocess.run(["screen.exe"])

            self.start_screen_button = ttk.Button(button_frame, text="Détection de l'écran", command=start_screen_exe)
            self.start_screen_button.grid(row=0, column=1, padx=5)

            self.verification_interval = 500
            self.displaying_image = False  
            self.pause_verification = False  
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\n Erreur lors de l'initialisation de ScreenCaptureApp: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def load_config(self):
        try:
            with open("config.json", "r") as config_file:
                config_data = json.load(config_file)
                self.user_threshold = float(config_data.get("user_threshold_percentage", 15.0))
        except FileNotFoundError:
            # Fichier de configuration manquant, utilisez une valeur par défaut
            self.user_threshold = 15.0
        except json.JSONDecodeError:
            # Erreur lors de la lecture du fichier JSON, utilisez une valeur par défaut
            self.user_threshold = 15.0

    def open_media_folder(self):
        try:
            # Si vous êtes sur Windows, cela ouvrira l'explorateur de fichiers. Sinon, cela ouvrira le gestionnaire de fichiers par défaut.
            webbrowser.open(os.path.realpath(self.media_folder_path))
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de l'ouverture du dossier média: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)
            

    def update_media_count(self, media_name): # Liste des fichiers et menu déroulant
        try:
            # Obtenez le nom du fichier basé sur la date actuelle
            today = datetime.today().strftime('%Y-%m-%d')
            file_path = os.path.join(STATS_FOLDER, f"{today}.txt")

            # Vérifiez si le fichier existe
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    media_dict = {line.split(":")[0].strip(): int(line.split(":")[1].strip()) for line in lines}
            else:
                media_dict = {}

            # Mettez à jour le compteur pour le média spécifique
            if media_name in media_dict:
                media_dict[media_name] += 1
            else:
                media_dict[media_name] = 1

            # Écrivez les mises à jour dans le fichier
            with open(file_path, 'w') as file:
                for key, value in media_dict.items():
                    file.write(f"{key}: {value}\n")
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de l'update media count: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def load_image_paths(self):
        try:
            selected_season = self.season_combobox.get()
            images_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), selected_season)
            all_files = sorted([f for f in os.listdir(images_folder) if os.path.isfile(os.path.join(images_folder, f)) and not f.lower().endswith('.gif')])
            image_paths = [os.path.join(images_folder, filename) for filename in all_files]
            return image_paths
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de l'ouverture du chargement des media path: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def populate_screen_combobox(self):
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                screen_names = [f"Ecran {i}" for i in range(1, len(monitors))]
                self.screen_combobox["values"] = screen_names
                self.screen_combobox.current(0)
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de la création de la fenêtre combobox: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def capture_specific_screen(self):
        try:
            selected_screen_index = self.screen_combobox.current()
            selected_screen_index += 1
            with mss.mss() as sct:
                monitors = sct.monitors
                if 0 <= selected_screen_index < len(monitors):
                    screenshot_path = os.path.join(self.output_folder, f"screenshot_{selected_screen_index}.png")
                    screenshot = sct.shot(mon=selected_screen_index, output=screenshot_path)
                    self.files_created.append(screenshot_path)
                    
                    # Si self.base_image est None, chargez l'image base.png comme image de base
                    if self.base_image is None:
                        base_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "base.png")
                        if os.path.exists(base_image_path):
                            self.base_image = cv2.imread(base_image_path)
                    
                    self.root.withdraw()
                    self.show_close_button_window()
                    self.schedule_next_capture(selected_screen_index)
                else:
                    print("Screen not found.")
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de la capture: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def schedule_next_capture(self, selected_screen_index):
        try:
            self.root.after(self.verification_interval, self.capture_screen, selected_screen_index)
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de next capture: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def capture_screen(self, selected_screen_index):
        try:
            # Capture d'écran immédiatement avant la vérification
            with mss.mss() as sct:
                screenshot_path = os.path.join(self.output_folder, f"screenshot_{selected_screen_index}.png")
                sct.shot(mon=selected_screen_index, output=screenshot_path)
                self.files_created.append(screenshot_path)

            # Vérification
            new_image = cv2.imread(screenshot_path)

            max_match_percentage = 0

            for image_path in self.load_image_paths():
                base_image = cv2.imread(image_path)
                match_percentage = self.calculate_image_match_percentage(base_image, new_image)

                if match_percentage > max_match_percentage:
                    max_match_percentage = match_percentage

            #self.match_label.config(text=f"Correspondance : {max_match_percentage:.2f}%")
            selected_season = self.season_combobox.get()

            if max_match_percentage > self.user_threshold and self.media_queue.empty():
                media_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
                with open(os.path.join("logs", "match_percentages.txt"), "a") as file:
                    file.write(f"{selected_season} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - : {max_match_percentage:.2f}%\n")
                for media_file in os.listdir(media_folder_path):
                    self.media_queue.put(os.path.join(media_folder_path, media_file))
                self.display_next_media(selected_screen_index)
            else:
                self.schedule_next_capture(selected_screen_index)
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de la capture d'écran: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def display_next_media(self, screen_index):
        try:
            if not self.media_queue.empty():
                next_media_path = self.media_queue.get()
                media_name = os.path.basename(next_media_path)  # Obtenez le nom du fichier à partir du chemin
                self.update_media_count(media_name)  # Mettez à jour le compteur pour ce média
                self.display_image_window(screen_index, next_media_path)
            else:
                self.close_displaying_image_window()
                self.schedule_next_capture(screen_index)
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de l'affichage du média suivant: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def calculate_image_match_percentage(self, image1, image2):
        try:
            # Redimensionner les images pour qu'elles aient la même taille
            if image1.shape != image2.shape:
                image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

            difference = cv2.absdiff(image1, image2)
            non_zero_pixels = cv2.countNonZero(cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY))
            total_pixels = image1.shape[0] * image1.shape[1]
            match_percentage = ((total_pixels - non_zero_pixels) / total_pixels) * 100
            return match_percentage
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors du calcul des pourcentages: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def display_image_window(self, screen_index, image_path):
        try:
            screen = self.get_screen_info(screen_index)
            if screen:
                screen_x, screen_y, screen_width, screen_height = screen["left"], screen["top"], screen["width"], screen["height"]

                if self.displaying_image_window is None:
                    self.displaying_image_window = tk.Toplevel(self.root)
                    self.displaying_image_window.title("Media Affichée")
                    self.displaying_image_window.geometry(f"{screen_width}x{screen_height}+{screen_x}+{screen_y}")
                    self.displaying_image_window.overrideredirect(True)
                    self.displaying_image_window.lift()  # Place la fenêtre au-dessus des autres
                    self.displaying_image_window.focus_force()

                    image_label = tk.Label(self.displaying_image_window)
                    image_label.pack(fill=tk.BOTH, expand=tk.YES)
                else:
                    image_label = self.displaying_image_window.winfo_children()[0]  # Récupère le premier enfant (le label)

                # Assurez-vous que la fenêtre est toujours au premier plan
                self.displaying_image_window.attributes('-topmost', True)
                self.displaying_image_window.after(500, lambda: self.displaying_image_window.attributes('-topmost', True))

                # Vérifiez si le média est une vidéo ou une image
                if image_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv')):
                    self.display_video_frames(image_label, image_path, screen_width, screen_height, screen_index)
                else:
                    # C'est une image
                    image = Image.open(image_path)
                    image = image.resize((screen_width, screen_height))
                    photo = ImageTk.PhotoImage(image=image)
                    image_label.config(image=photo)
                    image_label.image = photo
                    self.displaying_image_window.after(7000, self.display_next_media, screen_index)  # Affiche le prochain média après 7 secondes
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de la création de la fenêtre d'affichage des média: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def display_video_frames(self, label, video_path, screen_width, screen_height, screen_index):
        try:
            cap = cv2.VideoCapture(video_path)
            delay = 11  # Pour un affichage à environ 60 FPS
            skip_frames = 1  # Nombre de frames à sauter. 1 signifie aucune frame sautée.

            def update_frame():
                for _ in range(skip_frames):
                    cap.read()  # Lisez et ignorez les frames

                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame)
                    image = image.resize((screen_width, screen_height))
                    photo = ImageTk.PhotoImage(image=image)
                    label.config(image=photo)
                    label.image = photo
                    self.displaying_image_window.after(delay, update_frame)
                else:
                    cap.release()
                    self.display_next_media(screen_index)
            update_frame()
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de l'affichage de la vidéo: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

# Ajoutez cette méthode pour fermer la fenêtre d'affichage d'image
    def close_displaying_image_window(self):
        try:
            if self.displaying_image_window is not None:
                self.displaying_image_window.destroy()
                self.displaying_image_window = None
            self.displaying_image = False
            self.pause_verification = False
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de closing displaying image window: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def get_screen_info(self, screen_index):
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                if 0 <= screen_index < len(monitors):
                    return monitors[screen_index]
                return None
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de get screen info: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def show_close_button_window(self):
        try:
            self.close_window = tk.Toplevel(self.root)
            self.close_window.iconbitmap('cpt.ico')
            self.close_window.title("PyxMatch")
            self.close_window.geometry("300x150")
            
            self.root.resizable(False, False)
            
            close_label = ttk.Label(self.close_window, text="Options :")
            close_label.pack(pady=10)
            
            close_button = ttk.Button(self.close_window, text="Fermer", command=self.close_program)
            close_button.pack(pady=10)

            restart_button = ttk.Button(self.close_window, text="Restart", command=self.restart_program)
            restart_button.pack(pady=10)
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de show close button window: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def close_program(self):
        try:
            for file_path in self.files_created:
                if os.path.exists(file_path):
                    os.remove(file_path)
            if os.path.exists(self.output_folder):
                shutil.rmtree(self.output_folder)
            self.close_window.destroy()  # Fermer la fenêtre `close_window`
            self.root.quit()
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors de la fermeture du programme: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

    def restart_program(self):
        try:
            if self.close_window:
                self.close_window.destroy()  # Fermer la fenêtre `close_window`

            # Fermer proprement l'instance actuelle de ScreenCaptureApp
            self.root.quit()
            self.root.destroy()

            # Créer une nouvelle instance de ScreenCaptureApp
            root = tk.Tk()
            app = ScreenCaptureApp(root)
            root.mainloop()
        except Exception as e:
            username = get_username()
            ip = get_external_ip()
            error_message = f"{username} avec l'IP {ip}.\nErreur lors du redémarrage du programme: " + str(e)
            logging.error(error_message)
            send_error_message(error_message)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('cpt.ico'))
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Nom d'utilisateur")
        layout.addWidget(self.user_input)

        self.pass_input = QLineEdit(self)
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Mot de passe")
        layout.addWidget(self.pass_input)

        btn_login = QPushButton('Connexion', self)
        btn_login.clicked.connect(self.login)
        layout.addWidget(btn_login)

        self.setLayout(layout)
        self.setWindowTitle('PyxMatch')
        self.resize(250, 100)
        self.show()

    def showError(self):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("Erreur")
        error_dialog.setWindowTitle("Erreur")
        error_dialog.exec_()
        sys.exit()

    def run_v1_and_close(self):
        # Au lieu de lancer un autre script, nous allons lancer la ScreenCaptureApp
        self.close()  # Ferme la fenêtre de connexion
        root = tk.Tk()
        app = ScreenCaptureApp(root)
        ip = get_external_ip()
        username = get_username()
        send_telegram_message(ip, username)
        root.mainloop()

    def login(self):
        user = self.user_input.text()
        password = self.pass_input.text()
        response = keyauthapp.login(user, password)
        if keyauthapp.login(user, password) == None:
            self.run_v1_and_close()

    def register(self):
        user = self.user_input.text()
        password = self.pass_input.text()
        license = self.license_input.text()
        response = keyauthapp.register(user, password, license)
        if response == None:
            self.run_v1_and_close()

    def upgrade(self):
        user = self.user_input.text()
        license = self.license_input.text()
        response = keyauthapp.upgrade(user, license)
        if response == None:
            self.run_v1_and_close()

    def license_key(self):
        key = self.license_input.text()
        response = keyauthapp.license(key)
        if response == None:
            self.run_v1_and_close()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        ex = App()
        sys.exit(app.exec_())
    except Exception as e:
        username = get_username()
        ip = get_external_ip()
        error_message = f"{username} avec l'IP {ip}.\nErreur lors de l'ouverture du logiciel: " + str(e)
        logging.error(error_message)
        send_error_message(error_message)