import customtkinter as ctk
from tkcalendar import Calendar
import tkinter as tk
import json
import os
import re
import secrets
from twilio.rest import Client
import unicodedata
from datetime import datetime
import pytest

# Twilio configuration
ACCOUNT_SID = 'AC2a5e1f0b785cbef8d46cd60143678688'
AUTH_TOKEN = '97423e9dcbda897368147000870e79a1'
TWILIO_PHONE = '+5491156090716'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

users_file = 'data/users.json'


def validar_nombre(nombre, error_label):
    nombre_parts = nombre.split()

    # Validación para asegurarse de que el nombre solo contenga letras y espacios
    if not all(re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚ]+$", part) for part in nombre_parts):
        error_label.configure(
            text="El nombre completo solo debe contener letras y espacios.", text_color="red")
        raise ValueError(
            "El nombre completo solo debe contener letras y espacios.")

    # Validación para verificar que haya al menos un nombre y un apellido
    if len(nombre_parts) < 2:
        error_label.configure(
            text="Por favor ingrese un nombre completo (nombre y apellido).", text_color="red")
        raise ValueError(
            "Por favor ingrese un nombre completo (nombre y apellido).")

    # Si todo es válido
    error_label.configure(text="", text_color="black")
    return True


def eliminar_tildes(texto):
    return ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'))


def formatear_nombre(nombre):
    nombre_sin_tildes = eliminar_tildes(nombre)
    return nombre_sin_tildes.title()


def validar_telefono(phone, error_label):
    phone = phone.strip()
    if not re.match(r'^\+54\d{10}$', phone):
        error_label.configure(
            text="Por favor ingrese el número en el formato '+54' seguido de 10 dígitos sin el prefijo '9'.", text_color="red")
        raise ValueError("Número de teléfono inválido")
    if len(phone) != 13:
        error_label.configure(
            text="El número de celular debe tener exactamente 13 dígitos (incluyendo '+54').", text_color="red")
        raise ValueError("El número debe tener exactamente 13 dígitos")
    return True


def cargar_usuarios():
    """Carga los usuarios desde un archivo JSON."""
    if os.path.exists(users_file):
        with open(users_file, 'r') as file:
            return json.load(file)
    else:
        return []


def guardar_usuarios(users):
    """Guarda los usuarios en un archivo JSON."""
    with open(users_file, 'w') as file:
        json.dump(users, file, indent=4)


def formatear_telefono(phone):
    phone = phone.strip()
    if not re.match(r'^\+?[\d\s]+$', phone) or len(phone) < 10:
        raise ValueError(
            "Por favor ingrese un número de celular correspondiente a AMBA.")
    if phone.startswith("11"):
        phone = phone[2:]
    if not phone.startswith("+"):
        phone = "+54" + phone
    if phone.startswith("+54") and len(phone) == 13:
        return phone
    else:
        raise ValueError("Número de celular no válido.")


def enviar_codigo(phone, code):
    """Envía un código de verificación al teléfono proporcionado."""
    formatted_phone = formatear_telefono(phone)
    message = f"Su código de verificación es: {code}"
    try:
        response = client.messages.create(
            body=message, from_=TWILIO_PHONE, to=formatted_phone)
        print(
            f'Código enviado a {formatted_phone}. SID del mensaje: {response.sid}')
    except Exception as e:
        print(f'Error al enviar SMS: {e}')


def generar_enviar_codigo(full_name, phone):
    """Genera un código, lo guarda o actualiza el usuario y lo envía por SMS."""
    code = secrets.token_hex(3)
    users = cargar_usuarios()
    formatted_phone = formatear_telefono(phone)
    existing_user = next(
        (u for u in users if u["phone"] == formatted_phone), None)

    if existing_user:
        enviar_codigo(formatted_phone, code)
    else:
        new_user = {
            "id": len(users) + 1,
            "category": "Patient",
            "name": full_name,
            "phone": formatted_phone,
            "turnos": []
        }
        users.append(new_user)
        guardar_usuarios(users)
        enviar_codigo(formatted_phone, code)

    return code


def show_frame(frame):
    """Muestra el frame especificado en la ventana principal."""
    frame.tkraise()


