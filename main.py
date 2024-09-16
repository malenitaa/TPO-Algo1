import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import secrets
import json
import os
from twilio.rest import Client
import re, unicodedata
#ver que capaz se repiten validaciones de celular con las funciones validar y sendcode
#customtkinter
#modularizar 
#pep.8 pipinstallpep8
#niceui

# Twilio
ACCOUNT_SID = 'AC2a5e1f0b785cbef8d46cd60143678688'
AUTH_TOKEN = '97423e9dcbda897368147000870e79a1'
TWILIO_PHONE = '+5491156090716'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

users_file = 'data/users.json'

def validar_nombre(nombre, error_label):
    nombre_parts = nombre.split()
    if len(nombre_parts) < 2:
        error_label.config(text="Por favor ingrese un nombre completo (nombre y apellido).", foreground="red")
        raise ValueError("Por favor ingrese un nombre completo (nombre y apellido).")
    if not all(re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚ]+$", part) for part in nombre_parts):
        error_label.config(text="El nombre completo solo debe contener letras y espacios.", foreground="red")
        raise ValueError("El nombre completo solo debe contener letras y espacios.")
    else:
        error_label.config(text="", foreground="black")

def eliminar_tildes(texto):
    return ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'))

def formatear_nombre(nombre):
    nombre_sin_tildes = eliminar_tildes(nombre)
    return nombre_sin_tildes.title()

def validate_phone(phone, error_label):
    if not phone.isdigit():
        error_label.config(text="El número de celular debe ser numérico.", foreground="red")
        return False
    if len(phone) < 10:
        error_label.config(text="El número de celular debe tener al menos 10 dígitos.", foreground="red")
        return False
    return True

def verify_user():
    full_name = full_name_entry.get()
    phone = phone_entry.get()

    if full_name and phone:
        try:
            validar_nombre(full_name, error_label)
            if not validate_phone(phone, error_label):
                return 

            full_name = formatear_nombre(full_name)
            
            users = load_users()
            if any(u["phone"] == phone for u in users):
                error_label.config(text="Ya existe un usuario con este número de celular.", foreground="red")
                return

            generated_code = generate_and_send_code(full_name, phone)
            print(f'Código generado: {generated_code}')
            verify_code_screen(root, frames, phone, generated_code)

        except ValueError as e:
            print(f"Error: {e}")
    else:
        error_label.config(text="Por favor ingrese nombre y celular.", foreground="red")


def load_users():
    """Carga los usuarios desde un archivo JSON."""
    if os.path.exists(users_file):
        with open(users_file, 'r') as file:
            return json.load(file)
    else:
        return []

def save_users(users):
    """Guarda los usuarios en un archivo JSON."""
    with open(users_file, 'w') as file:
        json.dump(users, file, indent=4)

def format_phone(phone):
    phone = phone.strip() 
    if not re.match(r'^\+?[\d\s]+$', phone) or len(phone) < 10:
        raise ValueError("Por favor ingrese un número de celular correspondiente a AMBA.")
    
    if phone.startswith("11"):
        phone = phone[2:]  # chau "11" si está al principio
    
    if not phone.startswith("+"):
        phone = "+549" + phone  
    
    return phone

def send_code(phone, code):
    """Envía un código de verificación al teléfono proporcionado."""
    formatted_phone = format_phone(phone)
    message = f"Su código de verificación es: {code}"
    try:
        response = client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=formatted_phone
        )
        print(f'Código enviado a {formatted_phone}. SID del mensaje: {response.sid}')
    except Exception as e:
        print(f'Error al enviar SMS: {e}')

def generate_and_send_code(full_name, phone):
    """Genera un código, lo guarda o actualiza el usuario y lo envía por SMS."""
    code = secrets.token_hex(3)  
    users = load_users()

    if not validate_phone(phone, None): 
        return None
    
    existing_user = next((u for u in users if u["phone"] == phone), None)

    if existing_user:
        send_code(phone, code)
    else:
        new_user = {
            "id": len(users) + 1,
            "category": "Patient",
            "name": full_name,
            "phone": phone
            #agregar turnos con historial
            #,
            #"appointments": 
        }
        users.append(new_user)
        save_users(users)
        send_code(phone, code)

    return code


def show_frame(frame):
    """Muestra el frame especificado en la ventana principal."""
    frame.tkraise()