def login_screen(root, frames):
    """Pantalla de inicio de sesión."""
    root.configure(bg="#f2f2f2")
    login_frame = ctk.CTkFrame(root, corner_radius=10, fg_color="#f2f2f2")
    login_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

    # Header
    header_label = ctk.CTkLabel(login_frame, text="Sistema gestor de turnos", font=(
        "Arial", 24, "bold"), text_color="#333333", fg_color="#f2f2f2")
    header_label.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky='n')

    subheader_label = ctk.CTkLabel(login_frame, text="Bienvenido, ingrese sus datos para avanzar a sacar turno.", font=(
        "Arial", 12), text_color="#666666", fg_color="#f2f2f2")
    subheader_label.grid(row=1, column=0, columnspan=2,
                         padx=10, pady=(0, 20), sticky='n')

    ctk.CTkLabel(login_frame, text="Nombre Completo:", font=("Arial", 14)).grid(
        row=2, column=0, padx=10, pady=10, sticky='e')

    global full_name_entry
    full_name_entry = ctk.CTkEntry(login_frame, width=250)
    full_name_entry.grid(row=2, column=1, padx=10, pady=10)

    ctk.CTkLabel(login_frame, text="Teléfono Celular:", font=("Arial", 14)).grid(
        row=3, column=0, padx=10, pady=10, sticky='e')

    global phone_entry
    phone_entry = ctk.CTkEntry(login_frame, width=250)
    phone_entry.grid(row=3, column=1, padx=10, pady=10)

    global error_label
    error_label = ctk.CTkLabel(
        login_frame, text="", text_color="red", font=("Arial", 12))
    error_label.grid(row=5, column=0, columnspan=2, pady=10)

    def verify_user():
        full_name = full_name_entry.get()
        phone = phone_entry.get()
        turnos = []
        if full_name and phone:
            try:
                validar_nombre(full_name, error_label)
                if not validar_telefono(phone, error_label):
                    return
                full_name = formatear_nombre(full_name)
                generated_code = generar_enviar_codigo(full_name, phone)
                print(f'Código generado: {generated_code}')
                frames["VerifyCodeScreen"] = verify_code_screen(
                    root, frames, phone, generated_code)
                show_frame(frames["VerifyCodeScreen"])
            except ValueError as e:
                print(f"Error: {e}")
        else:
            error_label.configure(
                text="Por favor ingrese nombre y celular.", text_color="red")

    ctk.CTkButton(login_frame, text="Enviar Código", command=verify_user, width=200, height=40, corner_radius=5,
                  fg_color="#3498db", hover_color="#2980b9").grid(row=4, column=0, columnspan=2, pady=20)

    return login_frame


def verify_code_screen(root, frames, phone, generated_code):
    """Pantalla de verificación de código."""
    root.configure(bg="#f2f2f2")
    verify_code_frame = ctk.CTkFrame(
        root, corner_radius=10, fg_color="#f2f2f2")
    verify_code_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    content_frame = ctk.CTkFrame(verify_code_frame, fg_color="#f2f2f2")
    content_frame.pack(expand=True)

    ctk.CTkLabel(content_frame, text="Ingrese el código enviado por SMS:").pack(
        padx=10, pady=10)

    code_entry = ctk.CTkEntry(content_frame)
    code_entry.pack(padx=10, pady=10)

    def check_code():
        entered_code = code_entry.get().strip()  # Eliminar espacios en blanco
        print(f"Código ingresado: {entered_code}")
        print(f"Código generado: {generated_code}")  # Verifica el código aquí

        if entered_code == generated_code:
            print("Código Correcto")
            users = cargar_usuarios()
            user_data = next((u for u in users if u["phone"] == phone), None)
            if user_data:
                if user_data["category"] == "Doctor":
                    show_frame(frames["DoctorScreen"])
                else:
                    show_frame(frames["PatientScreen"])
        else:
            print("Código Incorrecto")

    ctk.CTkButton(content_frame, text="Verificar",
                  command=check_code).pack(padx=10, pady=20)

    return verify_code_frame


def doctor_screen(root, frames):
    """Pantalla de doctor."""
    doctor_frame = ctk.CTkFrame(
        root, corner_radius=10, fg_color="#f5f5f5", border_color="#CCCCCC", border_width=2)
    doctor_frame.grid(row=0, column=0, sticky='nsew')

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Título
    title_label = ctk.CTkLabel(doctor_frame, text="Pantalla del Doctor", font=(
        "Arial", 24, "bold"), text_color="#2c3e50")
    title_label.pack(pady=(20, 10))

    # Agregar calendario
    cal = Calendar(doctor_frame, selectmode='day', year=2024, month=12, day=2)
    cal.pack(pady=20)

    # Caja de mensajes
    mensaje_box = ctk.CTkTextbox(
        doctor_frame, height=10, width=200, border_color="#CCCCCC", border_width=1)
    mensaje_box.pack(pady=10)

    def enviar_mensaje():
        mensaje = mensaje_box.get("1.0", tk.END).strip()
        if mensaje:
            users = cargar_usuarios()
            for user in users:
                enviar_codigo(user['phone'], mensaje)  # Twilio
            print(f"Mensaje enviado a todos los usuarios: {mensaje}")
        else:
            print("El mensaje está vacío.")

    # Botón para enviar mensaje
    ctk.CTkButton(doctor_frame, text="Enviar Mensaje a Usuarios", command=enviar_mensaje,
                  width=200, corner_radius=5, fg_color="#3498db", hover_color="#2980b9").pack(pady=10)

    def mostrar_turnos():
        """Muestra los turnos de los pacientes."""
        users = cargar_usuarios()
        turnos_text = ""
        for user in users:
            if user["category"] == "Patient" and user.get("turnos"):
                turnos_text += f"Paciente: {user['name']}\n"
                for turno in user["turnos"]:
                    turnos_text += f"  - {turno['fecha']}\n"
        if not turnos_text:
            turnos_text = "No hay turnos reservados."

        # mostrar turnos
        turnos_window = ctk.CTkToplevel(root)
        turnos_window.title("Turnos de Pacientes")
        turnos_window.geometry("400x300")

        turnos_label = ctk.CTkLabel(turnos_window, text=turnos_text, justify="left")
        turnos_label.pack(pady=20, padx=20)

    # Botón para mostrar turnos
    ctk.CTkButton(doctor_frame, text="Turnos de Pacientes", command=mostrar_turnos,
                  width=200, corner_radius=5, fg_color="#2ecc71", hover_color="#27ae60").pack(pady=10)

    # Botón para volver al inicio
    ctk.CTkButton(doctor_frame, text="Volver al Inicio", command=lambda: show_frame(
        frames["LoginScreen"]), width=200, corner_radius=5, fg_color="#e74c3c", hover_color="#c0392b").pack(pady=10)

    return doctor_frame

def patient_screen(root, frames):
    """Pantalla de paciente."""
    patient_frame = ctk.CTkFrame(root, corner_radius=10, fg_color="#f5f5f5")
    patient_frame.grid(row=0, column=0, sticky='nsew')

    title_label = ctk.CTkLabel(patient_frame, text="Reservar Turno", font=(
        "Arial", 24, "bold"), text_color="#2c3e50")
    title_label.pack(pady=(20, 10))

    # Agregar calendario
    cal = Calendar(patient_frame, selectmode='day', year=2024, month=12, day=2)
    cal.pack(pady=20)

    def reservar_turno():
        fecha_seleccionada = cal.get_date()
        fecha_seleccionada_dt = datetime.strptime(
            fecha_seleccionada, "%m/%d/%y")
        fecha_actual_dt = datetime.now()

        if fecha_seleccionada_dt < fecha_actual_dt:
            print("La fecha de turno no puede ser anterior a la fecha de hoy.")
            # Dentro de patient_screen:
            error_label = ctk.CTkLabel(
                patient_frame, text="", font=("Arial", 12), text_color="red")
            error_label.pack(pady=5)

            error_label.configure(
                text="La fecha de turno no puede ser anterior a la fecha de hoy.")

            return

        print(f"Turno reservado para: {fecha_seleccionada}")
        phone = phone_entry.get()
        agregar_turno(phone, fecha_seleccionada)

    def agregar_turno(phone, fecha_turno):
        """Agrega un turno reservado a un paciente."""
        users = cargar_usuarios()

        # Buscar al paciente por su número de teléfono
        paciente = next((u for u in users if u["phone"] == phone), None)

        if paciente and paciente["category"] == "Patient":
            # Agregar el nuevo turno a la lista de turnos del paciente
            paciente["turnos"].append({"fecha": fecha_turno})

            # Guardar los cambios en el archivo JSON
            guardar_usuarios(users)

            print(
                f"Turno reservado para {paciente['name']} en la fecha {fecha_turno}.")
        else:
            print("Paciente no encontrado o no es un paciente válido.")

    # Botón para reservar turno
    ctk.CTkButton(patient_frame, text="Reservar Turno", command=reservar_turno, width=200,
                  corner_radius=5, fg_color="#3498db", hover_color="#2980b9").pack(pady=10)

    def ver_turnos_anteriores():
        phone = phone_entry.get()
        users = cargar_usuarios()

        # Buscar al paciente por su número de teléfono
        paciente = next((u for u in users if u["phone"] == phone), None)

        if paciente and paciente["category"] == "Patient":
            turnos = paciente["turnos"]
            for turno in turnos:
                turno_label = ctk.CTkLabel(
                    patient_frame, text=f"Turno: {turno['fecha']}", font=("Arial", 14))
                turno_label.pack(pady=5)
        else:
            error_label = ctk.CTkLabel(patient_frame, text="Paciente no encontrado o no es un paciente válido.", font=(
                "Arial", 14), text_color="red")
            error_label.pack(pady=5)

    # Botón para ver turnos reservados
    ctk.CTkButton(patient_frame, text="Turnos Reservados", command=ver_turnos_anteriores,
                  width=200, corner_radius=5, fg_color="#2ecc71", hover_color="#27ae60").pack(pady=10)

    # Botón para volver al inicio
    ctk.CTkButton(patient_frame, text="Volver al Inicio", command=lambda: show_frame(
        frames["LoginScreen"]), width=200, corner_radius=5, fg_color="#e74c3c", hover_color="#c0392b").pack(pady=10)

    return patient_frame


def main():
    root = ctk.CTk()
    root.title("Consultorio")
    root.geometry("500x600")

    # Configura el grid para que todos los frames ocupen el mismo espacio
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    frames = {}
    frames["LoginScreen"] = login_screen(root, frames)
    frames["VerifyCodeScreen"] = verify_code_screen(root, frames, "", "")
    frames["DoctorScreen"] = doctor_screen(root, frames)
    frames["PatientScreen"] = patient_screen(root, frames)

    show_frame(frames["LoginScreen"])

    root.mainloop()


if __name__ == "__main__":
    main()