def login_screen(root, frames):
    """Pantalla de inicio de sesión."""
    login_frame = ttk.Frame(root)
    login_frame.grid(row=0, column=0, sticky='nsew')

    # Header
    header_label = ttk.Label(login_frame, text="Sistema gestor de turnos", font=("Arial", 20))
    header_label.grid(row=0, column=0, columnspan=2, pady=10)

    subheader_label = ttk.Label(login_frame, text="Bienvenido, ingrese sus datos para avanzar a sacar turno.", font=("Arial", 10))
    subheader_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    ttk.Label(login_frame, text="Nombre Completo:").grid(row=2, column=0, padx=10, pady=10)
    global full_name_entry
    full_name_entry = ttk.Entry(login_frame)
    full_name_entry.grid(row=2, column=1, padx=10, pady=10)

    ttk.Label(login_frame, text="Teléfono Celular:").grid(row=3, column=0, padx=10, pady=10)
    global phone_entry
    phone_entry = ttk.Entry(login_frame)
    phone_entry.grid(row=3, column=1, padx=10, pady=10)
    
    global error_label
    error_label = ttk.Label(login_frame, text="", foreground="red")
    error_label.grid(row=5, column=0, columnspan=2, pady=10)
    
    def verify_user():
        full_name = full_name_entry.get()
        phone = phone_entry.get()
        if full_name and phone:
            try:
                validar_nombre(full_name, error_label)
                validate_phone(phone, error_label)
                full_name = formatear_nombre(full_name)
                generated_code = generate_and_send_code(full_name, phone)
                print(f'Código generado: {generated_code}')
                verify_code_screen(root, frames, phone, generated_code)
            except ValueError as e:
                print(f"Error: {e}")
        else:
            error_label.config(text="Por favor ingrese nombre y celular.", foreground="red")

    ttk.Button(login_frame, text="Enviar Código", command=verify_user).grid(row=4, column=0, columnspan=2, pady=20)
    
    return login_frame

def verify_code_screen(root, frames, phone, generated_code):
    """Pantalla de verificación de código."""
    verify_code_frame = ttk.Frame(root)
    verify_code_frame.grid(row=0, column=0, sticky='nsew')

    ttk.Label(verify_code_frame, text="Código:").grid(row=0, column=0, padx=10, pady=10)
    code_entry = ttk.Entry(verify_code_frame)
    code_entry.grid(row=0, column=1, padx=10, pady=10)
    
    def check_code():
        entered_code = code_entry.get()
        if entered_code == generated_code:
            print("Código Correcto")
            users = load_users()
            user_data = next((u for u in users if u["phone"] == phone), None)
            if user_data:
                if user_data["category"] == "Doctor":
                    show_frame(frames["DoctorScreen"])
                else:
                    show_frame(frames["PatientScreen"])
        else:
            print("Código Incorrecto")

    ttk.Button(verify_code_frame, text="Verificar", command=check_code).grid(row=1, column=0, columnspan=2, pady=20)
    ttk.Button(verify_code_frame, text="Volver al Inicio", command=lambda: show_frame(frames["LoginScreen"])).grid(row=2, column=0, columnspan=2, pady=10)

    return verify_code_frame

def doctor_screen(root, frames):
    """Pantalla de doctor."""
    doctor_frame = ttk.Frame(root)
    doctor_frame.grid(row=0, column=0, sticky='nsew')
    #agregar horario y turnos marcados, grisar los dias pasados
    cal = Calendar(doctor_frame, selectmode='day', year=2024, month=9, day=7)
    cal.pack(pady=20)

    mensaje_box = tk.Text(doctor_frame, height=5, width=40)
    mensaje_box.pack(pady=10)

    def enviar_mensaje():
        mensaje = mensaje_box.get("1.0", tk.END).strip()
        if mensaje:
            users = load_users()
            for user in users:
                send_code(user['phone'], mensaje)  # Twilio
            print(f"Mensaje enviado a todos los usuarios: {mensaje}")
        else:
            print("El mensaje está vacío.")

    ttk.Button(doctor_frame, text="Enviar Mensaje a Usuarios", command=enviar_mensaje).pack(pady=10)
    ttk.Button(doctor_frame, text="Volver al Inicio", command=lambda: show_frame(frames["LoginScreen"])).pack(pady=10)

    return doctor_frame

def patient_screen(root, frames):
    """Pantalla de paciente."""
    patient_frame = ttk.Frame(root)
    patient_frame.grid(row=0, column=0, sticky='nsew')
    #agregar horario y turnos marcados, grisar los dias pasados
    cal = Calendar(patient_frame, selectmode='day', year=2024, month=9, day=7)
    cal.pack(pady=20)

    def reservar_turno():
        fecha_seleccionada = cal.get_date()
        print(f"Turno reservado para: {fecha_seleccionada}")

    ttk.Button(patient_frame, text="Reservar Turno", command=reservar_turno).pack(pady=10)

    def ver_turnos_anteriores():
        print("Mostrando turnos anteriores")

    ttk.Button(patient_frame, text="Turnos Anteriores", command=ver_turnos_anteriores).pack(pady=10)
    ttk.Button(patient_frame, text="Volver al Inicio", command=lambda: show_frame(frames["LoginScreen"])).pack(pady=10)
    #agregar cerrar sesion o algo para salir

    return patient_frame

def main():
    root = tk.Tk()
    root.title("Consultorio")

    frames = {}
    frames["LoginScreen"] = login_screen(root, frames)
    frames["VerifyCodeScreen"] = verify_code_screen(root, frames, "", "")
    frames["DoctorScreen"] = doctor_screen(root, frames)
    frames["PatientScreen"] = patient_screen(root, frames)

    show_frame(frames["LoginScreen"])

    root.mainloop()

if __name__ == "__main__":
    main()
